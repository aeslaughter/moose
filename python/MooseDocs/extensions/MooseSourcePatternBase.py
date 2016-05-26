from markdown.inlinepatterns import Pattern

class MooseSourcePatternBase(Pattern):
    def __init__(self, regex):
        Pattern.__init__(self, regex)
        #super(Pattern, self).__init__(regex) # This fails

        # The default settings
        self._settings = {'strip_header':True,
                          'github_link':True,
                          'overflow-y':'visible',
                          'max-height':'500px',
                          'strip-extra-newlines':False}

    def updateSettings(self, settings):
        """
        Apply the settings captured from the regular expression.

        Args:
            settings[str]: A string containing the space separate key, value pairs (key=value key2=value2).
        """
        for s in settings.split(' '):
            if s:
                k, v = s.strip().split('=')
                if k not in self._settings:
                    #@TODO: Log this
                    print 'Unknown setting', k
                    continue
                try:
                    self._settings[k] = eval(v)
                except:
                    self._settings[k] = str(v)


    def style(self, *keys):
        """
        Extract the html style string from a list of settings.

        Args:
            *keys[str]: A list of keys to compose into a style string.
        """
        style = []
        for k in keys:
            style.append('{}:{}'.format(k, self._settings[k]))
        return ';'.join(style)
