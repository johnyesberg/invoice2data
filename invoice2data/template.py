"""
This module abstracts templates for invoice providers.

Templates are initially read from .yml files and then kept as class.
"""

import yaml
import os
import re
import dateparser
from unidecode import unidecode
import unicode
import logging as logger
from collections import OrderedDict

# from invoice2data.utils import ordered_load
from utils import ordered_load

OPTIONS_DEFAULT = {
    'remove_whitespace': False,
    'remove_accents': False,
    'lowercase': False,
    'currency': 'EUR',
    'date_formats': [],
    'languages': [],
    'decimal_separator': '.',
    'replace': [],  # example: see templates/fr/fr.free.mobile.yml
    'field_separator': r'\s+',
    'line_separator': r'\n',
    'append_separator': ' '
}

def read_templates(folder):
    """
    Load yaml templates from template folder. Return list of dicts.
    """
    output = []
    for path, subdirs, files in os.walk(folder):
        for name in sorted(files):
            if name.endswith('.yml'):
                tpl = ordered_load(open(os.path.join(path, name)).read())
                tpl['template_name'] = name

                # Test if all required fields are in template:
                assert 'keywords' in tpl.keys(), 'Missing keywords field.'
                required_fields = ['date', 'amount', 'invoice_number']
                assert len(set(required_fields).intersection(tpl['fields'].keys())) == len(required_fields), \
                    'Missing required key in template {} {}. Found {}'.format(name, path, tpl['fields'].keys())

                # Keywords as list, if only one.
                if type(tpl['keywords']) is not list:
                    tpl['keywords'] = [tpl['keywords']]

                if 'lines' in tpl:
                    assert 'start' in tpl['lines'], 'Lines start regex missing'
                    assert 'end' in tpl['lines'], 'Lines end regex missing'
                    assert 'line' in tpl['lines'], 'Line regex missing'

                output.append(InvoiceTemplate(tpl))
    return output


