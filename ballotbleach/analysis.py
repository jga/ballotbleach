from collections import defaultdict, OrderedDict
from logging import getLogger
import os
import re
from statistics import mean, median_low
from matplotlib import pyplot as plt
from matplotlib import ticker
from scipy.misc import imread
from textwrap import wrap
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


logger = getLogger(__name__)


def nearest_step(x, base=5):
    return int(base * round(float(x)/base))


def build_summary_data_text(summary_data):
    """
    Prepares a text string based on available summary data.
    """
    text = ''
    if 'n' in summary_data:
        text = ''.join((text, 'Votes: {0}  '.format(summary_data['n']),))
    if 'average' in summary_data:
        text = ''.join((text, 'Average: {0}  '.format(summary_data['average']),))
    if 'median' in summary_data:
        text = ''.join((text, 'Median: {0}'.format(summary_data['median']),))
    return text


def create_category_bar_chart(image_save_path, categories, values,
                              summary_data=None, title_text=None, tick_format=None):
    """
    Generates bar chart images.
    """
    figure, axes1 = plt.subplots(figsize=(5, 5), tight_layout=True)
    figure.subplots_adjust(left=0.2, right=0.85)
    y_coordinates = list()
    for category_index in range(0, len(values), 1):
        y_coordinates.insert(0, (category_index + 0.5))
    rectangles = axes1.barh(y_coordinates, values, align='center', color='#609cee', edgecolor='#FFFFFF')
    values_index = 0
    for rectangle in rectangles:
        width = int(rectangle.get_width())
        if (width < 20):
            text_x_location = width + 1
            font_color = 'black'
            font_align = 'left'
        else:
            text_x_location = 0.95 * width
            font_color = 'white'
            font_align = 'right'
        text_y_location = (rectangle.get_height() / 2.0) + rectangle.get_y()
        text_content = tick_format % values[values_index]
        axes1.text(text_x_location, text_y_location, text_content, horizontalalignment=font_align,
            verticalalignment='center', color=font_color, weight='normal')
        values_index += 1
    axes1.set_xlim([0, 100])
    labels = axes1.get_xmajorticklabels()
    for label in labels:
        label.set_color('#47474B')
    if title_text:
        wrapped_title = '\n'.join(wrap(title_text, 35))
        title = axes1.set_title(wrapped_title)
        title.set_y(1.05)
    if tick_format:
        x_ticks_formatter = ticker.FormatStrFormatter(tick_format)
        axes1.xaxis.set_major_formatter(x_ticks_formatter)
    axes1.set_ylim([0, (len(y_coordinates))])
    axes1.set_yticks(y_coordinates)
    axes1.set_yticklabels(categories, color='#47474B')
    axes1.yaxis.set_tick_params(color='#27292C', length=2, width=2)
    if summary_data:
        summary_text = build_summary_data_text(summary_data)
        figure.text(0.5, 0.01, summary_text, horizontalalignment='center', fontsize=8)
    logger.info('...saving bar chart at {0}'.format(image_save_path))
    figure.savefig(image_save_path)
    plt.close()


def create_rating_histogram(ballots, rating_range, chart_title, image_save_path):
    """
    Generates a histogram (bar chart) image from ballot data for the subject rating.
    """
    all_values = list()
    rating_histogram = {'0': 0}
    for value in rating_range:
        rating_histogram[str(value)] = 0
    for ballot in ballots:
        if ballot.subject_rating and str(ballot.subject_rating) in rating_histogram:
            rating_histogram[str(ballot.subject_rating)] += 1
            all_values.append(ballot.subject_rating)
        else:
            rating_histogram['0'] += 1
            all_values.append(0)
    total_submissions = 0
    for rating in rating_histogram:
        total_submissions += rating_histogram[rating]
    sorted_ratings = OrderedDict(sorted(rating_histogram.items(),
                                        key=lambda rating_data: int(rating_data[0])))
    categories = list()
    values = list()
    for rating in sorted_ratings:
        categories.append(rating)
        values.append(round(sorted_ratings[rating] / total_submissions * 100))
    chart_tick_format = '%d%%'
    categories_with_none = [x if x != '0' else "None" for x in categories]
    summary_data = {
        'n': total_submissions,
        'average': round(mean(all_values), 1),
        'median': median_low(all_values)
    }
    create_category_bar_chart(image_save_path, categories_with_none, values, summary_data,
                              chart_title, chart_tick_format)


