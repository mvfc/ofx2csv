#!/usr/bin/env` python3
#
# Convert Quicken QFX/OFX file into CSV
#
# Origin code from whistler/ofx2csv.py
# https://gist.github.com/whistler/e7c21c70d1cbb9c4b15d
#
# NKN: Modified for more generically convert all data in transactions, and
# positions into two CSV files.

from datetime import datetime
from pathlib import Path
from decimal import Decimal
from csv import DictWriter
from glob import glob
from ofxparse import OfxParser

import json
import argparse
import pprint


def myDir(obj):
  items = []
  for key in dir(obj):
    if not key.startswith('__'):
      items.append(key)
  return items


def showStructure(obj, depth : int =5):
  if depth==0: return obj
  if isinstance(obj, str): return obj
  if isinstance(obj, int): return obj
  if isinstance(obj, Decimal): return float(obj)

  if isinstance(obj, list): 
    items = []
    for item in list(obj):
      items.append(showStructure(item, depth-1))
    return items

  if isinstance(obj, dict): 
    items = {}
    for key in dict(obj):
      items[key] = showStructure(obj[key], depth-1)
    return items

  items = {}
  for key in dir(obj):
    if not key.startswith('__'):
      items[key] = showStructure(getattr(obj, key), depth-1)
  return items


def get_statement_from_qfx(qfx : OfxParser):
    #DBG print("qfx                               :{}".format(myDir(qfx                               )))
    #DBG print("qfx.account                       :{}".format(myDir(qfx.account                       )))
    #DBG print("qfx.account.statement             :{}".format(myDir(qfx.account.statement             )))
    #DBG print("qfx.account.statement.transactions:{}".format(myDir(qfx.account.statement.transactions)))

    #DBG print("accounts:")
    #DBG pprint.pprint(showStructure(qfx.accounts, 2))

    #DBG print("statement:")
    #DBG pprint.pprint(showStructure(qfx.accounts[0].statement, 1))

    #DBG print("transactions:")
    #DBG pprint.pprint(showStructure(qfx.accounts[0].statement.transactions, 2))

    #DBG print("positions:")
    #DBG pprint.pprint(showStructure(qfx.accounts[0].statement.positions, 2))

    #DBG print("security_list:")
    #DBG pprint.pprint(showStructure(qfx.security_list))

    # Read all security names
    secId2Name = {}
    for security in qfx.security_list:
      secId2Name[security.uniqueid] = security.name

    # Convert all accounts transactions into a table/list of activity
    statement = []
    for account in qfx.accounts:
      for transaction in account.statement.transactions:
        line = {}

        for field in dir(account):
          if not field.startswith('__') and field!=":":
            val = getattr(account, field)
            if isinstance(val, str): line[field] = val
            if isinstance(val, Decimal): line[field] = float(val)
            if isinstance(val, datetime): line[field] = val.strftime('%m/%d/%Y')

        for field in dir(transaction):
          if not field.startswith('__'):
            val = getattr(transaction, field)
            if field=="security": val = secId2Name[val]
            if isinstance(val, str): line[field] = val
            if isinstance(val, Decimal): line[field] = float(val)
            if isinstance(val, datetime): line[field] = val.strftime('%m/%d/%Y')

        #if not statement: print("{}".format(line.keys()))
        #print("{}".format(line.values()))
        statement.append(line)
    return statement


def get_positions_from_qfx(qfx : OfxParser):
    #DBG print("positions:")
    #DBG pprint.pprint(showStructure(qfx.accounts[0].statement.positions, 2))

    #DBG print("security_list:")
    #DBG pprint.pprint(showStructure(qfx.security_list))

    # Read all security names
    secId2Name = {}
    for security in qfx.security_list:
      secId2Name[security.uniqueid] = security.name

    # Convert all accounts positions into a table/list of activity
    positions = []
    for account in qfx.accounts:
      for position in account.statement.positions:
        line = {}

        for field in dir(account):
          if not field.startswith('__') and field!=":":
            val = getattr(account, field)
            if isinstance(val, str): line[field] = val
            if isinstance(val, Decimal): line[field] = float(val)
            if isinstance(val, datetime): line[field] = val.strftime('%m/%d/%Y')

        for field in dir(position):
          if not field.startswith('__'):
            val = getattr(position, field)
            if field=="security": val = secId2Name[val]
            if isinstance(val, str): line[field] = val
            if isinstance(val, Decimal): line[field] = float(val)
            if isinstance(val, datetime): line[field] = val.strftime('%m/%d/%Y')

        #if not positions: print("{}".format(line.keys()))
        #print("{}".format(line.values()))
        positions.append(line)
    return positions


def save_files(table, outputtype, out_file):
  if outputtype == 'csv':
    print("  Save to {}...".format(out_file))
    with out_file.open('w', newline='') as f:
      writer = DictWriter(f
      , fieldnames=table[0].keys()
      , extrasaction='ignore')

      writer.writeheader()
      for line in table: writer.writerow(line)

  elif outputtype == 'json':
    print("  Save to {}...".format(out_file))
    with out_file.open('w') as f: json.dump(table, f)

  else:
    print('{} type unsupported'.format(outputtype))


def main():
  argparser = argparse.ArgumentParser()
  argparser.add_argument("-o", "--outputtype", help = "csv or json", default="csv")
  argparser.add_argument("-i", "--input", nargs='+', help = "input file(s)", default=["*.qfx"])
  args = argparser.parse_args()

  outputtype = args.outputtype
  for input in args.input:
    files = glob(input)
    for qfx_file in files:
      print("Reading {}...".format(qfx_file))
      qfx = OfxParser.parse(open(qfx_file, encoding="latin-1"))
      statement = get_statement_from_qfx(qfx)
      save_files(statement, outputtype, Path(qfx_file).with_suffix('.' + outputtype))
  
      positions = get_positions_from_qfx(qfx)
      save_files(positions, outputtype, Path(qfx_file).with_suffix('.positions.' + outputtype))

main()
