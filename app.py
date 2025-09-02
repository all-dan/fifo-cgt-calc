from fifo import calculate_fifo
from normalization import run_normalization
import csv
import argparse

# --- Load Files
with open("data/normalized_trades.csv", "r") as f:
    trades = list(csv.DictReader(f))

# --- File Paths
MY_TRADES_PATH = "input/my_trades.csv"
NORMALIZED_TRADES_PATH = "data/normalized_trades.csv"
OUTPUT_REPORT_PATH = "output/report.csv"

def generate_report(sold_lots: list[dict], output_file: str) -> None:
    """
    Generate a report from the capital gains data
    Args:
        sold_lots (list[dict]): A list of sold lot dictionaries.
        output_file (str): The path to the output CSV file.
    """
    # Make sure to only try to gnerate a report if capital_gains were calculated before
    if sold_lots:
        with open(output_file, "w", newline="") as csvfile:
            fieldnames = ["Date", "Asset", "Sold Quantity", "Total Gain", "Buys Used"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for lot in sold_lots:
                writer.writerow({
                    "Date": lot['date'],
                    "Asset": lot['asset'],
                    "Sold Quantity": lot['quantity'],
                    "Total Gain": lot['total_gain'],
                    "Buys Used": [f"Date: {d['buy_date']}, Used Qty: {d['used_qty']}, Cost/Unit: {d['cost_per_unit']}, Cost Basis: {d['cost_basis']}, Gain: {d['gain']}" for d in lot['details']]
                })
    else:
        return None

def main():
    parser = argparse.ArgumentParser(description="FIFO CGT Calculator")
    parser.add_argument("--year", type=int, default=2025, help="Tax year to calculate (default: 2025)")
    parser.add_argument("--input", type=str, default=MY_TRADES_PATH, help="Path to input trades CSV")
    parser.add_argument("--output", type=str, default=OUTPUT_REPORT_PATH, help="Path to output report CSV")
    args = parser.parse_args()

    run_normalization(args.input, NORMALIZED_TRADES_PATH)
    generate_report(calculate_fifo(trades, args.year), args.output)

if __name__ == "__main__":
    main()