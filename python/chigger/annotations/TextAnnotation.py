from TextAnnotationBase import TextAnnotationBase
from TextAnnotationSource import TextAnnotationSource

class TextAnnotation(TextAnnotationBase):
    @staticmethod
    def validOptions():
        opt = TextAnnotationBase.validOptions()
        opt += TextAnnotationSource.validOptions()
        return opt

    def __init__(self, **kwargs):
        super(TextAnnotation, self).__init__(TextAnnotationSource(), **kwargs)
