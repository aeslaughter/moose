class TokenizeException(Exception):
    def __init__(self, match, pattern, line):
        self.match = match
        self.pattern = pattern
        self.line = line

class RenderException(Exception):
    pass
