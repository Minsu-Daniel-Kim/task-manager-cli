"""
Tests for countdown functionality.
"""

import unittest
import sys
import os

# Add parent directory to path to import countdown module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from countdown import parse_time_input, format_time


class TestCountdown(unittest.TestCase):
    """Test countdown timer functionality."""
    
    def test_parse_time_input_minutes(self):
        """Test parsing minutes input."""
        self.assertEqual(parse_time_input("25"), 25 * 60)
        self.assertEqual(parse_time_input("5"), 5 * 60)
        self.assertEqual(parse_time_input("60"), 60 * 60)
    
    def test_parse_time_input_mm_ss(self):
        """Test parsing MM:SS format."""
        self.assertEqual(parse_time_input("05:30"), 5 * 60 + 30)
        self.assertEqual(parse_time_input("10:45"), 10 * 60 + 45)
        self.assertEqual(parse_time_input("00:15"), 15)
    
    def test_parse_time_input_hh_mm(self):
        """Test parsing HH:MM format."""
        self.assertEqual(parse_time_input("1:30"), 1 * 3600 + 30 * 60)
        self.assertEqual(parse_time_input("2:15"), 2 * 3600 + 15 * 60)
    
    def test_parse_time_input_hh_mm_ss(self):
        """Test parsing HH:MM:SS format."""
        self.assertEqual(parse_time_input("01:30:45"), 1 * 3600 + 30 * 60 + 45)
        self.assertEqual(parse_time_input("00:05:30"), 5 * 60 + 30)
        self.assertEqual(parse_time_input("02:00:00"), 2 * 3600)
    
    def test_parse_time_input_invalid(self):
        """Test invalid time input."""
        with self.assertRaises(ValueError):
            parse_time_input("invalid")
        with self.assertRaises(ValueError):
            parse_time_input("25:70")  # Invalid seconds
        with self.assertRaises(ValueError):
            parse_time_input("")
    
    def test_format_time(self):
        """Test time formatting."""
        self.assertEqual(format_time(30), "00:30")
        self.assertEqual(format_time(90), "01:30")
        self.assertEqual(format_time(3661), "01:01:01")
        self.assertEqual(format_time(7200), "02:00:00")
        self.assertEqual(format_time(0), "00:00")


if __name__ == "__main__":
    unittest.main()