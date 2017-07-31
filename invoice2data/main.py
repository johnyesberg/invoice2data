#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import shutil
import os
from os.path import join
import pkg_resources
# import invoice2data.in_pdftotext as pdftotext
# from invoice2data.template import read_templates
# from invoice2data.out_csv import invoices_to_csv
import in_pdftotext as pdftotext
from template import read_templates
from out_csv import invoices_to_csv, write_issuer_invoices
import logging

logger = logging.getLogger(__name__)

FILENAME = "{date} {desc}.pdf"
UTF_CHAR_MAP = {u'\u2212': '-' } #FIXME: OBT


def _replace_special_chars(text, character_map=UTF_CHAR_MAP):
    """ Replace strange utf-8 charecters with known charecters

    Args:
        text (str): a block ot text

    Returns:
        text (str): a block ot text

    """
    for key, val in character_map.iteritems():
        text = text.replace(key, val)
    return text


def extract_data(invoicefile, templates=None, debug=False):
    """
    Args:
        invoicefile (str): a path to an invoice file

    Returns:


    """
    if templates is None:
        templates = read_templates(
            pkg_resources.resource_filename('invoice2data', 'templates'))

    extracted_str = pdftotext.to_text(invoicefile).decode('utf-8')
    extracted_str = _replace_special_chars(extracted_str) #FIXME: OBT

    charcount = len(extracted_str)
    logger.debug('number of char in pdf2text extract: %d', charcount)
    # Disable Tesseract for now.
    #if charcount < 40:
        #logger.info('Starting OCR')
        #extracted_str = image_to_text.to_text(invoicefile)
    logger.debug('START pdftotext result ===========================')
    logger.debug(extracted_str)
    logger.debug('END pdftotext result =============================')

    logger.debug('Testing {} template files'.format(len(templates)))
    for t in templates:
        optimized_str = t.prepare_input(extracted_str)

        if t.matches_input(optimized_str):
            return t.extract(optimized_str)

    logger.error('No template for %s', invoicefile)
    return False

def main():
    "Take folder or single file and analyze each."

    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('--debug', dest='debug', action='store_true',
                        help='Print debug information.')

    parser.add_argument('--copy', '-c', dest='copy',
                        help='Copy renamed PDFs to specified folder.')

    parser.add_argument('--template-folder', '-t', dest='template_folder',
                        help='Folder containing invoice templates in yml file. Always adds built-in templates.')

    parser.add_argument('--exclude-built-in-templates', dest='exclude_built_in_templates',
                        default=False, help='Ignore built-in templates.', action="store_true")

    parser.add_argument('--report-per-vendor', dest='report_per_vendor',
                        default=False, help='Generates a seperate report for each vendor.', action="store_true")

    parser.add_argument('input_files', type=argparse.FileType('r'), nargs='+',
                        help='File or directory to analyze.')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    templates = []

    # Load templates from external folder if set.
    if args.template_folder:
        templates += read_templates(os.path.abspath(args.template_folder))

    # Load internal templates, if not disabled.
    if not args.exclude_built_in_templates:
        templates += read_templates(pkg_resources.resource_filename('invoice2data', 'templates'))

    output = []
    out_per_issuer = dict()
    for f in args.input_files:
        logging.info("processing file %s" % f.name)
        pdf_title = pdftotext.get_document_title(f.name)
        logging.info("file title: %s" % pdf_title)
        res = extract_data(f.name, templates=templates)
        res['title'] = pdf_title
        if res['issuer'] in out_per_issuer.keys():
            out_per_issuer[res['issuer']].append(res)
        else:
            out_per_issuer[res['issuer']] = [res]

        if res:
            logger.info(res)
            output.append(res)
            if args.copy:
                filename = FILENAME.format(
                    date=res['date'].strftime('%Y-%m-%d'),
                    desc=res['desc'])
                shutil.copyfile(f.name, join(args.copy, filename))

    if args.report_per_vendor:
        for issuer, invoices in out_per_issuer.iteritems():
            write_issuer_invoices(issuer, invoices)
    else:
        invoices_to_csv(output, 'invoices-output.csv')

if __name__ == '__main__':
    main()
