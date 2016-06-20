#!/usr/bin/env python
import os
import utils
import logging
import MooseDocs
import inspect

class MkMooseDocsFormatter(logging.Formatter):

    COLOR = {'DEBUG':'GREEN', 'INFO':'RESET', 'WARNING':'YELLOW', 'ERROR':'RED', 'CRITICAL':'MAGENTA'}

    def format(self, record):
        return logging.Formatter.format(self, record)

        """
        stack = inspect.stack()
        the_class = stack[1][0].f_locals["self"].__class__
        the_method = stack[1][0].f_code.co_name
        print("  I was called by {}.{}()".format(str(the_class), the_method))

        msg = logging.Formatter.format(self, record)

        indent = record.name.count('.')

        if record.levelname in ['WARNING', 'ERROR', 'CRITICAL']:
            msg = '{}{}: {}'.format(' '*4*indent, record.levelname, msg)
        else:
            msg = '{}{}'.format(' '*4*indent, msg)

        if record.levelname in self.COLOR:
            msg = utils.colorText(msg, self.COLOR[record.levelname])

        return msg
        """



if __name__ == '__main__':

    import livereload



    # Setup the logger object
    logging.basicConfig(level=logging.INFO)

    """
    log = logging.getLogger('MooseDocs')
    formatter = MkMooseDocsFormatter()#'%(name)s:%(levelname)s: %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    """
    #log.setLevel(logging.DEBUG)


    root = MooseDocs.MOOSE_DIR

    config_file = os.path.join('docs', 'mkdocs.yml')
    exe = utils.find_moose_executable(os.path.join(root, 'modules', 'phase_field'), name='phase_field')

    gen = MooseDocs.MooseApplicationDocGenerator(root, config_file, exe)
    gen()
