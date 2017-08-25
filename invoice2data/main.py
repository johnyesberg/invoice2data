#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from os.path import join

import argparse
import glob
import shutil
import pkg_resources

from invoice2data import in_pdftotext as pdftotext
from invoice2data.template import read_templates
from invoice2data.out_csv import invoices_to_csv, write_issuer_invoices

logger = logging.getLogger(__name__)

FILENAME = "{date} {desc}.pdf"


def extract_data(invoicefile, templates=None, debug=False, encoding='ASCII7'):
    """
    Args:
        invoicefile (str): a path to an invoice file

    Returns:


    """
    if templates is None:
        templates = read_templates(
            pkg_resources.resource_filename('invoice2data', 'templates'))

    extracted_str = pdftotext.to_text(invoicefile, encoding=encoding)
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
        logger.debug('Trying template {}'.format(t))
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

    parser.add_argument('--include-file-name', dest='include_file_name',
                    default=False, help='Write the file name of the quote in the report.', action="store_true")

    parser.add_argument('--report-per-vendor', dest='report_per_vendor',
                        default=False, help='Generates a seperate report for each vendor.', action="store_true")

    parser.add_argument('--encoding', dest='encoding',
                        default='ASCII7', help='Encoding of the text')

    parser.add_argument('--input_files', type=str, nargs='+',
                        help='Files to analyze.')

    parser.add_argument('--output-directory', type=str, default='.', dest='output_dir',
                        help='Out directory for the report files.')

    parser.add_argument('input_directory', help='Input directory with PDF files to analyze.')

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
    if args.input_files:
        files = args.input_files
    else:
        files = glob.iglob(args.input_directory + '/*.pdf')

    for file_name in files:
        logging.info("processing file %s" % file_name)
        res = extract_data(file_name, templates=templates, encoding=args.encoding)

        if res:
            if res['issuer'] in out_per_issuer.keys():
                out_per_issuer[res['issuer']].append(res)
            else:
                out_per_issuer[res['issuer']] = [res]

            if args.include_file_name:
                res['file_name'] = os.path.basename(file_name)

            try:
                pdf_title = pdftotext.get_document_title(file_name)
                logging.info("file title: %s" % pdf_title)
                res['title'] = pdf_title
            except KeyError:
                logging.info("%s doesn't have a title... using filename instaed" % file_name)
                res['title'] = file_name
            logger.info(res)
            output.append(res)
            if args.copy:
                filename = FILENAME.format(
                    date=res['date'].strftime('%Y-%m-%d'),
                    desc=res['desc'])
                shutil.copyfile(f.name, join(args.copy, filename))

    if args.report_per_vendor:
        for issuer, invoices in out_per_issuer.iteritems():
            write_issuer_invoices(issuer, invoices, args.encoding, args.output_dir)
    else:
        invoices_to_csv(output, os.path.join(args.output_dir, 'invoices-output.csv'))

if __name__ == '__main__':
    main()
