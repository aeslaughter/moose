import os
import re
import copy
import bs4
import mooseutils
import logging
log = logging.getLogger(__name__)

class LatexNavigableString(bs4.element.NavigableString):
    pass

class Element(object):
    """
    Base class for converting html tag to latex.

    The basic conversion by changing the html tags to a "latex" tag and adding meta data to the tag
    attributes. See Translator for meta data use.

    Args:
        name[str]: (Required) The tag name to test against.
        attrs[dict]: (Optional) A dictionary of attributes and values that are required (see test())

    Kwargs (Optional):
        The following keywords are converted to tag meta data for latex conversion. The values passed in
        for each of the keywords should be a str type.

        begin --> data-latex-begin
            The command to place prior to content.
        begin_prefix --> data-latex-begin-prefix
            The text (e.g., '\n') that should be placed prior to the begin command.
        begin_suffix --> data-latex-begin-suffix
            The text (e.g., '\n') that should be placed after to the begin command.
        end --> data-latex-end
            The command to place after the content.
        end_prefix --> data-latex-end-prefix
            The text (e.g., '\n') that should be placed prior to the end command.
        end_suffix --> data-latex-end-suffix
            The text (e.g., '\n') that should be placed after to the end command.
        open -> data-latex-open
            Text placed prior to all begin commands and content.
        close -> data-latex-close
            Text placed after content and all end commands.
        content -> data-latex-content
            Text used to replace the content of the tag including children
    """
    def __init__(self, name=None, attrs=dict(), strip=False, **kwargs):

        if name == None:
            raise mooseutils.MooseException("The 'name' argument variable must be set.")

        self._name = name
        self._attrs = attrs
        self._strip = strip

        self._data = dict()
        keys = ['begin', 'begin_prefix', 'begin_suffix', 'end', 'end_prefix', 'end_suffix', 'open',
                'close', 'content', 'escape']
        for k in keys:
            self._data.setdefault('data-latex-{}'.format(k.replace('_', '-')), kwargs.get(k, None))
        self.__soup = None

    def __call__(self, soup, tag):
        self.__soup = soup
        if self.test(tag):
            self.convert(tag)
            tag.name = 'latex'

    def test(self, tag):

        if tag.name == 'latex':
            return False

        if not isinstance(tag, bs4.element.Tag) or tag.name != self._name:
            return False

        for key, value in self._attrs.iteritems():
            if (key not in tag.attrs) or (value not in tag[key]):
                return False

        return True

    def strip(self, tag):
        """
        Strip whitespace from string descendants: lstrip on first and rstrip on last.
        """
        strs = list(tag.strings)
        strs[0].replace_with(strs[0].lstrip())
        strs[-1].replace_with(strs[-1].rstrip())

    def convert(self, tag):
        tag.name = 'latex'
        for key, value in self._data.iteritems():
            if value is not None:
                tag.attrs.setdefault(key, value)
        if 'data-latex-content' in tag.attrs:
            tag.replace_with(self.new(string=LatexNavigableString(tag.attrs['data-latex-content'])))

        if self._strip:
            self.strip(tag)

    def new(self, name='latex', string=None):
        ntag = self.__soup.new_tag(name)
        if string:
            ntag.string = string
        return ntag

    def curly(self, **kwargs):
        ntag = self.new(**kwargs)
        ntag.attrs['data-latex-begin'] = '{'
        ntag.attrs['data-latex-end'] = '}'
        return ntag

    def square(self, **kwargs):
        ntag = self.new(**kwargs)
        ntag.attrs['data-latex-begin'] = '['
        ntag.attrs['data-latex-end'] = ']'
        return ntag

class Command(Element):
    def __init__(self, command=None, **kwargs):
        super(Command, self).__init__(**kwargs)

        self._command = command
        if self._command == None:
            raise mooseutils.MooseException("The 'command' argument variable must be set.")

        self._data['data-latex-begin'] = '\\{}'.format(self._command)

class ArgumentCommand(Command):
    def convert(self, tag):
        super(ArgumentCommand, self).convert(tag)
        new = self.curly()
        for child in reversed(tag.contents):
            new.insert(0, child.extract())
        tag.append(new)

