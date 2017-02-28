import re
from markdown.postprocessors import Postprocessor
from markdown.util import etree
import bs4

class MooseSlideContents(Postprocessor):
    """

    """
    RE = r'!subtoc'

    def run(self, text):
        """

        """
        self._levels = ['h1', 'h2', 'h3']

        soup = bs4.BeautifulSoup(text, 'html.parser')

        for section in soup.find_all("section", recursive=False):
            headings = section.find_all(self._levels)
            for subsection in section.find_all("section", recursive=False):
                master = section.find_all('section', recursive=False, limit=1)[0]
                for item in subsection.find_all():
                    match = re.search(self.RE, unicode(item.string))
                    if match:
                        item.replace_with(self._contents(master['id'], headings))
                    elif item in headings:
                        headings.remove(item)







        #sections = soup.find_all('section', class_="slides")
        #print div



        #for section in root.findall('section'):
        #    print section
        #print soup
        #print soup.prettify()
        return soup.prettify()

    @staticmethod
    def _contents(prefix, headings):

        soup = bs4.BeautifulSoup('', 'html.parser')
        ul = soup.new_tag('ul')
        level = None
        for h in headings:
            current = int(h.name[-1])

            li = soup.new_tag('li')
            a = soup.new_tag('a')
            a.string = h.string
            a['href'] = '#{}'.format(h['id'])
            li.append(a)
            ul.append(li)

        print ul
        return ul