class InvoiceTemplate(OrderedDict):
    """
    Represents single template files that live as .yml files on the disk.
    """

    def __init__(self, *args, **kwargs):
        super(InvoiceTemplate, self).__init__(*args, **kwargs)

        # Merge template-specific options with defaults
        self.options = OPTIONS_DEFAULT.copy()

        for lang in self.options['languages']:
            assert len(lang) == 2, 'lang code must have 2 letters'

        if 'options' in self:
            self.options.update(self['options'])

        # Set issuer, if it doesn't exist.
        if 'issuer' not in self.keys():
            self['issuer'] = self['keywords'][0]

    def prepare_input(self, extracted_str):
        """
        Input raw string and do transformations, as set in template file.
        """

        # Remove withspace
        if self.options['remove_whitespace']:
            optimized_str = re.sub(' +', '', extracted_str)
        else:
            optimized_str = extracted_str

        # Remove accents
        if self.options['remove_accents']:
            optimized_str = unicode.asciify(optimized_str)

        # convert to lower case
        if self.options['lowercase']:
            optimized_str = optimized_str.lower()

        # specific replace
        for replace in self.options['replace']:
            assert len(replace) == 2, 'A replace should be a list of 2 items'
            optimized_str = optimized_str.replace(replace[0], replace[1])

        return optimized_str

    def matches_input(self, optimized_str):
        """See if string matches keywords set in template file"""

        if all([keyword in optimized_str for keyword in self['keywords']]):
            logger.info('Matched template %s', self['template_name'])
            return True

        if all([re.search(k,optimized_str) for k in self['keywords']]):
            logger.info('Matched template %s', self['template_name'])
            return True

    def parse_number(self, value):
        assert value.count(self.options['decimal_separator']) < 2,\
            'Decimal separator cannot be present several times'
        # remove dollar sign if it's there
        value = value.replace('$','')
        # replace decimal separator by a |
        amount_pipe = value.replace(self.options['decimal_separator'], '|')
        # remove all possible thousands separators
        amount_pipe_no_thousand_sep = re.sub(
            '[.,\s]', '', amount_pipe)
        # put dot as decimal sep
        return float(amount_pipe_no_thousand_sep.replace('|', '.'))

    def coerce_type(self, value, target_type):
        if target_type == 'int':
            if not value.strip():
                return 0
            return int(self.parse_number(value))
        elif target_type == 'float':
            if not value.strip():
                return 0.0
            return float(self.parse_number(value))
        assert False, 'Unknown type'

    def extract(self, optimized_str):
        """
        Given a template file and a string, extract matching data fields.
        """

        logger.debug('START optimized_str ========================')
        logger.debug(optimized_str)
        logger.debug('END optimized_str ==========================')
        logger.debug(
            'Date parsing: languages=%s date_formats=%s',
            self.options['languages'], self.options['date_formats'])
        logger.debug('Float parsing: decimal separator=%s', self.options['decimal_separator'])
        logger.debug("keywords=%s", self['keywords'])
        logger.debug(self.options)

        # Try to find data for each field.
        output = {}
        output['issuer'] = self['issuer']

        for k, v in self['fields'].items():
            if k.startswith('static_'):
                logger.debug("field=%s | static value=%s", k, v)
                output[k.replace('static_', '')] = v
            else:
                logger.debug("field=%s | regexp=%s", k, v)

                # Fields can have multiple expressions
                if type(v) is list:
                    for v_option in v:
                        res_find = re.findall(v_option, optimized_str, re.DOTALL)
                        if res_find:
                            break
                else:
                    res_find = re.findall(v, optimized_str, re.DOTALL)
                if res_find:
                    logger.debug("res_find=%s", res_find)
                    if k.startswith('date'):
                        raw_date = res_find[0]
                        output[k] = dateparser.parse(
                            raw_date, date_formats=self.options['date_formats'],
                            languages=self.options['languages'])
                        logger.debug("result of date parsing=%s", output[k])
                        if not output[k]:
                            logger.error(
                                "Date parsing failed on date '%s'", raw_date)
                            return None
                    elif k.startswith('amount'):
                        output[k] = self.parse_number(res_find[0])
                    else:
                        output[k] = res_find[0]
                else:
                    logger.warning("regexp for field %s didn't match", k)

        if 'lines' in self:
            self.extract_lines(optimized_str, output)

        output['currency'] = self.options['currency']

        if True: #len(output.keys()) >= 5:
            try:
                output['desc'] = 'Invoice %s from %s' % (
                    output['invoice_number'], self['issuer'])
                logger.debug(output)
                return output
            except KeyError as err:
                logger.warning("Failed to process file: %s" % err)
                return output
        else:
            logger.error("Only %s keys in output: %s" % (len(output.keys()), output.keys()) )
            return None

    def extract_lines(self, content, output):
        """Try to extract lines from the invoice"""
        start = re.search(self['lines']['start'], content)
        if start==None:
            logger.warn("Could not match 'start' line.")
            return
        end = re.search(self['lines']['end'], content[start.end():])
        if end==None:
            logger.warn("Could not match 'end' line.")
            return
        _end_start = end.start() + start.end()
        if not start or not end:
            logger.warning('no lines found - start %s, end %s', start, end)
            return
        content = content[start.end():_end_start]
        content_lines = re.split(self.options['line_separator'], content)
        logger.info("content has %s characters and %s lines" % (len(content),len(content_lines)))
        lines = []
        current_row = {}
        separator = self.options['append_separator']
        if separator == 'newline':
            separator = '\n'
        for line in content_lines:
            logger.debug('Lines[ ]: %s', line)
            if "ignore_line" in self['lines']:
                match = re.search(self['lines']['ignore_line'], line)
                if match:
                    logger.debug("Lines[ignore]: %s",line)
                    continue
            if 'first_line' in self['lines']:
                match = re.search(self['lines']['first_line'], line)
                if match:
                    logger.debug("Lines[first]: %s",line)
                    if current_row:
                        lines.append(current_row)
                    current_row = {
                        field: value.strip()
                        for field, value in match.groupdict().items()
                        if value != None
                    }
                    continue
            if 'last_line' in self['lines']:
                match = re.search(self['lines']['last_line'], line)
                if match:
                    logger.debug("Lines[last]: %s",line)
                    for field, value in match.groupdict().items():
                        try:
                            value = value.strip()
                        except AttributeError as err:
                            logger.warning("Couldn't find value for %s: %s" % (field, err))
                            value = ''
                        current_row[field] = '%s%s%s' % (
                            current_row.get(field, ''),
                            current_row.get(field, '') and separator or '',
                            value
                            )
                    lines.append(current_row)
                    current_row = {}
                    continue
            match = re.search(self['lines']['line'], line)
            if match:
                logger.debug("Lines[line]: %s",line)
                for field, value in match.groupdict().items():
                    try:
                        value = value.strip()
                    except AttributeError as err:
                        logger.warning("Couldn't find value for %s: %s" % (field, err))
                        value = ''
                    current_row[field] = '%s%s%s' % (
                        current_row.get(field, ''),
                        current_row.get(field, '') and separator or '',
                        value
                        )
                continue
            logger.debug(
                'ignoring "%s" because it doesn\'t match anything', line
            )
        if current_row:
            lines.append(current_row)

        types = self['lines'].get('types', [])
        for row in lines:
            for name in row.keys():
                if name in types:
                    row[name] = self.coerce_type(row[name], types[name])

        if lines:
            output['lines'] = lines
