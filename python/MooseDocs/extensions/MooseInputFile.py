from MooseCompleteSourcePattern import MooseCompleteSourcePattern

class MooseInputFile(MooseCompleteSourcePattern):

    CPP_RE = r'!\[(.*?)\]\((.*\.[i])\s*(.*?)\)'

    def __init__(self, src):
        super(MooseInputFile, self).__init__(self.CPP_RE, src, 'text')
