#-------------------------------------------------------------------------------
# Name:        peakFinder.py
# Purpose:
#
# Author:      Jeremiah test
#
# Created:     23/06/2016
# Copyright:   (c) Jeremiah 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#import numpy as np
import matplotlib.pyplot as mpl
import sys
from numpy import NaN, Inf, isscalar, asarray, array
from dataGetter import getTableData






def peakdet(v, delta, x = None):

    maxtab = []
    mintab = []

    if x is None:
        x = array(range(len(v)))

    v = asarray(v)

    if len(v) != len(x):
        sys.exit('Input vectors v and x must have same length')

    if not isscalar(delta):
        sys.exit('Input argument delta must be a scalar')

    if delta <= 0:
        sys.exit('Input argument delta must be positive')

    mn, mx = Inf, -Inf
    mnpos, mxpos = NaN, NaN

    lookformax = True

    for i in range(len(v)):
        this = v[i]
        if this > mx:
            mx = this
            mxpos = x[i]
        if this < mn:
            mn = this
            mnpos = x[i]

        if lookformax:
            if this < mx-delta:
                maxtab.append((mxpos, mx))
                mn = this
                mnpos = x[i]
                lookformax = False
        else:
            if this > mn + delta:
                mintab.append((mnpos, mn))
                mx = this
                mxpos = x[i]
                lookformax = True

    return array(maxtab), array(mintab)

if __name__=="__main__":
    endIndex = 100


    from matplotlib import pyplot as plt


    testData = getTableData("testData/Am-241.csv")
    chan = testData['chan'][:endIndex]
    data = testData['data'][:endIndex]
    maxtab, mintab = peakdet(v=data, delta=40, x=chan)
    print "Plotting now..."
    ledlines = []
    ledlabels = []

    plt.plot(chan, data, color='darkorchid', ls='-', linewidth='3')
    ledlines.append(plt.Line2D(range(10), range(10), color='darkorchid', ls='-', linewidth='3'))
    ledlabels.append('raw data')


    plt.plot(maxtab[:,0], maxtab[:,1], color='firebrick', ls='None', linewidth='1', marker='o')
    ledlines.append(plt.Line2D(range(10), range(10), color='firebrick', ls='None', marker='o'))
    ledlabels.append('found max')

    plt.plot(mintab[:,0], mintab[:,1], color='dodgerblue', ls='None', linewidth='1', marker='x')
    ledlines.append(plt.Line2D(range(10), range(10), color='dodgerblue', ls='None', marker='x'))
    ledlabels.append('found min')

    plt.title('Am-241')
    plt.xlabel('Channel Number')
    plt.ylabel("Counts")
    plt.legend(ledlines,ledlabels, loc=0, numpoints=1, handlelength=5)
    plt.savefig('Am-241plot.eps')

    plt.show()

    # series = [0,0,0,2,0,0,0,0,0,0,0,2,0,0,0,0,0]
    # maxtab, mintab = peakdet(series,.3)
    # plot(series)
    # scatter(array(maxtab)[:,0], array(maxtab)[:,1], color='blue')
    # scatter(array(mintab)[:,0], array(mintab)[:,1], color='red')
    # show()