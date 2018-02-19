import codecs

def read(filename):
    with codecs.open(filename, encoding='utf-8') as fid:
        content = fid.read()
    return content
