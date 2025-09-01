import unittest
import tempfile
import csv
import os
from normalization import (
    load_existing_txids, #done
    write_trades_normalized, #done
    make_txid, #done
    check_valid_input,
    is_valid_date, #done
    is_valid_number, #done
)

class TestNormalization(unittest.TestCase):
    def test_is_valid_number(self):
        """Test that is_valid_number correctly identifies valid and invalid numbers."""
        self.assertTrue(is_valid_number("123"))
        self.assertTrue(is_valid_number("123.45"))
        self.assertFalse(is_valid_number("123,45"))
        self.assertFalse(is_valid_number("123. 45"))
        self.assertFalse(is_valid_number(""))
        self.assertTrue(is_valid_number("0"))
        self.assertFalse(is_valid_number("Joe"))
    
    def test_is_valid_date(self):
        """Test that is_valid_date correctly identifies valid and invalid date formats."""
        self.assertTrue(is_valid_date("2025-01-01"))
        self.assertFalse(is_valid_date("2025/01/01"))
        # My verison of Python (3.13.7) accepts this as ISO format
        self.assertTrue(is_valid_date("20250101"))
        self.assertFalse(is_valid_date("01012025"))
        self.assertFalse(is_valid_date("2025"))
        self.assertFalse(is_valid_date("01"))
        self.assertFalse(is_valid_date("2025-January-01"))
        self.assertFalse(is_valid_date("January"))

    def test_load_existing_txids(self):
        """Test loading existing transaction IDs from a CSV file."""
        # Creating a temp CSV to test function
        with tempfile.NamedTemporaryFile(mode="w+", newline="", delete=False) as tmpfile:
            writer = csv.DictWriter(tmpfile, fieldnames=["txid", "other"])
            writer.writeheader()
            writer.writerow({"txid": "abc123", "other": "foo"})
            writer.writerow({"txid": "def456", "other": "bar"})
            writer.writerow({"txid": "", "other": "baz"})
            tmpfile.flush()
            tmpfile_name = tmpfile.name

        # Actual test of the function
        txids = load_existing_txids(tmpfile_name)
        self.assertEqual(txids, {"abc123", "def456"})

        # Clean up
        os.remove(tmpfile_name)

    def test_write_trades_normalized(self):
        """Test writing normalized trades to a CSV file."""
        # Prepare sample trades
        trades = [
            {
                "date": "2025-01-01 00:00:00",
                "asset": "btc",
                "type": "buy",
                "quantity": "1.0",
                "price": "30000",
                "fee": "10",
                "total_gross": "30000",
                "total_net": "30010",
                "txid": "abc123",
                "note": "test"
            }
        ]

        # Write to a temporary file
        with tempfile.NamedTemporaryFile(mode="w+", newline="", delete=False) as tmpfile:
            tmpfile_name = tmpfile.name
            write_trades_normalized(trades, tmpfile_name)

        # Read back and check
        with open(tmpfile_name, newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["date"], "2025-01-01 00:00:00")
            self.assertEqual(rows[0]["asset"], "btc")
            self.assertEqual(rows[0]["type"], "buy")
            self.assertEqual(rows[0]["quantity"], "1.0")
            self.assertEqual(rows[0]["price"], "30000")
            self.assertEqual(rows[0]["fee"], "10")
            self.assertEqual(rows[0]["total_gross"], "30000")
            self.assertEqual(rows[0]["total_net"], "30010")
            self.assertEqual(rows[0]["txid"], "abc123")
            self.assertEqual(rows[0]["note"], "test")

        # Clean up
        os.remove(tmpfile_name)

    def test_make_txid(self):
        """Test synthetic transaction ID generation."""
        trade1 = {
            "Date": "2025-01-01",
            "Type": "buy",
            "Asset": "btc",
            "Quantity": "1.0",
            "Price": "30000"
        }

        trade2 = {
            "Date": "2025-01-02",
            "Type": "sell",
            "Asset": "eth",
            "Quantity": "2.0",
            "Price": "2000"
        }

        hash1 = make_txid(trade1)
        hash1_double = make_txid(trade1)
        hash2 = make_txid(trade2)

        # Hashes for the same trade should be equal
        self.assertEqual(hash1, hash1_double)
        # Hashes for different trades should not be equal
        self.assertNotEqual(hash1, hash2)
        # All hashes should be of length 10
        self.assertEqual(len(hash1), 10)
        self.assertEqual(len(hash2), 10)

    def test_check_valid_input(self):
        """Test validity of input data."""
        # Prepare sample data
        trades_correct = [
            {
                "Date": "2025-01-01",
                "Type": "Buy",
                "Asset": "BTC",
                "Quantity": "1.0",
                "Price": "30000",
                "Fees": "10",
                "Notes": "My Personal Note"
            }
        ] 
        trades_errors = [
            {
                "Date": "25-01-01",
                "Type": "Transfer",
                "Asset": "BTC",
                "Quantity": "1.0",
                "Price": "Money",
                "Fees": "10",
                "Notes": "My Personal Note"
            }
        ] 

        # Run function
        correct_data = check_valid_input(trades_correct)
        error_data = check_valid_input(trades_errors)

        # Evaluate tests
        self.assertEqual(correct_data,[])
        self.assertTrue(any("Invalid date format for 'Date': '25-01-01'" in err for err in error_data))
        self.assertTrue(any("Invalid trade type: Transfer." in err for err in error_data))
        self.assertTrue(any("Invalid value for Price: 'Money'" in err for err in error_data))

if __name__ == "__main__":
    unittest.main()