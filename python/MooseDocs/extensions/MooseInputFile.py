from MooseCompleteSourcePattern import MooseCompleteSourcePattern

class MooseInputFile(MooseCompleteSourcePattern):

    CPP_RE = r'!\[(.*?)\]\((.*\.[i])\s*(.*?)\)'

    def __init__(self):
        super(MooseInputFile, self).__init__(self.CPP_RE, 'text')
