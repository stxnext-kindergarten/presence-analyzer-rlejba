# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

from presence_analyzer import main, views, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


# pylint: disable=maybe-no-member, too-many-public-methods
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5)
        )

    def test_group_by_weekday(self):
        """
        Test group_by_weekday
        """
        testData = {
            'testUser1': {
                datetime.date(2013, 1, 1): {
                    'start': datetime.time(6, 0, 0),
                    'end': datetime.time(17, 00, 0),
                },
                datetime.date(2013, 10, 2): {
                    'start': datetime.time(8, 30, 0),
                    'end': datetime.time(16, 00, 0),
                }
            },
            'testUser2': {
                datetime.date(2013, 9, 22): {
                    'start': datetime.time(9, 0, 0),
                    'end': datetime.time(17, 30, 0),
                },
                datetime.date(2013, 9, 26): {
                    'start': datetime.time(8, 30, 0),
                    'end': datetime.time(16, 30, 0),
                },
                datetime.date(2012, 9, 26): {
                    'start': datetime.time(8, 30, 0),
                    'end': datetime.time(16, 30, 0),
                }
            },
            'testUser3': {}
        }

        testResult = utils.group_by_weekday(testData['testUser1'])
        testResult2 = utils.group_by_weekday(testData['testUser2'])
        testResult3 = utils.group_by_weekday(testData['testUser3'])

        self.assertListEqual(
            testResult, [[], [39600], [27000], [], [], [], []]
        )
        self.assertListEqual(
            testResult2, [[], [], [28800], [28800], [], [], [30600]]
        )
        self.assertListEqual(
            testResult3, [[], [], [], [], [], [], []]
        )

    def test_seconds_since_midnight(self):
        """
        Test second_since_midnight
        """
        self.assertEqual(
            utils.seconds_since_midnight(datetime.time(1, 0, 0)), 3600
        )
        self.assertEqual(
            utils.seconds_since_midnight(datetime.time(1, 2, 3)), 3723
        )
        self.assertEqual(
            utils.seconds_since_midnight(datetime.time(0, 0, 0)), 0
        )

    def test_interval(self):
        """
        Test interval
        """
        self.assertEqual(
            utils.interval(datetime.time(12, 0, 20), datetime.time(13, 0, 20)),
            3600,
        )
        self.assertEqual(
            utils.interval(datetime.time(0, 0, 0), datetime.time(0, 0, 0)),
            0,
        )

    def test_mean(self):
        """
        Test second_since_midnight
        """
        self.assertAlmostEqual(
            utils.mean([12, 4, 1222, 1, 55, 23, 423, 1]), 217.625
        )
        self.assertEqual(
            utils.mean([]), 0
        )
        self.assertAlmostEqual(
            utils.mean([12, 2, 1, 5, 1]), 4.2
        )

    def test_group_by_start_end(self):
        """
        Test group_by_start_end
        """
        testResult = utils.group_by_start_end(utils.get_data()[10])
        testResult2 = utils.group_by_start_end(utils.get_data()[11])
        testResult3 = utils.group_by_start_end([])

        self.assertListEqual(
            testResult, [
                [[], []],
                [[34745], [64792]],
                [[33592], [58057]],
                [[38926], [62631]],
                [[], []],
                [[], []],
                [[], []]
            ]

        )
        self.assertListEqual(
            testResult2, [
                [[33134], [57257]],
                [[33590], [50154]],
                [[33206], [58527]],
                [[37116, 34088], [60085, 57087]],
                [[47816], [54242]],
                [[], []],
                [[], []],
            ]
        )
        self.assertListEqual(
            testResult3, [
                [[], []],
                [[], []],
                [[], []],
                [[], []],
                [[], []],
                [[], []],
                [[], []]
            ]
        )


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
