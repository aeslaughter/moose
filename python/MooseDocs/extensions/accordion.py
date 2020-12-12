#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

import os
import multiprocessing
#import uuid
import logging
#import json
import moosetree
#from . import common
from ..base import renderers, Extension
#from ..common import exceptions, write
from ..tree import html, pages, tokens
from . import core, appsyntax

LOG = logging.getLogger(__name__)

def make_extension(**kwargs):
    return AccordionExtension(**kwargs)

class AccordionExtension(Extension):
    @staticmethod
    def defaultConfig():
        config = Extension.defaultConfig()
        return config

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__root = moosetree.Node(None, '')

        self.__manager = multiprocessing.Manager()
        self.__headings = self.__manager.dict()

    def extend(self, reader, renderer):
        self.requires(core, appsyntax)

        if isinstance(renderer, renderers.MaterializeRenderer):
            renderer.addCSS('accordion', "contrib/accordion/accordion.css")
            renderer.addJavaScript('accordion', "contrib/accordion/accordion.js")

    def rpath(self, page):
        return os.path.relpath(page.destination, page.base)


    def preExecute(self):
        """

        """
        def create_node(node, *args):
            path = ''
            for arg in args:
                path = os.path.join(path, arg)
                func = lambda n: n.name == arg
                node = moosetree.search.find(node, func , method=moosetree.search.IterMethod.CHILDREN) or moosetree.Node(node, arg, path=path)
            return node

        items = [page for page in self.translator.getPages() if isinstance(page, pages.Source)]
        for item in items:
            path = self.rpath(item).split(os.path.sep)
            if os.path.splitext(path[-1])[0] == 'index':
                node = create_node(self.__root, *path[:-1])
                node['index'] = True
            else:
                node = create_node(self.__root, *path)
            node['uid'] = item.uid

       # print(self.__root)

    def postTokenize(self, page, ast):

        def copy_children(n):
            tok = tokens.Token('', None)
            for c in n:
                c.copy(tok)
            return tok


        h1 = moosetree.find(ast, lambda n: n.name == 'Heading' and n['level'] == 1)
        h1 = copy_children(h1) if h1 else None

        h2 = moosetree.findall(ast, lambda n: n.name == 'Heading' and n['level'] == 2)
        h2 = [(copy_children(n), n.get('id', None)) for n in h2] if h2 else None

        self.__headings[page.uid] = (h1, h2)

    def postRender(self, page, result):


        path = os.path.relpath(page.destination, page.base)

        parent = moosetree.find(result.root, lambda n: n.name == 'header')
        div = html.Tag(parent, 'div', id_='accordion')
        ul = html.Tag(None, 'ul', id_='nav-mobile', class_="sidenav sidenav-fixed", style="transform:translateX(0%);")

        def add_list_items(ul, children):
            for child in children:
                li = html.Tag(ul, 'li')
                if child.children:
                    html.Tag(li, 'a', href='#', string=child.name)
                    add_list_items(html.Tag(li, 'ul'), child.children)
                else:
                    rpath = os.path.relpath(child['path'], os.path.dirname(path))
                    a = html.Tag(li, 'a', href=rpath)
                    h1, h2 = self.__headings.get(child['uid'], (None, None))
                    if h1:
                        self.translator.renderer.render(a, h1, page)
                    else:
                        html.String(a, content=child.name)

                    if h2:
                        page_ul = html.Tag(li, 'ul')
                        for h in h2:
                            page_li = html.Tag(page_ul, 'li')
                            html.Tag(page_li, 'a', href='#{}'.format(h[1]))
                            self.translator.renderer.render(page_li, h[0], page)

                if child.get('uid', None) == page.uid:
                    for n in li.path:
                        n.addClass('active')




        add_list_items(ul, self.__root)


        ul.parent = div





        #print(div)







        #div = html.Tag(footer, 'div', id_='accordion')

        #ul = html.Tag(div, 'ul')
        #li = html.Tag(ul, 'li')
        #h = html.Tag(li, 'h3')
        #html.Tag(h, 'a', href='#', string='Dashboard')

        #ul = html.Tag(li, 'ul')
        #li =  html.Tag(ul, 'li')
        #html.Tag(li, 'a', href='#', string='Reports')
        #html.Tag(li, 'a', href='#', string='Search')



        #html.Tag(li, 'a', href='#', string='Item 1')

        #ul2 = html.Tag(li)
        #li2 = html.Tag(ul2, 'li')
        #html.Tag(li2, 'a', href='#', string='Item 1.1')
