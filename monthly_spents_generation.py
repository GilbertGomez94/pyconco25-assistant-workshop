"""
generate_transactions.py

This script produces a synthetic bank ledger covering the last three months
from the current date. The output is a tab‐separated table with the following columns:

    Date        – DD/MM/YYYY
    Description – Transaction description
    Amount      – Positive for income, negative for expense
    REF         – 11‐digit random reference number
    Available   – Running balance after each transaction

Features:
1. Three salary deposits (one per month)
2. Three flat rent payments (one per month)
3. A variety of additional expenses (80% chance) and small incomes (20% chance)
4. A final “Adjustment” transaction to ensure the net of all amounts is exactly +100 USD

Dependencies:
- Python 3.7+
- pandas
- python-dateutil
"""

import random
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd


def generate_random_ref(length: int = 11) -> str:
    """
    Generate a random numeric reference string of fixed length.

    Args:
        length (int): Number of digits. Default is 11.

    Returns:
        str: Random numeric string.
    """
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


def format_date(dt: datetime.date) -> str:
    """
    Format a date object as DD/MM/YYYY.

    Args:
        dt (datetime.date): The date to format.

    Returns:
        str: Formatted date string.
    """
    return dt.strftime("%d/%m/%Y")


def build_transactions(start_date: datetime.date,
                       end_date: datetime.date,
                       initial_balance: float = 5000.0) -> pd.DataFrame:
    """
    Generate a DataFrame of transactions between start_date and end_date.

    The function will:
      - Add three salary deposits (1500 USD each) spaced monthly.
      - Add three rent payments (–800 USD each) spaced monthly.
      - Add multiple random transactions (expenses or small incomes).
      - Compute a running balance.
      - Append a final “Adjustment” so that the overall net change is +100 USD.

    Args:
        start_date (datetime.date): Beginning of the transaction period.
        end_date (datetime.date): End of the transaction period.
        initial_balance (float): Starting account balance.

    Returns:
        pd.DataFrame: Columns = [Date, Description, Amount, REF, Available]
    """
    transactions = []
    salary_amount = 1500.00
    rent_amount = 800.00

    # 1) Three salary deposits, one each month
    for month_offset in range(1, 4):
        txn_date = start_date + relativedelta(months=month_offset)
        transactions.append({
            "Date": format_date(txn_date),
            "Description": "Salary Deposit",
            "Amount": salary_amount,
            "REF": generate_random_ref()
        })

    # 2) Three rent payments, one each month (flat expense)
    for month_offset in range(1, 4):
        txn_date = start_date + relativedelta(months=month_offset, days=2)
        transactions.append({
            "Date": format_date(txn_date),
            "Description": "Rent Payment",
            "Amount": -rent_amount,
            "REF": generate_random_ref()
        })

    # 3) Additional random transactions
    expense_descriptions = [
        "Food Delivery", "Game coins", "Online Transfer",
        "Raffle Ticket",
        "Utility Payment", "Credit Card Payment", "Subscription Fee"
    ]
    income_descriptions = [
        "Interest", "Cashback", "Freelance Income"
    ]

    total_days = (end_date - start_date).days
    num_extra = 120  # adjust volume of extras as desired

    for _ in range(num_extra):
        # pick a random date in the interval
        random_offset = random.randint(0, total_days)
        txn_date = start_date + datetime.timedelta(days=random_offset)

        # 80% chance expense, 20% chance small income
        if random.random() < 0.8:
            desc = random.choice(expense_descriptions)
            amt = round(-random.uniform(20.0, 300.0), 2)
        else:
            desc = random.choice(income_descriptions)
            amt = round(random.uniform(5.0, 200.0), 2)

        transactions.append({
            "Date": format_date(txn_date),
            "Description": desc,
            "Amount": amt,
            "REF": generate_random_ref()
        })

    # Build DataFrame and sort by date
    df = pd.DataFrame(transactions)
    df["Date_dt"] = pd.to_datetime(df["Date"], dayfirst=True)
    df = df.sort_values("Date_dt").reset_index(drop=True)
    df.drop(columns=["Date_dt"], inplace=True)

    # Calculate running balance
    df["Available"] = initial_balance + df["Amount"].cumsum()

    # Compute net and add adjustment so net sum = +100 USD
    net_change = df["Amount"].sum()
    adjustment = 100.0 - net_change

    # Append final adjustment entry on end_date
    adj_df = pd.DataFrame([{
        "Date": format_date(end_date),
        "Description": "Adjustment",
        "Amount": adjustment,
        "REF": generate_random_ref(),
        "Available": df["Available"].iloc[-1] + adjustment
    }])
    # concat it onto the bottom
    df = pd.concat([df, adj_df], ignore_index=True)

    # Re‐order columns
    df = df[["Date", "Description", "Amount", "REF", "Available"]]
    return df


if __name__ == "__main__":
    # Define period: last 3 months until today
    today = datetime.date.today()
    three_months_ago = today - relativedelta(months=3)

    # Generate ledger and print as TSV
    ledger_df = build_transactions(
        start_date=three_months_ago,
        end_date=today,
        initial_balance=5000.0
    )

    # Output to stdout in tab‐separated format
    ledger_df.to_csv("transactions2.csv", index=False)
