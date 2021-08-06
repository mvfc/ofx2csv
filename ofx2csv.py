from csv import DictWriter
from glob import glob
from ofxparse import OfxParser
import json
import urllib.request
import datetime
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("-o", "--outputtype", help = "singlecsv, json, or manycsv", default="singlecsv")
args = argparser.parse_args()


DATE_FORMAT = "%d/%m/%Y"
jsonBody = {}
outputtype = args.outputtype
jsonBody["data"] = []
allStatements = []


def write_csv(statement, out_file):
    print("Writing: " + out_file)
    fields = ['Date', 'Description (payee)', 'Transaction Type (type)', 'UID', 'Amount',
              'sic', 'mcc', 'Notes (memo)', 'Debit', 'Credit', 'Balance', 'FID', 'Organization']
    with open(out_file, 'w', newline='') as f:
        writer = DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for line in statement:
            writer.writerow(line)


def get_statement_from_qfx(qfx):
    #print(qfx.account.account_id)
    #print(qfx.account.institution.organization)
    #print(qfx.account.institution.fid)
    balance = qfx.account.statement.balance
    statement = []
    credit_transactions = ['credit', 'dep', 'int', 'directdep']
    debit_transactions = ['debit', 'atm', 'pos',
                          'xfer', 'check', 'fee', 'payment']
    other_transactions = ['other']
    for transaction in qfx.account.statement.transactions:
        #print(transaction.type)
        credit = ""
        debit = ""
        balance = balance + transaction.amount
        if transaction.type in credit_transactions:
            credit = transaction.amount
        elif transaction.type in debit_transactions:
            debit = -transaction.amount
        elif transaction.type in other_transactions:
            if transaction.amount < 0:
                debit = -transaction.amount
            else:
                credit = transaction.amount
        else:
            raise ValueError("Unknown transaction type:" + transaction.type)

        line = {
            'Date': transaction.date.strftime(DATE_FORMAT),
            'Description (payee)': transaction.payee,
            'Transaction Type (type)': transaction.type,
            'Notes (memo)': transaction.memo,
            'UID': transaction.id,
            'Amount': str(transaction.amount),
            'sic': transaction.sic,
            'mcc': transaction.mcc,
            'Debit': str(debit),
            'Credit': str(credit),
            'Balance': str(balance),
            'FID': qfx.account.institution.fid,
            'Organization': qfx.account.institution.organization}
        statement.append(line)
        jsonBody["data"].append(line)
    return statement


files = glob(r"*.ofx")
for qfx_file in files:
    qfx = OfxParser.parse(open(qfx_file, encoding="latin-1"))
    statement = get_statement_from_qfx(qfx)
    allStatements = allStatements + statement
    #print(statement)

    if outputtype == 'manycsv':
        out_file = "converted_" + qfx_file.replace(".ofx", ".csv")
        write_csv(statement, out_file)
if outputtype == 'singlecsv':
    out_file = "ofx-transactions.csv"
    write_csv(allStatements, out_file)
else:
    with open('ofx-transactions.json', 'w') as outfile:
        json.dump(jsonBody, outfile)