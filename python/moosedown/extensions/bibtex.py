"""
Extension for creating using BibTeX for references.
"""
import glob

import pybtex

from moosedown.extensions import command

def make_extension(**kwargs):
    return BibtexExtension(**kwargs)

class BibtexExtension(command.CommandExtension):

    @staticmethod
    def defaultConfig():
        config = command.CommandExtension.defaultConfig()
        config['bib_files'] = ("docs/content/bib/*.bib", "Space separated list of glob patterns that contain bib files.")
        return config

    def __init__(self, *args, **kwargs):
        command.CommandExtension.__init__(self, *args, **kwargs)

        bib_files = []
        for pattern in self['bib_files'].split():
            bib_files += glob.glob(pattern)

        print bib_files



    def extend(self, reader, renderer):
        self.requires(command)


       # self.addCommand(BibtexCommand())
