# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import redirect, abort, url_for
from flask.ext.mako import render_template
from mako.exceptions import TopLevelLookupException

from presence_analyzer.main import app
from presence_analyzer.utils import (
    jsonify,
    get_data,
    mean,
    group_by_weekday,
    group_by_start_end,
    get_xml_data,
    group_by_months
)

import logging
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect(url_for('pages', page="presence_start_end.html"))


@app.route('/<page>')
def pages(page):
    """
    Renders templates.
    """
    try:
        return render_template(page, page=page)
    except TopLevelLookupException:
        return render_template('404.html')


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_xml_data()
    return [
        {'user_id': key, 'name': value['user_name']}
        for key, value in data.iteritems()
    ]


@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
@jsonify
def avatar_view(user_id):
    """
    Returns adress of user avatar.
    """
    data = get_xml_data()
    return data[str(user_id)]['avatar']


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], mean(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], sum(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_view(user_id):
    """
    Returns mean presence time of given
    user grouped by weekday and start/end hour.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_start_end(data[user_id])
    result = [
        (calendar.day_abbr[weekday], mean(start_end[0]), mean(start_end[1]))
        for weekday, start_end in enumerate(weekdays)
    ]
    return result


@app.route('/api/v1/monthly_presence/<int:user_id>', methods=['GET'])
@jsonify
def monthly_presence_view(user_id):
    """
    Returns monthly presence from the start of work.

    The result is grouped like this:
    result = [
        ['2013.03', 23553]
        ['2013.04', 29928]
        ['2013.06', 44211]
    ]
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    months = group_by_months(data[user_id])
    result = [
        [month, value] for (month, value) in months.items()
    ]
    result.sort()
    result.insert(0, ('Month', 'Presence (s)'))

    return result
