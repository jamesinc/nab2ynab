
import csv
import argparse
from datetime import datetime

def write(outfile, transactions):

    keys = transactions[0].keys()

    with open(outfile, "w", newline="") as outfile:
        dict_writer = csv.DictWriter(outfile, keys)
        dict_writer.writeheader()
        dict_writer.writerows(transactions)

    print("Done")

def main(infile):

    transactions = []

    with open(infile, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        # Skip headers row
        next(reader)

        for row in reader:
            # Accept format D MMM YY
            txn_date = datetime.strptime(row[0], "%d %b %y")
            try:
                payee = row[8]
            except IndexError:
                payee = ""

            transactions.append({
                "Date": txn_date.strftime("%d/%m/%Y"),
                "Payee": payee,
                "Memo": row[5],
                "Amount": row[1],
            })

    if transactions:
        write(infile, transactions)
    else:
        print("Nothing to do (no transactions detected)")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="NAB to YNAB CSV Converter",
        description="Replaces a National Australia Bank (NAB) format transactions CSV with a YNAB-friendly CSV format"
    )

    parser.add_argument("transactions", help="path to CSV exported from NAB online banking")

    args = parser.parse_args()

    main(args.transactions)
