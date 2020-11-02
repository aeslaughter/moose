#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

#import os
#import uuid
import logging
#import json
import moosetree
#from . import common
from ..base import renderers, Extension
#from ..common import exceptions, write
from ..tree import html
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

    def extend(self, reader, renderer):
        self.requires(core, appsyntax)

        if isinstance(renderer, renderers.MaterializeRenderer):
            renderer.addCSS('accordion', "contrib/accordion/accordion.css")
            renderer.addJavaScript('accordion', "contrib/accordion/accordion.js")

    def postRender(self, page, result):
        footer = moosetree.find(result.root, lambda n: 'moose-content' in n['class'])

        div = html.Tag(footer, 'div', id_='accordion')

        ul = html.Tag(div, 'ul')
        li = html.Tag(ul, 'li')
        h = html.Tag(li, 'h3')
        html.Tag(h, 'a', href='#', string='Dashboard')

        ul = html.Tag(li, 'ul')
        li =  html.Tag(ul, 'li')
        html.Tag(li, 'a', href='#', string='Reports')
        html.Tag(li, 'a', href='#', string='Search')



        #html.Tag(li, 'a', href='#', string='Item 1')

        #ul2 = html.Tag(li)
        #li2 = html.Tag(ul2, 'li')
        #html.Tag(li2, 'a', href='#', string='Item 1.1')
