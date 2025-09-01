import yaml
import csv
from decimal import Decimal
from collections import deque, defaultdict

# --- Load Files
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

with open("data/normalized_trades.csv", "r") as f:
    trades = list(csv.DictReader(f))

# --- Constants
CGT_TAX_Normal = Decimal(config.get("CGT_TAX_Normal", 0.33))
PERSONAL_EXEMPTION = Decimal(config.get("PERSONAL_EXEMPTION", 1270))

def calculate_fifo(trades: list[dict]) -> list[dict]:
    """
    Calculate FIFO (First In, First Out) capital gains for a list of trades.
    Args:
        trades (list[dict]): A list of trade dictionaries.
    Returns:
        list[dict]: A list of capital gain dictionaries.
    """
    """Design Choice: Use a defaultdict to automatically create a FIFO queue for each asset."""
    lots = defaultdict(deque)

    capital_gains = []

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
        # if sell, find a buy in queue to match qty
        elif trade["type"] == "sell":
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

            capital_gains.append({
                "date": trade["date"],
                "asset": asset,
                "type": "sell",
                "total_gain": total_gain,
                "details": details,
            }) 

    return capital_gains

def generate_report(capital_gains: list[dict]) -> None:
    """
    Generate a report from the capital gains data.
    Args:
        capital_gains (list[dict]): A list of capital gain dictionaries.
    """
    for cg in capital_gains:
        print(f"Date: {cg["date"]}, Asset: {cg["asset"]}, Total-Gain: {cg["total_gain"]}, from sell of lot on {[d["buy_date"] for d in cg["details"]]}")

generate_report(calculate_fifo(trades))

"""
What the user needs for the tax report:
- Total Sales Proceeds (sum of all sell trades)
- Total Chargeable Gains (sum of all sell trades - cost basis)
- Total Losses in the year (if any)
- Amount of Gain (Total Chargeable Gains - Total Losses)
- Personal Exemption (fixed amount)
- Net Chargeable Gain (Total Chargeable Gains - Losses (first) - Personal Exemption)
"""