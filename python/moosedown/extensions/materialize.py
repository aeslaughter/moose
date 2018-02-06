"""
Tools for using features of the materialize framework (e.g., tabs, cards).
"""

"""TABS extension"""
# Card, CardContent, CardTabs, Modal
class Card(tokens.Token):
    pass

class CardTabs(tokens.Token):
    pass

class CardContent(tokens.Token):
    pass

class Caption(tokens.Token):
    pass


class Tabs(tokens.Token):
    pass
class Tab(tokens.Token):
    PROPERTIES = [Property("title", ptype=unicode, required=True)]
class TabContent(tokens.Token):
    pass

class Modal(tokens.Token):
    pass

"""Materialize extension"""
class Row(tokens.Token):
    pass
class Column(tokens.Token):
    pass


        """
        example = tokens.Float(parent, label="example", caption=self.settings['caption'], **self.attributes )
        tabs = Tabs(example)

        #print match.group('content')
        content = match.group('content').split('~~~')
        #print repr(content)

        md = Tab(tabs, title=u'MooseDown')
        tokens.Code(TabContent(md), code=content[0], language=u'markdown')

        html = Tab(tabs, title=u'HTML')
        tokens.Code(TabContent(html), code=content[1], language=u'html')

        rendered = Tab(tabs, title=u'HTML (Rendered)')
        root = TabContent(rendered, class_="moose-html-rendered-tab")
        root = self.reader.parse(content[0], root)

        tex = Tab(tabs, title=u'Latex')
        tokens.Code(TabContent(tex), code=content[2], language=u'latex')
        """

        """
        # TODO: this is for tabs
        #regex = r'~{3}(?P<title>.*?)(?:\s+(?P<settings>.*?))?$(?P<content>.*?)(?=^~|\Z)'

        for i, match in enumerate(re.finditer(regex, content, flags=re.MULTILINE|re.DOTALL)):
            settings, _ = common.parse_settings(defaults, match.group('settings'))
            #id_ = uuid.uuid4()

            if i == 0:
                tab = Tab(left, title=match.group('title'))
            else:
                tab = Tab(right, title=match.group('title'))

            content = TabContent(tab)
            code = tokens.Code(content, code=match.group('content'), language=settings['language'])
        """


class RenderRow(components.RenderComponent):
    def createHTML(self, token, parent):
        return html.Tag(parent, 'div', class_="row")#, **token.attributes)

class RenderColumn(components.RenderComponent):
    def createHTML(self, token, parent):
        return html.Tag(parent, 'div', class_="col s12 m12 l4")#, **token.attributes)

class RenderCard(components.RenderComponent):
    def createMaterialize(self, token, parent):
        return html.Tag(parent, 'div', class_="card")

class RenderCardTabs(components.RenderComponent):
    def createMaterialize(self, token, parent):
        return html.Tag(parent, 'div', class_="card-tabs")

class RenderCardContent(components.RenderComponent):
    def createMaterialize(self, token, parent):
        return html.Tag(parent, 'div', class_="card-content")

class RenderTabs(components.RenderComponent):

    def createHTML(self, token, parent):
        #row = html.Tag(parent, 'div', class_="row", **token.attributes)
        #col = html.Tag(row, 'div', class_="col s12 m6")
        return html.Tag(parent, 'ul', class_="tabs")

#    def createMaterialize(self, token, parent):
#        return self.createHTML(token, parent)
        #for child in token:
        #    li = html.Tag(ul, 'li', class_="tab")
        #    a = html.Tag(li, 'a', href='#' + str(child['id']))
        #    html.String(a, content=child.title, escape=True)

    def createLatex(self, token, parent):
        pass
        #TODO: do something
        #return latex.Environment(parent, 'UNKNOWN')

class RenderTab(components.RenderComponent):
    def createHTML(self, token, parent):
        li = html.Tag(parent, 'li', class_="tab")
        a = html.Tag(li, 'a', href='#{}'.format(uuid.uuid4()))
        html.String(a, content=token.title)
        return li

    #def createMaterialize(self, token, parent):
    #    return self.createHTML(token, parent)

class RenderTabContent(components.RenderComponent):
    def createHTML(self, token, parent):
        a = parent.find('a')
        return html.Tag(parent.parent.parent, 'div', id_=a['href'].strip('#'), **token.attributes)

    #def createMaterialize(self, token, parent):
    #    return self.createHTML(token, parent)