class Environment(Command):
    def __init__(self, **kwargs):
        kwargs.setdefault('begin_suffix', '\n')
        kwargs.setdefault('end_prefix', '\n')
        super(Environment, self).__init__(**kwargs)
        self._data['data-latex-begin'] = '\\begin{%s}' % self._command
        self._data['data-latex-end'] = '\\end{%s}' % self._command

class Heading(Command):
    def convert(self, tag):
        super(Heading, self).convert(tag)
        id_ = tag.get('id', None)
        if id_:
            string = tag.string.wrap(self.curly())

            label = self.new()
            label['data-latex-begin'] = '\\label'
            string.append(label)

            text = self.curly()
            text.string = id_
            label.append(text)

        else:
            tag.string.wrap(self.curly())

class PreCode(Environment):
    def __init__(self, **kwargs):
        kwargs.setdefault('name', 'pre')
        kwargs.setdefault('command', 'verbatim')
        super(PreCode, self).__init__(**kwargs)
    def test(self, tag):
        return super(PreCode, self).test(tag) and (tag.code)
    def convert(self, tag):
        super(PreCode, self).convert(tag)
        tag.code.name = 'latex'

class Table(Environment):
    def __init__(self, **kwargs):
        kwargs.setdefault('command', 'tabular')
        super(Table, self).__init__(name='table', **kwargs)
    def convert(self, tag):
        super(Table, self).convert(tag)
        tag['data-latex-begin-suffix'] = ''
        cols = self.curly()
        cols.string = 'l'*self.numColumns(tag)
        cols['data-latex-close'] = '\n'
        tag.insert(0, cols)
    def numColumns(self, tag):
        return len(tag.tbody.find('tr').find_all('td'))

class TableHeaderFooter(Element):
    def convert(self, tag):
        super(TableHeaderFooter, self).convert(tag)
        tag['data-latex-open'] =  '\\hline\n'
        tag['data-latex-close'] = '\\hline'

class TableItem(Element):
    def convert(self, tag):
        super(TableItem, self).convert(tag)
        if tag.find_next_sibling(self._name):
            tag['data-latex-close'] =  ' & '
        else:
            tag['data-latex-close'] = ' \\\\'

class ListItem(Command):
    def __init__(self, **kwargs):
        super(ListItem, self).__init__(name='li', command='item', **kwargs)

    def convert(self, tag):
        super(ListItem, self).convert(tag)
        tag['data-latex-begin-suffix'] = ' '

        if tag.find_next_sibling(self._name):
            tag['data-latex-close'] = '\n'

class Image(ArgumentCommand):
    def __init__(self, **kwargs):
        kwargs.setdefault('end_suffix', '\n')
        super(Image, self).__init__(name='img', command='includegraphics', attrs={'src':''},  **kwargs)

    def convert(self, tag):
        tag.string = tag['src']
        super(Image, self).convert(tag)

        if not os.path.exists(tag.string):
            log.error('Image file does not exist: {}'.format(tag.string))

class Figure(Environment):
    def __init__(self, **kwargs):
        kwargs.setdefault('name', 'figure')
        kwargs.setdefault('command', 'figure')
        super(Figure, self).__init__(**kwargs)
    def convert(self, tag):
        super(Figure, self).convert(tag)

        if 'id' in tag.attrs:
            label = self.curly()
            label.attrs['data-latex-begin-prefix'] = '\\label'
            label.attrs['data-latex-end-suffix'] = '\n'
            label.string = tag.attrs['id']
            tag.insert(0, label)
        else:
            tag['data-latex-begin'] = '\\begin{%s*}' % self._command
            tag['data-latex-end'] = '\\end{%s*}' % self._command


class LinkElement(ArgumentCommand):
    def __init__(self, **kwargs):
        super(LinkElement, self).__init__(name='a', attrs={'href':''}, command='href', **kwargs)
    def convert(self, tag):
        super(LinkElement, self).convert(tag)
        url = self.curly()
        url.string = tag.get('href', '#')
        tag.insert(0, url)
