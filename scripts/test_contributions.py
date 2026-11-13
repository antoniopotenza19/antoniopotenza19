"""Checks for count parsing and calendar/streak edge cases."""
from datetime import date, timedelta
import unittest
from fetch_contributions import parse_calendar, summarize


class CalendarTests(unittest.TestCase):
    def test_realistic_calendar(self):
        start = date.today() - timedelta(days=364)
        markup = ''.join(f'<td class="ContributionCalendar-day" data-date="{start+timedelta(days=i)}" data-level="{4 if i == 0 else 0}" id="d{i}"></td><tool-tip for="d{i}">{"1,234 contributions" if i == 0 else "No contributions"} on day</tool-tip>' for i in range(365))
        days = parse_calendar(markup)
        self.assertEqual(len(days), 365)
        self.assertEqual(days[0]["count"], 1234)
        self.assertEqual(sum(d["count"] for d in days), 1234)
        with self.assertRaises(ValueError):
            parse_calendar(markup.replace("1,234 contributions", "Unknown"))

    def test_empty_calendar_rejected(self):
        with self.assertRaises(ValueError):
            parse_calendar('<html>Temporarily unavailable</html>')

    def test_current_streak_skips_only_today(self):
        today = date.today()
        days = [{"date": str(today-timedelta(days=4-i)), "count": c} for i,c in enumerate([0,2,1,4,0])]
        self.assertEqual(summarize(days)["current_streak"], 3)
        self.assertEqual(summarize(days)["longest_streak"], 3)
        days[-2]["count"] = 0
        self.assertEqual(summarize(days)["current_streak"], 0)
        self.assertEqual(summarize(days)["longest_streak"], 2)

    def test_all_zero(self):
        self.assertEqual(summarize([{"date":str(date.today()),"count":0}]),
                         {"total":0,"active_days":0,"current_streak":0,"longest_streak":0})


if __name__ == '__main__':
    unittest.main()
