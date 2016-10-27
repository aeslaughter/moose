import os
import sys
import glob
import re
import livereload
import logging
import shutil
import MooseDocs
import build
log = logging.getLogger(__name__)


"""
def _livereload(host, port, config, builder, site_dir):

    server = livereload.Server()

    # Watch the documentation files, the config file and the theme files.
    server.watch(config['docs_dir'], builder)
    server.watch(config['config_file_path'], builder)

    for d in config['theme_dir']:
        server.watch(d, builder)

    server.serve(root=site_dir, host=host, port=int(port), restart_delay=0)
"""


def serve_options(parser, subparser):
  """
  Command-line options for serve command.
  """

  serve_parser = subparser.add_parser('serve', help='Generate and Sever the documentation using a local server.')
  return serve_parser

def serve(config_file='moosedocs.yml'):
  """
  Create live server
  """

  # Location of serve site
  tempdir = os.path.abspath(os.path.join(os.getenv('HOME'), '.local', 'share', 'moose', 'site'))

  # Clean the "temp" directory (if desired)
  if os.path.exists(tempdir):
    log.info('Cleaning build directory: {}'.format(tempdir))
    shutil.rmtree(tempdir)

  # Create the "temp" directory
  if not os.path.exists(tempdir):
    os.makedirs(tempdir)

  def builder(**kwargs):
    pass

  # Perform the initial build
  log.info("Building documentation...")
  config = build.build(config_file=config_file)#, site_dir=tempdir)


  server = livereload.Server()
  server.watch('content', builder)
  server.serve(root=tempdir, host='127.0.0.1', port='8000', restart_delay=0)
