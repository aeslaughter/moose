import bs4
import lxml

html = '<hr><p>foo is not a <code>bar</code>, or is it a <a src="http://somelink.org">link</a>?</p>'
soup = bs4.BeautifulSoup(html, 'lxml')

for child in soup.descendants:
    if child.name == 'p':
        child.name = 'command'
        child.attrs = {'cmd':'par', 'suffix':'\n'}
    elif child.name == 'code':
        child.name = 'command'
        child.attrs = {'cmd':'texttt'}
        child.string.wrap(soup.new_tag('curly'))

    elif child.name == 'a':
        child.name = 'command'
        child.attrs['cmd'] = 'href'
        child.string.wrap(soup.new_tag('curly'))

        c0 = soup.new_tag('curly')
        c0.string = child['src']
        child.insert(0, c0)
        print child
    #elif child.name == None:
    #    child.name = 'string'

    #print child, type(child), child.name

def process(tag):
    if tag.name == 'command':
        yield "%s\\%s%s" % (tag.get('prefix', ''), tag['cmd'], tag.get('suffix', ''))
    elif tag.name == 'environment':
        yield "\\begin{%s}\n" % tag['cmd']
    elif tag.name == 'curly':
        yield "{"
    elif tag.name == 'square':
        yield "["
    elif tag.name == None:
        yield unicode(tag).strip('\n')

    if isinstance(tag, bs4.element.Tag):
        for child in tag.children:
            for p in process(child):
                yield p

    if tag.name == 'environment':
        yield "\n\\end{%s}" % tag['cmd']
    elif tag.name == 'curly':
        yield "}"
    elif tag.name == 'square':
        yield "]"


print soup.prettify()

print '-------------------'

print ''.join(process(soup))
