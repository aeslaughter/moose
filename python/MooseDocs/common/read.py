import codecs
import re
import os

def read(filename):
    with codecs.open(filename, encoding='utf-8') as fid:
        content = fid.read()

    if filename.endswith(('.h', '.C')):
        content = re.sub(r'^//\*', '//', content, flags=re.MULTILINE|re.UNICODE)

    return content

def get_language(filename):
    _, ext = os.path.splitext(filename)
    if ext in ['.C', '.h', '.cpp', '.hpp']:
        return u'cpp'
    elif ext == '.py':
        return u'python'
    return u'text'
