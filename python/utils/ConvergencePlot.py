import matplotlib.pyplot, numpy
from pylab import *
from matplotlib.backends.backend_pdf import PdfPages

##
# A tool for making convergence plots.
# @param x The x data of the graph (e.g., dofs)
# @param y The y data of the graph (e.g., L2_error)
#
# Key, value Options:
#   xlabel = <str> The label for the x-axis
#   ylabel = <str> The label for the y-axis
#
class ConvergencePlot(object):
  def __init__(self, x, y, **kwargs):

    x_label = kwargs.pop('xlabel', 'x')
    y_label = kwargs.pop('ylabel', 'y')

    self._x = numpy.array(x)
    self._y = numpy.array(y)

    figure(figsize=(10,6))
    plot(self._x, self._y, 'ob', markersize=12)

    self._gcf = gcf()
    self._gca = gca()

    gca().set_yscale('log')
    gca().set_xscale('log')

    # Add axis labels
    xlabel(x_label,{'fontsize':20})
    ylabel(y_label,{'fontsize':20})

    # Adjust tick mark fonts
    for xtick in  gca().xaxis.get_major_ticks():
      xtick.label.set_fontsize(18)

    for ytick in gca().yaxis.get_major_ticks():
      ytick.label.set_fontsize(18)

    # Apply grid marks
    grid(True)
    grid(True, which='minor', color='b')


  ##
  # Display and output the slope fit.
  #
  # key, value Options:
  #    order = <int> The order of the fit for plotting idea line (default = 2).
  def fit(self, **kwargs):

    # Perform fit
    coefficients = numpy.polyfit(log10(self._x), log10(self._y), 1)
    print coefficients

    #polynomial = numpy.poly1d(coefficients)
    #order = kwargs.pop('order', 2)

    #y_ideal = pow(10,coefficients[1])*numpy.power(self._x, sign(coefficients[0])*order)

    #plot(self._x, y_ideal, '-k', lw=1)

    #text(self._x[0], self._y[-1],'slope: ' + str(coefficients[0]))1


  ##
  # Save the plot to the provide filename.
  def save(self, filename):
    savefig(filename)

  def show():
    show()
