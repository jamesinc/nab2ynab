"""
convert.py

Converts National Australia Bank (NAB) transaction export CSVs to YouNeedABudget (YNAB) format.
"""

import csv
import argparse
from datetime import datetime

import tabulate


def write(outfile, transactions):

    keys = transactions[0].keys()

    with open(outfile, "w", newline="", encoding="UTF-8") as outfile:
        dict_writer = csv.DictWriter(outfile, keys)
        dict_writer.writeheader()
        dict_writer.writerows(transactions)


def main(infile, auth_only=False):

    transactions = []

    with open(infile, "r", encoding="UTF-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        # Skip headers row
        next(reader)

        uncleared_balance = 0.0
        authorisations = []

        for row in reader:
            # Accept format D MMM YY
            try:
                txn_date = datetime.strptime(row[0], "%d %b %y").strftime("%d/%m/%Y")
            except ValueError:
                print("BONK: Unable to process this CSV file")
                print("      Has it already been run through this converter?")
                raise

            try:
                payee = row[8]
            except IndexError:
                payee = ""

            # Skip purchase authorisations as they will later become actual
            # purchases and the dates will change and this will confuse YNAB
            if row[4].strip().upper() != "PURCHASE AUTHORISATION":
                transactions.append({
                    "Date": txn_date,
                    "Payee": payee,
                    "Memo": row[5],
                    "Amount": row[1],
                })
            else:
                uncleared_balance += float(row[1])
                authorisations.append({
                    "Date": txn_date,
                    "Payee": payee,
                    "Memo": row[5],
                    "Amount": float(row[1])
                })

        if authorisations:
            print("\nThe following transactions have not yet cleared. If you want to add them to YNAB,")
            print("you have to do it manually!\n")

            header = authorisations[0].keys()
            rows = [row.values() for row in authorisations]

            print(tabulate.tabulate(rows, header, floatfmt=".2f", tablefmt="rounded_outline", showindex=True))
            print(f"\nTOTAL UNCLEARED: ${uncleared_balance:.2f}\n")

    if transactions:
        if auth_only:
            print("** Note: the source CSV has not been modified (--auth-only mode) **")
        else:
            write(infile, transactions)
    else:
        print("Nothing to do (no transactions found)")

    print("Done!")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="NAB to YNAB CSV Converter",
        description="Replaces a National Australia Bank (NAB) transactions CSV with a YNAB-friendly CSV format"
    )

    parser.add_argument("transactions", help="path to CSV exported from NAB online banking")
    parser.add_argument("--auth-only", action="store_true", help="just display uncleared transactions and exit")

    args = parser.parse_args()

    main(args.transactions, args.auth_only)
