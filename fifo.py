import yaml
from decimal import Decimal
from datetime import datetime
from collections import deque, defaultdict

# --- Load Files
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# --- File Paths and Constants
MY_TRADES_PATH = "input/my_trades.csv"
NORMALIZED_TRADES_PATH = "data/normalized_trades.csv"

CGT_TAX_Normal = Decimal(config.get("CGT_TAX_Normal", 0.33))
PERSONAL_EXEMPTION = Decimal(config.get("PERSONAL_EXEMPTION", 1270))

# --- Functions
def calculate_fifo(trades: list[dict], tax_year: int) -> list[dict]:
    """
    Calculate FIFO (First In, First Out) capital gains for a list of trades.
    Args:
        trades (list[dict]): A list of trade dictionaries.
    Returns:
        list[dict]: A list of capital gain dictionaries.
    """
    lots = defaultdict(deque)

    sold_lots = []

    #First Check if sells in chosen tax year
    if not any(trade["type"] == "sell" and datetime.fromisoformat(trade["date"]).year == tax_year for trade in trades):
        print(f"WARNING: No sell trade found in tax year {tax_year}")
    else:
        # For FIFO it's important that that tx are sorted by date
        # trade in this for loop accesses the dicts in trades
        for trade in sorted(trades, key=lambda t: t["date"]): 
            asset = trade["asset"]
            qty = Decimal(trade["quantity"])
            # if a buy push the qty to the FIFO queue
            if trade["type"] == "buy":
                lots[asset].append({
                    "quantity": qty,
                    "total_net": Decimal(trade["total_net"]),
                    "original_qty": qty,
                    "date": trade["date"]
                })
            # if sell in tax_year , find a buy in queue to match qty
            elif trade["type"] == "sell" and datetime.fromisoformat(trade["date"]).year == tax_year:
                qty_to_match = qty
                details = []

                proceeds = Decimal(trade["total_net"])
                # important: since a sell can be partial, a while loop ensures
                # that while qty_to_match > 0 the algorithm keeps matching with
                # remaining buys on the queue
                while qty_to_match > 0 and lots[asset]:
                    buy_lot = lots[asset][0]
                    match_qty = min(qty_to_match, buy_lot["quantity"])

                    # each trade has a total net value, which divided by it's original
                    # qty is the cost per unit, this can be used to calculate cost_basis
                    cost_per_unit = buy_lot["total_net"] / buy_lot["original_qty"]
                    cost_basis = cost_per_unit * match_qty
                    gain = proceeds - cost_basis

                    details.append({
                        "used_qty": match_qty,
                        "cost_per_unit": cost_per_unit,
                        "cost_basis": cost_basis,
                        "gain": gain,
                        "buy_date": buy_lot["date"],
                    })

                    # the match_qty and qty_to_match are updated and the buy_lot is
                    # removed from the queue if fully matched
                    buy_lot["quantity"] -= match_qty
                    qty_to_match -= match_qty
                    if buy_lot["quantity"] == 0:
                        lots[asset].popleft()
                if qty_to_match > 0:
                    print(f"WARNING: Unmatched sell quantity for asset: {asset}. Remaining quantity: {qty_to_match}")

                total_gain = sum(d["gain"] for d in details)

                sold_lots.append({
                    "date": trade["date"],
                    "asset": asset,
                    "type": "sell",
                    "quantity": qty,
                    "total_gain": total_gain,
                    "details": details,
                })
        return sold_lots