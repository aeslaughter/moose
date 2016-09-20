import csv
from collections import OrderedDict

##
# Reads CSV into a multidimensional list
# @param filename The filename to read, including the *.csv
# return The header and data lists
#
# Note, this function assumes that the first row is the header, as
# is the case for postprocessor *.csv output
class CSVIO(object):
  def __init__(self, filename):

    # Extract the data from the
    with open(filename, 'rb') as f:
      reader = csv.reader(f)
      self._data = OrderedDict()

      for row in reader:
        # Do not include blank rows
        if len(row) == 0:
          continue

        # First row is header
        if reader.line_num == 1:
          for r in row:
            self._data[r] = []
        else:
          for i in xrange(len(row)):
            self._data.values()[i].append(float(row[i]))

  def getColumn(self, name):
    return self._data[name]
