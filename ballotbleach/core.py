"""
Configuration options and functions that support command-line scripting.

Attributes:
    BALLOTBLEACH_TIMEZONE_NAME (str): A timezone name. Default is 'America/Chicago'.
    DATA_FILE_PATH (str): File path for raw survey input data.
    OUT_FILE_DIRECTORY (str): File path to output processed data result file.
    LOGGER_CONFIG (dict): A dictionary for `logger_configuration`.
    logger (logger): Python logger.
"""
from datetime import datetime
from logging import getLogger, config
from os.path import expanduser
import pytz
import xlrd
from .classes import Ballot, Store
from .analysis import build_visualizations

logger = getLogger(__name__)

BALLOTBLEACH_TIMEZONE_NAME = 'America/Chicago'
USER_HOME = expanduser('~')
DATA_FILE_PATH = ''.join((USER_HOME, '/dev/data/council_survey_newest.xlsx',))
OUT_FILE_DIRECTORY = ''.join((USER_HOME, '/dev/data/'))
LOGGER_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
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
            'level': 'DEBUG',
        },
    }
}


def row_to_ballot(row):
    """
    Transforms an Excel (xlsx) file row into a :class:`~ballotbleach.classes.Ballot`.
    """
    tz = pytz.timezone(BALLOTBLEACH_TIMEZONE_NAME)
    excel_timestamp = xlrd.xldate_as_tuple(row[0].value, 0)
    logger.debug(excel_timestamp)
    timestamp = datetime(excel_timestamp[0], excel_timestamp[1], excel_timestamp[2],
                         excel_timestamp[3], excel_timestamp[4], excel_timestamp[5],
                         tzinfo=tz)
    most_effective = row[3].value if row[3].value else 'None'
    ballot = Ballot(timestamp, row[1].value,
                    row[2].value, most_effective)
    return ballot


def load_ballots(filename, skip_first_row=True):
    """
    Creates :class:`~ballotbleach.classes.Ballot` classes from a passed Excel (xlsx) file.
    """
    store = Store()
    book = xlrd.open_workbook(filename=filename)
    sheet = book.sheet_by_index(0)
    logger.debug('Total filled rows {0}'.format(sheet.nrows))
    start_row = 1 if skip_first_row else 0
    for row in range(start_row, sheet.nrows):
        ballot = row_to_ballot(sheet.row(row))
        store.add_ballot(ballot)
    return store


def run(out_file_name='all_ballots.csv'):
    """
    Called by command line script per setup.py configuration. Writes out
    a CSV with *all* ballots scored for risk.
    """
    config.dictConfig(LOGGER_CONFIG)
    store = load_ballots(DATA_FILE_PATH)
    store.score_risk()
    store.to_csv(OUT_FILE_DIRECTORY, out_file_name)


def dump_clean(out_file_name='clean_ballots.csv', risk_cutoff=75):
    """
    Called by command line script per setup.py configuration. Writes out
    a CSV with all ballots with a risk score under the passed threshold. The default is
    75 points.
    """
    config.dictConfig(LOGGER_CONFIG)
    store = load_ballots(DATA_FILE_PATH)
    store.score_risk()
    store.to_csv(OUT_FILE_DIRECTORY, out_file_name, risk_cutoff)


def analyze(image_save_directory=OUT_FILE_DIRECTORY, risk_cutoff=75):
    """
    Called by command line script per setup.py configuration. Writes out
    visualizations with statistics analyzing submitted surveys. By default,
    ballots at or exceeding the risk cutoff of 75 will **not** be considered
    in analytical results.
    """
    store = load_ballots(DATA_FILE_PATH)
    build_visualizations(image_save_directory, store, risk_cutoff)
