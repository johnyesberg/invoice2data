import logging

import csv
import pandas as pd

from utils import remove_empty_lines


def invoices_to_csv(data, path):
    """ Writes  a CSV file with date, desc, and amount only

    Agrs:
        data (dict): key value pair from parsing the pdf
        path (str): a path for the output CSV file

    """
    with open(path, "w") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')

        writer.writerow(['date', 'desc', 'amount'])
        for line in data:
            writer.writerow([
                line['date'].strftime('%d/%m/%Y'),
                line['desc'],
                line['amount']])


def write_issuer_invoices(issuer, invoices, encoding):
    """
    Args:
        issuer (str): name of the issuer
        invoices (list[dict]): list of the the invoices to be written into a single file
        encoding (str): text encoding
    """

    # if there are 'lines' we look for the union of the fields names
    has_lines = False
    for invoice in invoices:
         if 'lines' in invoice:
             logging.info("lines is in invoice")
             has_lines = True
             break

    rows = []
    for invoice in invoices:
        invoice.pop("desc")
        if has_lines:
            lines = remove_empty_lines(invoice.pop("lines"))
            for line in lines:
                full_line = invoice.copy()
                full_line.update(line)
                rows.append(full_line)
        else:
            rows.append(invoice)


    out_filename = (issuer + "_summary.csv").replace(' ', '_')
    logging.info("Writing output summary for %s into %s" % (issuer, out_filename))
    summary = pd.DataFrame(rows).set_index(['title', 'invoice_number'])
    if encoding == 'ASCII7':
        encoding = 'ascii'
    summary.to_csv(out_filename, index=True, encoding=encoding)
