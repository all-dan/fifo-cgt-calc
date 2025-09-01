# FIFO CGT Tax Calculator (in development)

**Disclaimer**  
This application is for informational and educational purposes only and does not constitute financial, tax, or legal advice. No warranty is given as to the accuracy, completeness, or suitability of the results for your specific circumstances. Always consult a qualified professional and verify results independently before making any financial or tax decisions. Use of this software is at your own risk; the author accepts no liability for any loss or damage arising from its use.

## Orientation

This app aims to cover the most important CGT rules outlined by Irish Revenue found here: [Revenue.ie: 7. Selling or disposing of shares](https://www.revenue.ie/en/gains-gifts-and-inheritance/transfering-an-asset/how-to-calculate-cgt.aspx) (last accessed: Sep 2025).

**User steps:**  
1. Prepare a `trades.csv` file (see schema below) and place it in `/input` or use existing csv and delete dummy values.
2. Configure settings in `/config` if needed.

**Folders:**  
- `/input`: User-supplied files (e.g., `trades.csv`)
- `/config`: App configuration
- `/data`: Internal files (do not edit)
- `/output`: App-generated results
- `/tests`: Unit tests

Users should only need to access `/input` and `/config`. All other folders are for internal use or development.

The main scripts working in this app are:

- app.py
- fifo.py
- normalization.py

### How the app works

Save your trades to `/input/mytrades.csv` with these columns:

|Date|Type|Asset|Quantity|Price|Fees|Notes
|-|-|-|-|-|-|-
|2025-01-01|buy|btc|0.01|50000|10|my personal note

> **Note:** Use a dot (`.`) as the decimal separator for Quantity, Price, and Fees. Commas will break the CSV format.

### Execution

to follow

## Context 

Irish Revenue (Office of the Revenue Commissioners) is Ireland’s tax and customs authority, it collects taxes, enforces customs, and implements tax law to fund public services. To understand CGT in Ireland better I aimed at implementing some their rules for educational purposes:

#### Implemented:

- **Rate**: 33% on net gains. 
- **Annual exemption**: First €1,270 of gains tax-free.
- **FIFO**: First shares bought are considered first sold.
- **Gain calculation**: Gain = Sale proceeds − (purchase cost + fees).

#### Not yet implemented:
- **4-Week Rule**: Losses are ignored if you repurchase the same asset within 4 weeks.
- **Bonus shares**: Adjust cost per share proportionally if you receive free shares.
- **Rights issues**: Consider enhancement expenditure if you buy discounted shares via rights.
- **Different share classes**: Allocate cost and enhancements by relative market value.
- (**ETFs**: Taxed under Exit Tax (41%), FIFO doesn’t apply, and there’s an 8-year deemed disposal.)

## Function Reference (auto-generated)
<!-- FUNCTION_REFERENCE_START -->

### Module: normalization.py

#### `check_valid_input(raw_trades: list[dict]) -> str` 

 Checks if the input trades are valid.
Args:
    raw_trades (list): The list of raw trade dictionaries to validate.
Returns:
    str: A report of any errors found. 

#### `is_valid_date(date_str: str) -> bool` 

 Checks if a string is a valid date.
Args:
    date_str (str): The string to check.
Returns:
    bool: True if the string is a valid date, False otherwise. 

#### `is_valid_number(num: str) -> bool` 

 Checks if a string is a valid number.
Args:
    num (str): The string to check.
Returns:
    bool: True if the string is a valid number, False otherwise. 

#### `load_existing_txids(file_path: str) -> set` 

 Loads existing transaction IDs from a CSV file.
Args:
    file_path (str): The path to the CSV file.
Returns:
    set: A set of existing transaction IDs. 

#### `main() -> None` 

 Main function to process trade data. 

#### `make_txid(trade: dict) -> str` 

 Creates a synthetic transaction ID for a trade.
Args:
    trade (dict): The trade dictionary containing relevant information.
Returns:
    str: The generated transaction ID. 

#### `write_trades_normalized(trades: list[dict], file_path: str) -> None` 

 Writes the normalized trade data to a CSV file.
Args:
    trades (list): The list of normalized trade dictionaries to write.
    file_path (str): The path to the output CSV file. 

### Module: app.py

### Module: fifo.py

#### `calculate_fifo(trades: list[dict]) -> list[dict]` 

 Calculate FIFO (First In, First Out) capital gains for a list of trades.
Args:
    trades (list[dict]): A list of trade dictionaries.
Returns:
    list[dict]: A list of capital gain dictionaries. 

#### `generate_report(capital_gains: list[dict]) -> None` 

 Generate a report from the capital gains data.
Args:
    capital_gains (list[dict]): A list of capital gain dictionaries. 

<!-- FUNCTION_REFERENCE_END -->

I used `Python 3.13.7`.