import markdown

class MooseMarkdownExtension(markdown.Extension):
    """
    A wrapper class to define a static method for extracting the default configure options.

    This is need so that the default options can be displayed via a table using the devel extension
    without getting the configuration settings actually being used.
    """

    @staticmethod
    def defaultConfig():
        return dict()

    def __init__(self, *args, **kwargs):
        self.config = self.defaultConfig()
        super(MooseMarkdownExtension, self).__init__(*args, **kwargs)
