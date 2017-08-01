"""
Keep helper functions not related to specific module.
"""

import logging

import yaml
from collections import OrderedDict

# borrowed from http://stackoverflow.com/a/21912744
def ordered_load(
        stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict
):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)

    return yaml.load(stream, OrderedLoader)


def remove_empty_lines(lines):
    """ Remove lines with no data

    Args:
        lines (list(dict)): All the lines extracted from the invoice

    Returns:
        list[dict]: the lines without the empty lines
    """

    _lines = []
    for line in lines:
        if line and any(line.values()): # keep only non-empty lines
            _lines.append(line)
    return _lines
