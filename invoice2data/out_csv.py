import csv

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


def write_issuer_invoices(issuer, invoices):
    """
    Args:
        issuer (str): name of the issuer
        invoices (list[dict]): list of the the invoices to be written into a single file
    """
    pass
    # assert False, "Not implemented"
    #
    # loging.info("Writing output summary for %s " % issuer)

    # for  in invoices.iteritems():
    #     pass
