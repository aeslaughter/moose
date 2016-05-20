import re

class MarkdownTable(object):
    """
    A class for creating markdown tables from parameter data parsed from MOOSE yaml data.
    """

    PARAMETER_TABLE_COLUMNS = ['name', 'cpp_type', 'description']
    PARAMETER_TABLE_COLUMN_NAMES = ['Name', 'Type', 'Description']

    def __init__(self):

        self._parameters = []
        self._column_widths = []
        for col in self.PARAMETER_TABLE_COLUMN_NAMES:
            self._column_widths.append(len(col))


    def addParam(self, param):
        """
        Add a parameter to the table.

        Args:
            param[dict]: A parameter dict() extracted from MOOSE yaml data.
        """

        self._parameters.append(param)
        for i in range(len(self.PARAMETER_TABLE_COLUMNS)):
            key = self.PARAMETER_TABLE_COLUMNS[i]
            param[key] = self._formatParam(param[key], key)
            self._column_widths[i] = max(self._column_widths[i], len(param[key]))


    def markdown(self):
        """
        Return the parameter table in markdown format. (public)
        """

        md = []

        s = self._buildFormatString(self.PARAMETER_TABLE_COLUMN_NAMES)

        frmt = '| ' + ' | '.join( ['{:<{}s}'] * (len(s)/2) ) + ' |'
        md += [frmt.format(*s)]

        md += ['']
        for i in range(len(self.PARAMETER_TABLE_COLUMN_NAMES)):
            md[-1] += '| ' + '-'*self._column_widths[i] + ' '
        md[-1] += '|'

        for param in self._parameters:
            text = []
            for key in self.PARAMETER_TABLE_COLUMNS:
                text.append(param[key])
            s = self._buildFormatString(text)
            md += [frmt.format(*s)]

        return '\n'.join(md)

    def _buildFormatString(self, text):
        """
        A helper method for building format strings. (protected)
        """
        output = []
        for i in range(len(text)):
            output.append(text[i])
            output.append(self._column_widths[i])
        return output

    def _formatParam(self, param, key):
        """
        Convert the supplied parameter into a format suitable for output.
        """

        # Make sure that supplied parameter is a string
        param = str(param).strip()

        # The c++ types returned by the yaml dump are raw and contain "allocator" stuff. This script attempts
        # to present the types in a more readable fashion.
        if key == 'cpp_type':
            # Convert std::string
            string = 'std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >'
            param = param.replace(string, 'std::string')

            # Convert vectors
            param = re.sub(r'std::__1::vector\<(.*),\sstd::__1::allocator\<(.*)\>\s\>', r'std::vector<\1>', param)

            # Return the monospaced text format
            param = '`' + param + '`'

        return param


class MooseObjectParameterTable(object):

    def __init__(self):
        self._required = MarkdownTable()
        self._optional = MarkdownTable()

    def addParam(self, param):

        print param['required'], type(param['required'])
        if param['required']:
            self._required.addParam(param)
        else:
            self._optional.addParam(param)

    def markdown(self):


        md = []
        md += [self._required.markdown()]
        md += ['']
        md += [self._optional.markdown()]
        return '\n'.join(md)
