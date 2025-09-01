import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
import hashlib
import os

# --- Definition of valid trade types/ required fields
VALID_TRADE_TYPES = ["buy", "sell"]
REQUIRED_FIELDS = ["Date", "Type", "Asset", "Quantity", "Price"]
EXPECTED_COLUMNS = ["Date", "Type", "Asset", "Quantity", "Price", "Fees", "Notes"]

MY_TRADES_PATH = "input/my_trades.csv"
NORMALIZED_TRADES_PATH = "data/normalized_trades.csv"
# --- Helper Functions Start
def is_valid_number(num: str) -> bool:
    """
    Checks if a string is a valid number.
    Args:
        num (str): The string to check.
    Returns:
        bool: True if the string is a valid number, False otherwise.
    """
    try:
        Decimal(num)
        return True
    except (ValueError, TypeError, InvalidOperation):
        return False

def is_valid_date(date_str: str) -> bool:
    """
    Checks if a string is a valid date.
    Args:
        date_str (str): The string to check.
    Returns:
        bool: True if the string is a valid date, False otherwise.
    """
    try:
        datetime.fromisoformat(date_str)
        return True
    except (ValueError, TypeError):
        return False

def check_valid_input(raw_trades: list[dict]) -> list[str]:
    """
    Checks if the input trades are valid.
    Args:
        raw_trades (list): The list of raw trade dictionaries to validate.
    Returns:
        str: A report of any errors found.
    """
    error_report = []
    for line_num, t in enumerate(raw_trades, start=2):  # start=2 to account for header row
        
        row_errors = []

        # Check if there are unexpected columns
        extra_cols = set(t.keys()) - set(EXPECTED_COLUMNS)
        if extra_cols:
            # Convert all to string and filter out None
            extra_cols_str = ', '.join(str(col) for col in extra_cols if col is not None)
            # If None: it's likely the user added a comma somewhere
            if None in extra_cols:
                row_errors.append(f"Too many fields in this row (possible extra comma in a value e.g. 1,2 instead of 1.2).")
            if extra_cols_str:
                row_errors.append(f"Unexpected columns: {extra_cols_str}. Possible formatting error, check headers for accuracy.")
        # Check for missing required fields
        for field in REQUIRED_FIELDS:
            if not t.get(field, "").strip():
                row_errors.append(f"Missing required field: {field}")
        # Check for valid trade type
        if t.get("Type", "").strip().lower() not in VALID_TRADE_TYPES:
            row_errors.append(f"Invalid trade type: {t.get('Type')}. Valid types are: {VALID_TRADE_TYPES}.")
        # Check for valid numeric fields
        for num_field in ["Price", "Quantity"]:
            if not is_valid_number(t.get(num_field, "")):
                row_errors.append(f"Invalid value for {num_field}: '{t.get(num_field)}' (e.g. 123.45 or 123)")
        # Check for valid fee field
        fee_val = t.get("Fees", "").strip()
        if fee_val not in ["", None] and not is_valid_number(fee_val):
            row_errors.append(f"Invalid value for Fee: '{fee_val}' (e.g. 123.45 or 123)")
        # Check for valid date field
        if t.get("Date").strip() and not is_valid_date(t["Date"].strip()):
            row_errors.append(f"Invalid date format for 'Date': '{t.get('Date')}' (e.g. 2025-01-01)")
        
        # Aggregate errors
        if row_errors:
            error_report.append(f"Line {line_num}: " + "; ".join(row_errors))
    return error_report    

def make_txid(trade: dict) -> str:
    """
    Creates a synthetic transaction ID for a trade.
    Args:
        trade (dict): The trade dictionary containing relevant information.
    Returns:
        str: The generated transaction ID.
    """
    base = f"{trade['Date']}_{trade['Type']}_{trade['Asset']}_{trade['Quantity']}_{trade['Price']}"
    return hashlib.sha256(base.encode()).hexdigest()[:10]

def write_trades_normalized(trades: list[dict], file_path: str) -> None:
    """
    Writes the normalized trade data to a CSV file.
    Args:
        trades (list): The list of normalized trade dictionaries to write.
        file_path (str): The path to the output CSV file.
    """
    if not trades:
        return
    # Order of columns for the output CSV
    col_names = [
        "date", "asset", "type", "quantity", "price", "fee", 
        "total_gross", "total_net", "txid", "note"
    ]

    with open(file_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=col_names)
        writer.writeheader()
        counter = 0
        for t in trades:
            row = {k: (str(v) if isinstance(v, (Decimal, datetime)) else v) for k, v in t.items()}
            writer.writerow(row)
            counter += 1
        print(f"INFO: Added {counter} new trades.")    

def load_existing_txids(file_path: str) -> set:
    """
    Loads existing transaction IDs from a CSV file.
    Args:
        file_path (str): The path to the CSV file.
    Returns:
        set: A set of existing transaction IDs.
    """
    if not os.path.exists(file_path):
        return set()
    with open(file_path, newline='') as f:
        reader = csv.DictReader(f)
        return {row.get("txid") for row in reader if row.get("txid")}

# --- Helper Functions End

def main() -> None:
    """
    Main function to process trade data.
    """
    trades = []

    with open(MY_TRADES_PATH, "r") as f:
        raw_trades = list(csv.DictReader(f))

    error_report = check_valid_input(raw_trades)

    if error_report:
        print("ERROR: Errors found in the CSV file:")
        for err in error_report:
            print(err)

    else:
        existing_txids = load_existing_txids(NORMALIZED_TRADES_PATH)

        for t in raw_trades:
            
            txid = make_txid({
                "Date": t["Date"].strip(),
                "Type": t["Type"].strip().lower(),
                "Asset": t["Asset"].strip().lower(),
                "Quantity": t["Quantity"].strip(),
                "Price": t["Price"].strip()
            })

            if txid in existing_txids:
                continue
            else:
                date = datetime.fromisoformat(t["Date"])
                fee = Decimal(t["Fees"].strip()) if t.get("Fees", "").strip() not in ["", None] else Decimal(0)
                total_gross = Decimal(t["Price"].strip()) * Decimal(t["Quantity"].strip())

                if t["Type"].strip().lower() == "buy":
                    total_net = total_gross + fee
                elif t["Type"].strip().lower() == "sell":
                    total_net = total_gross - fee

                trades.append({
                    "date": date,
                    "asset": t["Asset"].strip().lower(),
                    "type": t["Type"].strip().lower(),
                    "quantity": Decimal(t["Quantity"].strip()),
                    "price": Decimal(t["Price"].strip()),
                    "fee": fee,
                    "total_gross": total_gross,
                    "total_net": total_net,
                    "txid": txid,
                    "note": t.get("Notes", "").strip(),
                })
                existing_txids.add(txid)
    if trades:
        write_trades_normalized(trades, NORMALIZED_TRADES_PATH)
    else: print("INFO: No new trades found.")

if __name__ == "__main__":
    main()