import datetime
import csv
import argparse
import sys
import re
import json

# used only because using strptime is impossible with this format
_ugly_date_regexp = re.compile('(?P<month>\d{1,2})/'
                               '(?P<day>\d{1,2})/'
                               '(?P<year>\d{2})'
                               '(?P<hour>\d{1,2}):'
                               '(?P<minute>\d{2})')


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
    parser.add_argument('csvfile', nargs='?',
                        type=argparse.FileType('rU', bufsize=2**18),
                        default=sys.stdin,
                        help='defaults to stdin')
    parser.add_argument('jsonfile', nargs='?',
                        type=argparse.FileType('w', bufsize=2**18),
                        default=sys.stdout,
                        help='defaults to stdout')

    arguments = parser.parse_args()

    records_obj = csv_normalize(arguments.csvfile)
    arguments.jsonfile.write(
        json.dumps(
            dict(records=[rec for rec in records_obj]),
            default=json_complex_type_default,
        )
    )
    arguments.csvfile.close()
    arguments.csvfile.close()

if __name__ == '__main__':
    main()