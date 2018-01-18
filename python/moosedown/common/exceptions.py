class TokenizeException(Exception):
    pass

class RenderException(Exception):
    def __init__(self, info, message, *args):
        Exception(message.format(*args))
        self.info = info
