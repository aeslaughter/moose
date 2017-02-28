import re
from markdown.postprocessors import Postprocessor
import bs4

class MooseSlideContents(Postprocessor):
    """

    """

    def run(self, text):
        """

        """
        self._levels = ['h1', 'h2', 'h3']

        soup = bs4.BeautifulSoup(text, 'html.parser')

        for section in soup.find_all("section", recursive=False):
            contents = section.find_all(self._levels)

            for tag in section.find_all():
                match = re.search(r'^!sectiontoc', unicode(tag.string))
                if match:
                    print contents

        #sections = soup.find_all('section', class_="slides")
        #print div



        #for section in root.findall('section'):
        #    print section
        #print soup
        #print soup.prettify()
        return soup.prettify()
