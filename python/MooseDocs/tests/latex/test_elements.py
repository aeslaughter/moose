#!/usr/bin/env python
import unittest
from MooseDocs.html2latex import Translator, BasicExtension
from MooseDocs import testing

class TestLatexElements(unittest.TestCase):
    """
    Test that basic html to latex conversion working.
    """
    @classmethod
    def setUpClass(cls):
        config = dict()
        cls._translator = Translator(extensions=[BasicExtension(**config)])

    def assertLaTeX(self, html, gold):
        """
        Assert markdown to latex conversion.
        """
        tex = self._translator.convert(html)
        print ('\n{:>15}: {}'*3).format('HTML', repr(html), 'TEX', repr(tex), 'TEX (GOLD)', repr(gold))
        self.assertEqual(tex, gold, testing.text_diff(tex.splitlines(), gold.splitlines()))

    def test_a(self):
        html = u'<a href="foo">bar</a>'
        self.assertLaTeX(html, u'\href{foo}{bar}')

    def test_li(self):
        html = u'<li>content</li>'
        gold = u'\\item content'
        self.assertLaTeX(html, gold)

    def test_ul(self):
        html = u'<ul><li>one</li><li>two</li></ul>'
        gold = u'\\begin{itemize}\n\\item one\n\\item two\n\\end{itemize}'
        self.assertLaTeX(html, gold)

    def test_ol(self):
        html = u'<ol><li>one</li><li>two</li></ol>'
        gold = u'\\begin{enumerate}\n\\item one\n\\item two\n\\end{enumerate}'
        self.assertLaTeX(html, gold)

    def test_headings(self):
        headings = ['section', 'subsection', 'subsubsection', 'textbf', 'underline', 'emph']
        text = ['One', 'Two', 'Three', 'Four', 'Five', 'Six']
        for i, h in enumerate(headings):
            html = u'<h{0}>Heading {1}</h{0}>'.format(i+1, text[i])
            gold = u'\%s{Heading %s}' % (h, text[i])
            self.assertLaTeX(html, gold)

            html = u'<h{0} id="heading-{2}">Heading {1}</h{0}>'.format(i+1, text[i], text[i].lower())
            gold = u'\%s{Heading %s\label{heading-%s}}' % (h, text[i], text[i].lower())
            self.assertLaTeX(html, gold)

    def test_div(self):
        html = u'<div>This is some content with <a href="foo">link</a> in the middle.</div>'
        gold = u'This is some content with \href{foo}{link} in the middle.'
        self.assertLaTeX(html, gold)

    def test_pre(self):
        html = u'<pre>double x = 2;\nx += 2;</pre>'
        gold = u'\\begin{verbatim}\ndouble x = 2;\nx += 2;\n\\end{verbatim}'
        self.assertLaTeX(html, gold)

    def test_code(self):
        html = u'<code>double x = 2;</code>'
        gold = u'\\texttt{double x = 2;}'
        self.assertLaTeX(html, gold)

    def test_pre_code(self):
        html = u'<pre><code>double x = 2;\nx += 2;</code></pre>'
        gold = u'\\begin{verbatim}\ndouble x = 2;\nx += 2;\n\\end{verbatim}'
        self.assertLaTeX(html, gold)

    def test_hr(self):
        html = u'<hr>'
        gold = u'\\hrule\n'
        self.assertLaTeX(html, gold)

    def test_p(self):
        html = u'<p>This is a paragraph.</p><p>And this is another.</p>'
        gold = u'\\par\nThis is a paragraph.\n\\par\nAnd this is another.\n'
        self.assertLaTeX(html, gold)

    def test_span(self):
        html = u'<span>Some text</span>'
        gold = u'Some text'
        self.assertLaTeX(html, gold)

    def test_em(self):
        html = u'<em>slanty</em>'
        gold = u'\\emph{slanty}'
        self.assertLaTeX(html, gold)

    def test_inline_equation(self):
        html = u'<script type="math/tex">x+y</script>'
        gold = u'$x+y$'
        self.assertLaTeX(html, gold)

    def test_block_equation(self):
        html = u'<script type="math/tex; mode=display">x+y</script>'
        gold = u'\\begin{equation}\nx+y\n\\end{equation}'
        self.assertLaTeX(html, gold)

    def test_th_td(self):
        html = u'<th>1</th><th>2</th><th>3</th>'
        gold = u'1 & 2 & 3 \\\\'
        self.assertLaTeX(html, gold)
        self.assertLaTeX(html.replace('th', 'td'), gold)

    def test_tr(self):
        html = u'<tr><th>1</th><th>2</th><th>3</th></tr><tr><th>2</th><th>4</th><th>6</th></tr>'
        gold = u'1 & 2 & 3 \\\\\n2 & 4 & 6 \\\\\n'
        self.assertLaTeX(html, gold)

    def test_thead_tfoot(self):
        html = u'<thead><tr><th>1</th><th>2</th><th>3</th></tr></thead>'
        gold = u'\\hline\n1 & 2 & 3 \\\\\n\\hline'
        self.assertLaTeX(html, gold)
        self.assertLaTeX(html.replace('thead', 'tfoot'), gold)

    def test_tbody(self):
        html = u'<tbody><tr><td>1</td><td>2</td><td>3</td></tr><tr><td>2</td><td>4</td><td>6</td></tr></tbody>'
        gold = u'1 & 2 & 3 \\\\\n2 & 4 & 6 \\\\\n'
        self.assertLaTeX(html, gold)

    def test_thead_tbody_tfoot_table(self):
        html = u'<thead><tr><th>h1</th><th>h2</th><th>h3</th></tr></thead>'
        html += u'<tbody><tr><td>1</td><td>2</td><td>3</td></tr><tr><td>2</td><td>4</td><td>6</td></tr></tbody>'
        html += u'<tfoot><tr><td>f1</td><td>f2</td><td>f3</td></tr></tfoot>'
        gold = u'\\hline\nh1 & h2 & h3 \\\\\n\\hline'
        gold += u'1 & 2 & 3 \\\\\n2 & 4 & 6 \\\\\n'
        gold += u'\\hline\nf1 & f2 & f3 \\\\\n\\hline'
        self.assertLaTeX(html, gold)

        html = '<table>' + html + '</table>'
        gold = '\\begin{tabular}{ll}\n' + gold + '\n\\end{tabular}'
        self.assertLaTeX(html, gold)

    def test_figure(self):
        html = u'<figure>content</figure>'
        gold = u'\\begin{figure}\ncontent\n\\end{figure}'
        self.assertLaTeX(html, gold)

    def test_figcaption(self):
        html = u'<figcaption>a caption</figcaption>'
        gold = u'\\caption{a caption}'
        self.assertLaTeX(html, gold)

    def test_img(self):
        html = u'<img src="file.png">'
        gold = u'\\includegraphics{file.png}\n'
        self.assertLaTeX(html, gold)

    def test_figure_figcaption_img(self):
        html = u'<figure><img src="file.png"><figcaption>a caption</figcaption></figure>'
        gold = u'\\begin{figure}\n\\includegraphics{file.png}\n\\caption{a caption}\n\\end{figure}'
        self.assertLaTeX(html, gold)

    def test_center(self):
        html = u'<center>this</center>'
        gold = u'\\begin{center}\nthis\n\\end{center}'
        self.assertLaTeX(html, gold)

    def test_unknown(self):
        html = u'<unknown>something</unknown>'
        gold = u'\\begin{verbatim}\nsomething\n\\end{verbatim}'
        self.assertLaTeX(html, gold)

if __name__ == '__main__':
    unittest.main(verbosity=2)
