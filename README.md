# FIFO CGT Tax Calculator (in development)

**Disclaimer**  
This application is for informational and educational purposes only and does not constitute financial, tax, or legal advice. No warranty is given as to the accuracy, completeness, or suitability of the results for your specific circumstances. Always consult a qualified professional and verify results independently before making any financial or tax decisions.

## Orientation

This app takes a list of sell and buy transactions and calculates the capital gain based on FIFO logic. By default it considers basic Irish Revenue rules: 33% CGT on sold shares/ crypto as well as a 1270 EUR personal exemption. There are many more rules to this so the app does not give an accurate picture of taxes owed. Just to name a few rules I implemented, vs those that I might implement in the future:

### Implemented:

- **Rate**: 33% on net gains. 
- **Annual exemption**: First €1,270 of gains tax-free.
- **FIFO**: First shares bought are considered first sold.
- **Gain calculation**: Gain = Sale proceeds − (purchase cost + fees).

### Not implemented:
- **4-Week Rule**: Losses are ignored if you repurchase the same asset within 4 weeks.
- **Bonus shares**: Adjust cost per share proportionally if you receive free shares.
- **Rights issues**: Consider enhancement expenditure if you buy discounted shares via rights.
- **Different share classes**: Allocate cost and enhancements by relative market value.
- (**ETFs**: Taxed under Exit Tax (41%), FIFO doesn’t apply, and there’s an 8-year deemed disposal.)

## Execution and Structure

### User steps:

1. Prepare a `my_trades.csv` file (see: CSV layout below) and place it in `/input` or use the existing csv and delete dummy values.

**CSV Layout**

|Date|Type|Asset|Quantity|Price|Fees|Notes
|-|-|-|-|-|-|-
|2025-01-01|buy|btc|0.01|50000|10|my personal note

> **Note:** Use a dot (`.`) as the decimal separator for Quantity, Price, and Fees. Commas will break the CSV format.

2. Configure settings in `/config` if changes are needed (defaults below):

```yaml
GT_TAX_Normal: 0.33 
PERSONAL_EXEMPTION: 1270
```

3. You can run the CLI from your projects folder like this:

```sh
python app.py
```

### Flags (optional):
- `--year` (default: 2025): Tax year to calculate.
- `--input` (default: input/my_trades.csv): Path to input file.
- `--output` (default: output/report.csv): Path to output file.

Run app with optional flags: 
```sh
python app.py --year 2025 --input input/custom_file_name.csv --output output/custom_file_name.csv
```

### Folders:
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

## Function Reference (auto-generated)
<!-- FUNCTION_REFERENCE_START -->

### Module: normalization.py

#### `check_valid_input(raw_trades: list[dict]) -> list[str]` 

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

#### `make_txid(trade: dict) -> str` 

 Creates a synthetic transaction ID for a trade.
Args:
    trade (dict): The trade dictionary containing relevant information.
Returns:
    str: The generated transaction ID. 

#### `run_normalization(my_trades: str, normalized_trades: str) -> None` 

 Main function to process trade data. 

#### `write_trades_normalized(trades: list[dict], file_path: str) -> None` 

 Writes the normalized trade data to a CSV file.
Args:
    trades (list): The list of normalized trade dictionaries to write.
    file_path (str): The path to the output CSV file. 

### Module: fifo.py

#### `calculate_fifo(trades: list[dict], tax_year: int) -> list[dict]` 

 Calculate FIFO (First In, First Out) capital gains for a list of trades.
Args:
    trades (list[dict]): A list of trade dictionaries.
Returns:
    list[dict]: A list of capital gain dictionaries. 

### Module: app.py

#### `calculate_fifo(trades: list[dict], tax_year: int) -> list[dict]` 

 Calculate FIFO (First In, First Out) capital gains for a list of trades.
Args:
    trades (list[dict]): A list of trade dictionaries.
Returns:
    list[dict]: A list of capital gain dictionaries. 

#### `generate_report(sold_lots: list[dict], output_file: str) -> None` 

 Generate a report from the capital gains data
Args:
    sold_lots (list[dict]): A list of sold lot dictionaries.
    output_file (str): The path to the output CSV file. 

#### `main()` 

 None 

#### `run_normalization(my_trades: str, normalized_trades: str) -> None` 

 Main function to process trade data. 



<!-- FUNCTION_REFERENCE_END -->