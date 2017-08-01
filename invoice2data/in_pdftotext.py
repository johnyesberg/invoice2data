# -*- coding: utf-8 -*-
import subprocess
import logging as logger
import shutil
from distutils import spawn #py2 compat
from PyPDF2 import PdfFileReader


def to_text(path):
    """
    Wrapper around Poppler pdftotext.
    """

    if spawn.find_executable("pdftotext"): #shutil.which('pdftotext'):
        out, err = subprocess.Popen(
            ["pdftotext", '-layout', '-enc', 'UTF-8', path, '-'],
            stdout=subprocess.PIPE).communicate()
        return out
    else:
        raise EnvironmentError('pdftotext not installed. Can be downloaded from https://poppler.freedesktop.org/')


def document_metadata(filepath):
    """ Extract the file metadata

    Args:
        filepath (str): a path to the PDF file

    Returns:
        dict: The elements of the PDF's metadata
    """
    pdf_toread = PdfFileReader(open(filepath, "rb"))
    return pdf_toread.getDocumentInfo()


def get_document_title(filepath):
    """ Extract the file title from the metadata

    Args:
        filepath (str): a path to the PDF file

    Returns:
        str: title of the file
    """
    return document_metadata(filepath)['/Title']