def create_rating_by_selected_actor(ballots, rating_range, chart_directory, subject_rating_title):
    """
    Create images of the subject rating for ballots that selected an actor.
    """
    ballots_by_actor = defaultdict(list)
    for ballot in ballots:
        ballots_by_actor[ballot.selected_actor].append(ballot)
    for actor in ballots_by_actor:
        chart_title = "{0} by {1} votes".format(subject_rating_title, actor)
        simplified_actor_name = re.sub(r'[^a-zA-Z0-9]+', '', actor)
        image_name = ''.join((simplified_actor_name.lower(), '-ratings.png',))
        image_save_path = os.path.join(chart_directory, image_name)
        create_rating_histogram(ballots_by_actor[actor], rating_range, chart_title, image_save_path)


def create_actor_ranking(ballots, title, tick_format, save_path):
    """
    Creates bar chart visualization that ranks the selected actors from most
    selected to least.
    """
    actor_ranking = defaultdict(int)
    for ballot in ballots:
        actor_ranking[ballot.selected_actor] += 1
    total_ranking_submissions = 0
    for actor in actor_ranking:
        total_ranking_submissions += actor_ranking[actor]
    sorted_ranking = OrderedDict(sorted(actor_ranking.items()))
    categories = list()
    values = list()
    for actor in sorted_ranking:
        categories.append(actor)
        values.append(round(sorted_ranking[actor]/total_ranking_submissions * 100))
    summary_data = {
        'n': total_ranking_submissions,
    }
    create_category_bar_chart(save_path, categories, values, summary_data,
                              title, tick_format)


def create_word_cloud(ballots, chart_directory, image_name, mask_file,
                      stop_words, word_counts=None):
    """
    Generates a word cloud from given ballots.
    """
    if word_counts is None:
        word_counts=[25, 50, 100, 1000]
    text = ''
    for ballot in ballots:
        text = ''.join((text, ballot.feedback,))
    all_stop_words = STOPWORDS
    all_stop_words |= set(stop_words)
    for word_count in word_counts:
        if mask_file:
            color_mask = imread(mask_file)
            image_colors = ImageColorGenerator(color_mask)
            wc = WordCloud(background_color="white", max_words=word_count,
                           mask=color_mask,
                           stopwords=all_stop_words,
                           color_func=image_colors,
                           max_font_size=80, random_state=42)
        else:
            wc = WordCloud(background_color="white", max_words=word_count,
                           stopwords=all_stop_words,
                           max_font_size=80, random_state=42)
        wc.generate(text)
        axis_image = plt.imshow(wc)
        plt.axis("off")
        image_name_with_count = '{0}-{1}.png'.format(image_name, str(word_count))
        logger.info('...creating word cloud {0}'.format(image_name_with_count))
        save_location = os.path.join(chart_directory, image_name_with_count)
        plt.savefig(save_location)
        plt.close()


def create_word_cloud_by_selected_actor(ballots, chart_directory, mask_file, stop_words):
    """
    Generates word cloud for each selected actor.
    """
    ballots_by_actor = defaultdict(list)
    word_counts = [25]
    for ballot in ballots:
        ballots_by_actor[ballot.selected_actor].append(ballot)
    for actor in ballots_by_actor:
        simplified_actor_name = re.sub(r'[^a-zA-Z0-9]+', '', actor)
        image_name = ''.join((simplified_actor_name.lower(), '-wordcloud',))
        create_word_cloud(ballots_by_actor[actor], chart_directory, image_name,
                          mask_file, stop_words, word_counts)


def save_charts(chart_directory, chart_options, clean_ballots):
    """
    Handles the creation of analysis charts.
    """
    logger.info("Building charts...")
    # actor ranking image
    actor_ranking_image_file = ''.join((chart_options['actor_ranking_image_name'], '.png',))
    actor_ranking_image_path = os.path.join(chart_directory, actor_ranking_image_file)
    create_actor_ranking(clean_ballots,
                         chart_options['actor_ranking_title'],
                         chart_options['actor_ranking_tick_format'],
                         actor_ranking_image_path)
    # rating histogram
    rating_histogram_image_file = ''.join((chart_options['subject_rating_image_name'], '.png',))
    rating_histogram_image_path = os.path.join(chart_directory, rating_histogram_image_file)
    create_rating_histogram(clean_ballots, chart_options['subject_rating_range'],
                            chart_options['subject_rating_title'],
                            rating_histogram_image_path)
    # rating histograms for each actor's votes
    create_rating_by_selected_actor(clean_ballots, chart_options['subject_rating_range'],
                                    chart_directory, chart_options['subject_rating_title'])
    # main word cloud
    create_word_cloud(clean_ballots, chart_directory, 'feedback-wordcloud',
                      chart_options['mask_file'], chart_options['stop_words'])
    # word cloud for each actor's votes
    create_word_cloud_by_selected_actor(clean_ballots, chart_directory,
                                        chart_options['mask_file'], chart_options['stop_words'])
    logger.info("...chart-building completed.")
