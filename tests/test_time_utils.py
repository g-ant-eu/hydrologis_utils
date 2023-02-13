from hydrologis_utils.time_utils import *

import unittest

# run with python3 -m unittest discover tests/

class TestTimeutils(unittest.TestCase):
    CHECKDATE = "2021-12-24 12:00:00"
    CHECKDATE_COMPACT = "20211224_120000"
    
    def test_new_datetime(self):
        string = self.CHECKDATE

        dt = newDatetime(string)

        str = toStringWithSeconds(dt)

        self.assertEqual(string, str)

    def test_new_datetime_utc(self):
        string = self.CHECKDATE

        dt = newDatetimeUtc(string)

        str = toStringWithSeconds(dt)

        self.assertEqual(string, str)
    
    def test_quick_to_string(self):
        string = self.CHECKDATE
        dt = newDatetime(string)
        str = quickToString(dt.timestamp())

        self.assertEqual(string, str)

    def test_compact(self):
        string = self.CHECKDATE
        dt = newDatetime(string)
        str = toStringCompact(dt)

        self.assertEqual(self.CHECKDATE_COMPACT, str)
    
    def test_quick_utc_to_string(self):
        string = self.CHECKDATE
        dt = newDatetimeUtc(string)
        str = quickUtcToString(dt.timestamp())

        self.assertEqual(string, str)         

    def test_epoch_millis(self):
        string = self.CHECKDATE
        dt = newDatetime(string)
        millis = toEpochInMillis(dt)
        self.assertEqual(millis, 1640343600000)




if __name__ == "__main__":
    unittest.main()