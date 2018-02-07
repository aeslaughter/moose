import re

from moosedown.base import components
from moosedown.tree import tokens
from moosedown.tree.base import Property

def make_extension(**kwargs):
    return KatexExtension(**kwargs)

class TexEquation(tokens.Token):
    PROPERTIES = tokens.Token.PROPERTIES + [Property('tex', required=True, ptype=unicode)]
    pass

class KatexExtension(components.Extension):
    def extend(self, reader, renderer):
        reader.addBlock(KatexBlockEquation(), location='>Code')

class KatexBlockEquation(components.TokenComponent):
    RE = re.compile(r'(?:\A|\n{2,})'         # start of string or empty line
                    r'^\\begin{equation}.*?^\\end{equation}' # tex
                    r'(?=\n\Z|\Z|\n{2,})',        # end of string or empty line
                    flags=re.DOTALL|re.MULTILINE|re.UNICODE)

    def createToken(self, info, parent):
        tex = TexEquation(parent, tex=info[0])
        return parent
