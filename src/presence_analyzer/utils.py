# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""

import csv
from json import dumps
from functools import wraps
from datetime import datetime
from threading import Lock

from lxml import etree
from flask import Response

from presence_analyzer.main import app

import logging
log = logging.getLogger(__name__)  # pylint: disable=invalid-name

Cache = {}  # Container for cache decorator.


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        """
        This docstring will be overridden by @wraps decorator.
        """
        return Response(
            dumps(function(*args, **kwargs)),
            mimetype='application/json'
        )
    return inner


def cache(time):
    """
    Stores function data in Cache container.
    """
    lock = Lock()
    current_time = datetime.now()

    def wrapper(function):
        name = function.__name__

        @wraps(function)
        def inner(*args, **kwargs):
            with lock:
                if (name not in Cache or
                    (current_time - Cache[name]['Time']).total_seconds() >
                        time):
                    Cache[name] = {
                        'Time': current_time,
                        'Data': function()
                    }

            return Cache[name]['Data']
        return inner
    return wrapper


@cache(600)
def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {})[date] = {'start': start, 'end': end}

    return data


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = [[], [], [], [], [], [], []]  # one list for every day in week
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0


def group_by_start_end(items):
    """
    Groups given items for start-end hours of each day of the week.
    """
    result = [[[], []] for i in range(7)]
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()][0].append(
            seconds_since_midnight(start)
        )
        result[date.weekday()][1].append(
            seconds_since_midnight(end)
        )
    return result


def get_xml_data():
    """
    Gets data from xml file and groups it like this:
    {
        user_id : {'user_name': user_name, 'avatar': user_avatar_source}
    }
    """
    xml_data = {}
    with open(app.config['DATA_XML'], 'r') as xmlfile:
        tree = etree.parse(xmlfile)
        server = tree.find('server')
        server_data = '{}://{}'.format(
            server.find('protocol').text,
            server.find('host').text
        )

        users = tree.find('users')
        users = users.findall('user')

        for user in users:
            user_id = user.get('id')
            user_name = user.find('name').text
            user_avatar = user.find('avatar').text
            avatar = '{}{}'.format(server_data, user_avatar)
            xml_data[user_id] = {'user_name': user_name, 'avatar': avatar}

    return xml_data
