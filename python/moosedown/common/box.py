def box(content, title=None, line=None):
    """
    Tool for building unicode box around text, this is used for error reporting.
    """
    lines = content.split('\n')
    n_lines = len(max(lines, key=len))

    out = ''
    if title:
        out += title + '\n'

    if line is not None:
        num_digits = len(str(line + len(lines)))
        out += u'{0:>{1}}{2}{3}{4}'.format(' ', num_digits, u'\u250C', u'\u2500'*n_lines, u'\u2510')
        for i, x in enumerate(lines):
            out += u'\n{0:>{1}}{2}{3:<{4}}{2}'.format(line+i, num_digits, u'\u2502', x, n_lines)
        out += u'\n{0:>{1}}{2}{3}{4}'.format(' ', num_digits, u'\u2514', u'\u2500'*n_lines, u'\u2518')
    else:
        out += u'{}{}{}'.format(u'\u250C', u'\u2500'*n_lines, u'\u2510')
        for i, x in enumerate(lines):
            out += u'\n{0}{1:<{2}}{0}'.format(u'\u2502', x, n_lines)
        out += u'\n{}{}{}'.format(u'\u2514', u'\u2500'*n_lines, u'\u2518')

    return out
