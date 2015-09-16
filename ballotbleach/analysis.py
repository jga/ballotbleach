from collections import defaultdict, OrderedDict
from matplotlib import pyplot as plt
from matplotlib import ticker
from scipy.misc import imread
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


def nearest_step(x, base=5):
    return int(base * round(float(x)/base))


def create_category_bar_chart(image_save_path, categories, values, title=None, tick_format=None):
    figure, axes1 = plt.subplots(figsize=(5, 5), tight_layout=True)
    figure.subplots_adjust(left=0.2, right=0.85)
    y_coordinates = list()
    for category_index in range(0, len(values), 1):
        y_coordinates.insert(0, (category_index + 0.5))
    rectangles = axes1.barh(y_coordinates, values, align='center', color='#609cee', edgecolor='#FFFFFF')
    axes1.set_xlim([0, 100])

    if title:
        axes1.set_title(title)
    if tick_format:
        x_ticks_formatter = ticker.FormatStrFormatter(tick_format)
        axes1.xaxis.set_major_formatter(x_ticks_formatter)

    axes1.set_ylim([0, (len(y_coordinates))])
    axes1.set_yticks(y_coordinates)
    axes1.set_yticklabels(categories)
    figure.savefig(image_save_path)
    plt.close()


def calculate_performance_histogram(ballots, chart_title, save_location):
    performance_histogram = defaultdict(int)
    for ballot in ballots:
        if ballot.council_rating:
            performance_histogram[str(ballot.council_rating)] += 1
        else:
            performance_histogram['0'] += 1
    total_submissions = 0
    for rating in performance_histogram:
        total_submissions += performance_histogram[rating]
    sorted_performance = OrderedDict(sorted(performance_histogram.items()))
    categories = list()
    values = list()
    for rank in sorted_performance:
        clean_rank = rank.replace('.0', '')
        categories.append(clean_rank)
        values.append(round(sorted_performance[rank]/total_submissions * 100))
    chart_tick_format = '%d%%'
    categories.sort(key=int)
    categories_with_none = [x if x != '0' else "None" for x in categories]
    create_category_bar_chart(save_location, categories_with_none, values, chart_title, chart_tick_format)


def to_performance_histograms(ballots):
    member_ballots = defaultdict(list)
    for ballot in ballots:
        member_ballots[ballot.most_effective].append(ballot)


def get_effectiveness_ranking(ballots):
    member_effectiveness = defaultdict(int)
    for ballot in ballots:
        member_effectiveness[ballot.most_effective] += 1
    total_effectiveness_submissions = 0
    for member in member_effectiveness:
        total_effectiveness_submissions += member_effectiveness[member]
    sorted_effectiveness = OrderedDict(sorted(member_effectiveness.items()))
    categories = list()
    values = list()
    for member in sorted_effectiveness:
        categories.append(member)
        values.append(round(sorted_effectiveness[member]/total_effectiveness_submissions * 100))
    chart_title = 'Most Effective Member'
    chart_tick_format = '%d%%'
    save_path = '/Users/jga/member-effectiveness.png'
    create_category_bar_chart(save_path, categories, values, chart_title, chart_tick_format)


def create_word_cloud(ballots):
    text = ''
    for ballot in ballots:
        text = ''.join((text, ballot.next_priorities,))
    city_mask = imread("/Users/jga/ATXcouncil.jpg")
    image_colors = ImageColorGenerator(city_mask)
    word_counts = [25, 50, 100, 200, 3000]
    all_stop_words = STOPWORDS
    new_stop_words = ['city', 'austin']
    all_stop_words |= set(new_stop_words)
    for word_count in word_counts:
        print('On word cloud ' + str(word_count))
        wc = WordCloud(background_color="white", max_words=word_count,
                       mask=city_mask,
                       stopwords=all_stop_words,
                       color_func=image_colors,
                       max_font_size=80, random_state=42)
        wc.generate(text)
        axis_image = plt.imshow(wc)
        plt.axis("off")
        save_name = '/Users/jga/{0}_{1}.png'.format('priorities_wordcloud', str(word_count))
        plt.savefig(save_name)
        plt.close()


def create_visualizations():
    """
    Effective member ranking
    Performance histogram
    Performance histogram by effective member
    Overall word cloud
    Word cloud by member
    """
    pass


def build_visualizations(image_save_directory, store, risk_cutoff):
    """
    Handles the creation of visualization suite.
    """
    store.score_risk()
    cleared_ballots = store.filter_ballots(risk_cutoff)
    #get_effectiveness_ranking(cleared_ballots)
    calculate_performance_histogram(cleared_ballots, 'Council Performance Rating', '/Users/jga/council-rating.png')
    #create_word_cloud(cleared_ballots)
