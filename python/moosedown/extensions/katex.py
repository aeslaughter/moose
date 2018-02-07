import re
import collections

from moosedown.base import components
from moosedown.tree import tokens, html
from moosedown.tree.base import Property

def make_extension(**kwargs):
    return KatexExtension(**kwargs)

class TexEquation(tokens.Token):
    PROPERTIES = tokens.Token.PROPERTIES + [Property('prefix', ptype=unicode, required=True),
                                            Property('tex', required=True, ptype=str),
                                            Property('number', ptype=int)] #set by constructor
    COUNTS = collections.defaultdict(int)

    def __init__(self, *args, **kwargs):
        tokens.Token.__init__(self, *args, **kwargs)

        TexEquation.COUNTS[self.prefix] += 1
        self.number = TexEquation.COUNTS[self.prefix]

class KatexExtension(components.Extension):
    @staticmethod
    def defaultConfig():
        config = components.Extension.defaultConfig()
        config['prefix'] = ('Eq.', "The prefix to used when refering to an equation by " \
                                   "the \label content.")
        return config
    def extend(self, reader, renderer):
        reader.addBlock(KatexBlockEquation(), location='>Code')
        renderer.add(TexEquation, RenderTexEquation())

class KatexBlockEquation(components.TokenComponent):
    RE = re.compile(r'(?:\A|\n{2,})'                      # start of string or empty line
                    r'^\\begin{(?P<cmd>equation\*{0,1})}' # start equation block
                    r'(?P<equation>.*?)'                  # tex equation
                    r'^\\end{(?P=cmd)}'                   # end equation block
                    r'(?=\n\Z|\Z|\n{2,})',                # end of string or empty line
                    flags=re.DOTALL|re.MULTILINE|re.UNICODE)
    LABEL_RE = re.compile(r'\\label{(?P<id>.*?)}', flags=re.UNICODE)

    def reinit(self): #TODO: move this to core, with CountToken...???
        TexEquation.COUNTS.clear()

    def createToken(self, info, parent):
        prefix = self.extension['prefix']
        raw = r'{}'.format(info['equation']).strip('\n').replace('\n', ' ').encode('string-escape')

        tex = TexEquation(parent, tex=raw, prefix=unicode(prefix))

        is_numbered = not info['cmd'].endswith('*')

        label = self.LABEL_RE.search(info['equation'])
        if label and not is_numbered:
            msg = "TeX non-numbered equations (e.g., equations*) may not include a \\label, since" \
                  "it will not be possible to refer to the equation."
            raise exceptions.TokenizeException(msg)
        elif label:
            tex.tex = tex.tex.replace(label.group().encode('ascii'), '')
            tokens.Shortcut(parent.root, key=label.group('id'),
                                         link=u'#moose-katex-equation-{}'.format(tex.number),
                                         content=u'{} {}'.format(prefix, tex.number))

        return parent

class RenderTexEquation(components.RenderComponent):
    def createHTML(self, token, parent):
        div = html.Tag(parent, 'div', class_='moose-katex-block')

        if token.number is not None:
            eq_id = 'moose-katex-equation-{}'.format(token.number)
            html.Tag(div, 'div', class_='moose-katex-equation', id_=eq_id)
            num = html.Tag(div, 'div', class_='moose-katex-equation-number')
            html.String(num, content=u'({})'.format(token.number))

        else:
            html.Tag(div, 'div', class_='moose-katex-equation')

        script = html.Tag(div, 'script')
        content = u'var element = document.getElementById("%s");' % eq_id
        content += u'katex.render("%s", element, {displayMode:%s,throwOnError:false});' % (token.tex, 'true')
        html.String(script, content=content)

        return parent
    #def createMaterialize(self, token, parent):
    #    pass

    def createLatex(self, token, parent):
        pass
