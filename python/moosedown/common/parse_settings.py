"""
Tools for parsing key value pairs from a raw string.
"""
import re
import copy

from exceptions import TokenizeException

SETTINGS_RE = re.compile(r'(?P<key>[^\s=]+)=(?P<value>.*?)(?=(?:\s[^\s=]+=|$))')

def match_settings(defaults, raw):
    """
    Parses a raw string for key, value pairs separated by an equal sign.

    Inputs:
        default[dict]: The default values for the known keys.
        raw[str]: The raw string to parse and inject into a dict().
    """
    known = dict((k,v[0]) for k,v in copy.deepcopy(defaults).iteritems())
    unknown = dict()

    if not raw:
        return known, unknown

    for match in SETTINGS_RE.finditer(raw):

        key = match.group('key').strip()
        value = match.group('value').strip()

        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value.lower() == 'none':
            value = None
        elif all([v.isdigit() for v in value]):
            value = float(value) #pylint: disable=redefined-variable-type

        if key in known:
            known[key] = value
        else:
            unknown[key] = value

    return known, unknown


def parse_settings(defaults, local):
    """

    """
    settings, unknown = match_settings(defaults, local)
    if unknown:
        msg = "The following key, value settings are unknown:"
        for key, value in unknown.iteritems():
            msg += '\n{}{}={}'.format(' '*4, key, repr(value))
        raise TokenizeException(msg) #TODO: TokenException

    return settings, unknown
