from argparse import ArgumentError
import datetime
import csv
import argparse
import sys
from configparser import ConfigParser
import re
import json
import pymongo

# used only because using strptime is impossible with this format
_ugly_date_regexp = re.compile('(?P<month>\d{1,2})/'
                               '(?P<day>\d{1,2})/'
                               '(?P<year>\d{2})'
                               '(?P<hour>\d{1,2}):'
                               '(?P<minute>\d{2})')


def cmd_insert(args):
    database = args.connection.patronage
    collection = database.data
    records_generator = csv_normalize(args.csvfile)
    for (num, record) in enumerate(records_generator):
        collection.save(record)
    print(num, 'new objects imported to the database collection')


def cmd_drop_all(args):
    database = args.connection.patronage
    collection = database.data
    print('Removing', collection.count(), 'objects from collection ...')
    collection.drop()
    print('... Done')


def json_complex_type_default(obj):
    """ Function trying to serialize complex objects
    :param obj: object to test if it can be serialized to json
    :return: string representing complex type
    :rtype: str
    """
    if isinstance(obj, datetime.datetime):  # datetime -> iso formatted date
        return obj.isoformat()


def ugly_date_parse(datestr):
    """Function trying to parse ugly date format provided by the organizers
    :param datestr: string containing date representation
    :type datestr: str
    :return: datetime object
    :rtype: datetime.datetime
    """
    date_components = _ugly_date_regexp.match(datestr).groupdict()
    if not date_components:
        raise AttributeError('Cannot parse date for {}'.format(datestr))
    dateint = {key: int(val) for (key, val) in date_components.items()}
    year = dateint['year']
    year += 2000 if year <= 68 else 1900  # calibration of 2-digit year notation
    date = datetime.datetime(year, dateint['month'], dateint['day'],
                             dateint['hour'], dateint['minute'])
    return date


def csv_normalize(fileobj):
    """ Generator that converts complex types from csv file to python types
    :param fileobj: opened file object
    :type fileobj: file
    :return: dictionary normalized
    :rtype: dict
    """
    reader = csv.DictReader(fileobj)
    for row in reader:
        row['Account_Created'] = ugly_date_parse(row['Account_Created'])
        row['Last_Login'] = ugly_date_parse(row['Last_Login'])
        row['Transaction_date'] = ugly_date_parse(row['Transaction_date'])
        row['Longitude'] = float(row['Longitude'])
        row['Latitude'] = float(row['Latitude'])
        row['Price'] = int(row['Price'].replace(',', ''))
        yield row


def main():
    """main function"""
    parser = argparse.ArgumentParser(
        description='BLStream patronage challenge solution',
    )
    parser.add_argument('-c', '--config', dest='config', required=True,
                        type=argparse.FileType('r', bufsize=2**18),
                        help='configuration file')
    subparsers = parser.add_subparsers(title='commands',
                                       help='additional help')

    # import command
    parser_import = subparsers.add_parser('import')
    parser_import.add_argument('csvfile', nargs='?',
                               type=argparse.FileType('rU', bufsize=2**18),
                               default=sys.stdin,
                               help='defaults to stdin')
    parser_import.set_defaults(cmdfunc=cmd_insert)

    # drop_all command
    parser_drop = subparsers.add_parser('drop_all')
    parser_drop.set_defaults(cmdfunc=cmd_drop_all)

    # parse command line and configure according to config file
    args = parser.parse_args()
    cfg = ConfigParser()
    cfg.read_file(args.config)
    args.config.close()
    args.connection = pymongo.MongoClient(
        cfg.get('mongodb', 'host', fallback="localhost"),
        cfg.getint('mongodb', 'port', fallback=27017),
    )

    try:
        args.cmdfunc(args)
    except AttributeError:
        print('command not found', file=sys.stderr)
        parser.print_help()
        return

if __name__ == '__main__':
    main()