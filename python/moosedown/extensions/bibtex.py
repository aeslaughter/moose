"""
Extension for creating using BibTeX for references.
"""
import os
import re
import glob

from pybtex.database import parse_file, BibliographyData

import moosedown
from moosedown.base import components
from moosedown.tree import tokens, html
from moosedown.extensions import command

def make_extension(**kwargs):
    return BibtexExtension(**kwargs)

class BibtexExtension(command.CommandExtension):

    @staticmethod
    def defaultConfig():
        config = command.CommandExtension.defaultConfig()
        config['bib_files'] = ("docs/content/bib/moose.bib", "Space separated list of glob patterns that contain bib files.")
        return config

    def __init__(self, *args, **kwargs):
        command.CommandExtension.__init__(self, *args, **kwargs)

        self.__database = BibliographyData()

        bib_files = []
        for pattern in self['bib_files'].split():
            bib_files += glob.glob(os.path.join(moosedown.ROOT_DIR, pattern))

        for bfile in bib_files:
            db = parse_file(bfile)
            for key in db.entries: #TODO: https://bitbucket.org/pybtex-devs/pybtex/issues/93/databaseadd_entries-method-not-considering
                self.__database.add_entry(key, db.entries[key])

        #print self._database
        #TODO: reinit should re-build database if the files have changed


    @property
    def database(self):
        return self.__database.entries

    def extend(self, reader, renderer):
        self.requires(command)

        reader.addInline(BibtexReferenceComponent(), location='>Format')

        renderer.add(BibtexReference, RenderBibtexReference())

class BibtexReference(tokens.Token):
    PROPERTIES = [tokens.Property('keys', ptype=list, required=True),
                  tokens.Property('cite', ptype=unicode, default=u'cite')]

class BibtexReferenceComponent(components.TokenComponent):
    RE = re.compile(r'\['                          # open
                    r'(?P<cite>cite|citet|citep):' # cite prefix
                    r'(?P<keys>.*)'                # list of keys
                    r'(?:\s+(?P<settings>.*?))?'   # settings
                    r'\]',                         # closing ]
                    flags=re.UNICODE)

    def createToken(self, info, parent):
        keys = [key.strip() for key in info['keys'].split(',')]
        BibtexReference(parent, keys=keys, cite=info['cite'])
        return parent

class RenderBibtexReference(components.RenderComponent):

    def createHTML(self, token, parent):

        #TODO: move this author stuff to token???
        ul = html.Tag(parent, 'ul', class_='moose-cite-list')

        for key in token.keys:

            if key not in self.extension.database:
                msg = 'Unknown BibTex key: {}'
                raise exceptions.RenderException(msg, key)

            entry = self.extension.database[key]
            author_found = True
            if not 'author' in entry.persons.keys() and not 'Author' in entry.persons.keys():
                author_found = False
                entities = ['institution', 'organization']
                for entity in entities:
                    if entity in entry.fields.keys():
                        author_found = True
                        name = ''
                        for word in entry.fields[entity]:
                            if word[0].isupper():
                                name += word[0]
                        entry.persons['author'] = [Person(name)]

            if not author_found:
                msg = 'No author, institution, or organization for {}'
                raise exceptions.RenderException(msg, key)


            a = entry.persons['author']
            n = len(a)
            if n > 2:
                author = '{} et al.'.format(' '.join(a[0].last_names))
            elif n == 2:
                a0 = ' '.join(a[0].last_names)
                a1 = ' '.join(a[1].last_names)
                author = '{} and {}'.format(a0, a1)
            else:
                author = ' '.join(a[0].last_names)

            print author
            form = u'{}, {}' if token.cite == 'citep' else u'{} ({})'
            li = html.Tag(ul, 'li')
            html.Tag(li, 'a', href='#{}'.format(key), string=form.format(author, entry.fields['year']))


        return parent

    def createMaterialize(self, token, parent):
        self.createHTML(token, parent)
