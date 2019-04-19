class ObserverMixin(object):
    """Mixin class to control interactive behavior of the object."""

    @staticmethod
    def validOptions():
        from .. import geometric
        from . import Options


        opt = Options()
        #outline = geometric.OutlineSource.validOptions()
        #outline.update(color=(0,1,0), linewidth=2)
        outline = Options()
        outline.add('enabled', True, doc="Enable/disable interactive status of the object.")
        #outline.remove('bounds')
        opt.add('interactive', outline, doc="Options for controlling interaction style.")

        return opt

    def interactive(self):
        return self.getOption('interactive').get('enabled')
