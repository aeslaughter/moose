import re
import copy

SETTINGS_RE = re.compile(r'(?P<key>[^\s=]+)=(?P<value>.*?)(?=(?:\s[^\s=]+=|$))')

def parse_settings(defaults, raw):
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
