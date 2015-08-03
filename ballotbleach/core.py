from logging import getLogger, config
from os.path import expanduser
import xlrd
from .classes import Ballot, Store

logger = getLogger(__name__)


USER_HOME = expanduser('~')
DATA_FILE_PATH = ''.join((USER_HOME, '/dev/data/council_survey_newest.xlsx',))
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
    ballot = Ballot(row[0].value, row[1].value,
                    row[2].value, row[3].value)
    return ballot


def load_ballots(filename):
    store = Store()
    book = xlrd.open_workbook(filename=filename)
    sheet = book.sheet_by_index(0)
    logger.info('Total filled rows {0}'.format(sheet.nrows))
    for row in range(1, sheet.nrows):
        ballot = row_to_ballot(sheet.row(row))
        store.add_ballot(ballot)
    return store


def run():
    config.dictConfig(LOGGER_CONFIG)
    store = load_ballots(DATA_FILE_PATH)
    store.print_all_ballots()