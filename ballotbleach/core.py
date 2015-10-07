"""
Configuration options and functions that support command-line scripting.

Attributes:
    BALLOTBLEACH_TIMEZONE_NAME (str): Default timezone name is 'America/Chicago'.
    LOGGER_CONFIG (dict): Default dictionary for `logger_configuration`.
    logger (logger): Python logger.
"""
import configparser
from datetime import datetime
import json
from logging import getLogger
from logging import config as log_config
import os
import click
import pytz
import xlrd
from .classes import Ballot, Store
from .analysis import save_charts

logger = getLogger(__name__)

# Default settings
BALLOTBLEACH_TIMEZONE_NAME = 'America/Chicago'
#USER_HOME = os.path.expanduser('~')
#DATA_FILE_PATH = ''.join((USER_HOME, '/clas/raw-ballots.xlsx',))
#OUT_FILE_DIRECTORY = ''.join((USER_HOME, '/clas/'))
LOGGER_CONFIG = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'ballotbleach': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
    }
}


def row_to_ballot(row, tz_name=BALLOTBLEACH_TIMEZONE_NAME):
    """
    Transforms an Excel (xlsx) file row into a :class:`~ballotbleach.classes.Ballot`.
    """
    tz = pytz.timezone(tz_name)
    excel_timestamp = xlrd.xldate_as_tuple(row[0].value, 0)
    logger.debug(excel_timestamp)
    timestamp = datetime(excel_timestamp[0], excel_timestamp[1], excel_timestamp[2],
                         excel_timestamp[3], excel_timestamp[4], excel_timestamp[5],
                         tzinfo=tz)
    selected_actor = row[2].value if row[2].value else 'None'
    subject_rating = row[1].value
    if subject_rating:
        subject_rating = int(subject_rating)
    else:
        subject_rating = None
    ballot = Ballot(timestamp, subject_rating, selected_actor,
                    row[3].value)
    return ballot


def load_xlsx_ballots(filename, skip_first_row=True):
    """
    Creates :class:`~ballotbleach.classes.Ballot` classes from a passed Excel (xlsx) file.
    """
    store = Store()
    book = xlrd.open_workbook(filename=filename)
    sheet = book.sheet_by_index(0)
    logger.info('Excel file - Total filled rows {0}'.format(sheet.nrows))
    start_row = 1 if skip_first_row else 0
    for row in range(start_row, sheet.nrows):
        ballot = row_to_ballot(sheet.row(row))
        store.add_ballot(ballot)
    return store


def dump_clean(input_file_path, output_file_directory,
               out_file_name='clean_ballots.csv', risk_cutoff=75):
    """
    Writes out a CSV with all ballots with a risk score under the passed threshold. The default is
    75 points.
    """
    log_config.dictConfig(LOGGER_CONFIG)
    store = load_xlsx_ballots(input_file_path)
    store.score_risk()
    store.to_csv(output_file_directory, out_file_name, risk_cutoff)


def get_chart_options(config_parser):
    """
    Returns a dictionary with configuration for chart generation.
    """
    chart_options = {
        'actor_ranking_title': 'Most Selected',
        'actor_ranking_tick_format': '%d%%',
        'actor_ranking_image_name': 'most-selected',
        'subject_rating_title': 'Rating',
        'subject_rating_image_name': 'rating',
        'subject_rating_range': [1, 2, 3, 4, 5],
        'mask_file': None,
        'stop_words': None,
    }
    if config_parser.has_section('ballotbleach.charts'):
        section = config_parser['ballotbleach.charts']
        if 'stop_words' in section:
            word_list = json.loads(section['stop_words'])
            del section['stop_words']
            chart_options['stop_words'] = word_list
        if 'subject_rating_range' in section:
            rating_range = json.loads(section['subject_rating_range'])
            del section['subject_rating_range']
            chart_options['subject_rating_range'] = rating_range
        for key, value in section.items():
            chart_options[key] = value
    return chart_options


def analyze(chart_options, input_file, chart_directory, risk_cutoff):
    """
    Called by command line script per setup.py configuration. Writes out
    visualizations with statistics analyzing submitted surveys. By default,
    ballots at or exceeding the risk cutoff of 75 will **not** be considered
    in analytical results.
    """
    store = load_xlsx_ballots(input_file)
    store.score_risk()
    cleared_ballots = store.filter_ballots(risk_cutoff)
    save_charts(chart_directory, chart_options, cleared_ballots)

@click.command()
@click.argument('action', default='full')
@click.option('--cutoff', default=None)
@click.option('--conf', default='ballotbleach.ini')
@click.option('--input', default='raw-ballots.xlsx')
def run(action, cutoff, conf, input):
    """
    Called by command line script per setup.py configuration.
    - Reads and transforms a source file into a ballot store
    - Risk scores ballots in the store
    - Writes out a CSV with *all* ballots and their risk scored.
    - If a cutoff is passed, writes out a CSV with *only* ballots above the cutoff.
    - Generates and saves basic analysis charts.
    """
    # First, handle configuration
    input_file = input
    output_directory = 'results'
    config_parser = configparser.ConfigParser()
    config_parser.read(conf)
    if config_parser.has_section('ballotbleach'):
        if cutoff is None:
            cutoff = int(config_parser['ballotbleach']['risk_cutoff']) \
                if 'risk_cutoff' in config_parser['ballotbleach'] else None
        if 'log_level' in config_parser['ballotbleach']:
            LOGGER_CONFIG['loggers']['ballotbleach']['level'] = config_parser['ballotbleach']['log_level']
        if input_file is None:
            input_file = config_parser['ballotbleach']['input_file'] \
                if 'input_file' in config_parser['ballotbleach'] else 'raw-ballots.xlsx'
        if 'output_directory' in config_parser['ballotbleach']:
            output_directory = config_parser['ballotbleach']['output_directory']
    log_config.dictConfig(LOGGER_CONFIG)
    chart_directory = os.path.join(output_directory, 'charts')
    chart_options = get_chart_options(config_parser)
    logger.info('CONFIG')
    logger.info(chart_options)
    # Now, handle action
    if action == 'charts':
        analyze(chart_options, input_file, chart_directory, cutoff)
    elif action == 'full':
        store = load_xlsx_ballots(input_file)
        store.score_risk()
        store.to_csv(output_directory)
        logger.info('Wrote CSV file with risk-scored ballots to {0} directory'.format(output_directory))
        cleared_ballots = store.filter_ballots(cutoff)
        save_charts(chart_directory, chart_options, cleared_ballots)
    else:
        print('That command action is not supported.')
