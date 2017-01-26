# import necessary packages
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sp
import sys

# import data getting function
from dataGetter import getTableData


# peak detection function
def peakDet(channels, counts):
    # converts data from .csv file into arrays
    channels = np.array(channels)
    counts = np.array(counts)

    # startup error message
    if len(channels) != len(counts):
        sys.exit('channels and counts must have the same length')

    # identifies relative max/min values in the "counts" array. "order" refers to the number of neighboring points on
    # either side that are compared to the point in question.
    maxcounts = sp.argrelmax(counts, order=30)
    mincounts = sp.argrelmin(counts, order=30)
    highs = []
    lows = []

    # creates a list of ordered pairs of max values
    for max in maxcounts:
        highs.append((channels[max], counts[max]))

    # creates a list of ordered pairs of min values
    for min in mincounts:
        lows.append((channels[min], counts[min]))

    # returns max/min lists as arrays
    return np.array(highs), np.array(lows)

if __name__ == "__main__":
    # cutoff point for data
    endIndex = 200

    testData = getTableData("testData/Am-241.csv")
    channels = testData['chan'][:endIndex]
    counts = testData['data'][:endIndex]
    highs, lows = peakDet(channels, counts)
    print "Plotting now..."
    ledlines = []
    ledlabels = []

    # generates spectrum and marks relative maxima and minima
    plt.plot(channels, counts, color='darkorchid', ls='-', linewidth='3')
    ledlines.append(plt.Line2D(range(10), range(10), color='darkorchid', ls='-', linewidth='3'))
    ledlabels.append('raw data')

    plt.plot(highs[:, 0], highs[:, 1], color='firebrick', ls='None', linewidth='1', marker='o')
    ledlines.append(plt.Line2D(range(10), range(10), color='firebrick', ls='None', marker='o'))
    ledlabels.append('found max')

    plt.plot(lows[:, 0], lows[:, 1], color='dodgerblue', ls='None', linewidth='1', marker='x')
    ledlines.append(plt.Line2D(range(10), range(10), color='dodgerblue', ls='None', marker='x'))
    ledlabels.append('found min')

    plt.title('Am-241')
    plt.xlabel('Channel Number')
    plt.ylabel("Counts")
    plt.legend(ledlines, ledlabels, loc=0, numpoints=1, handlelength=5)
    plt.savefig('Am-241plot.eps')

    plt.show()