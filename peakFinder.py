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
from quickPlots import quickPlotter






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
    # A few options for this data
    endIndex = 100
    verbose = True

    # Get the test data
    testDataFile = "testData/Am-241.csv"
    if verbose: print "Getting the test data in the file", testDataFile
    testData = getTableData(testDataFile)
    chan = testData['chan'][:endIndex]
    data = testData['data'][:endIndex]

    # do the peak finding algorithm
    if verbose: print "Applying the peak finding algorithm..."
    maxtab, mintab = peakdet(v=data, delta=40, x=chan)

    # plot the results
    if verbose: print "Getting plot parameters..."
    plotDict = {}
    plotDict['verbose'] = verbose

    # These can be a list or a single value
    plotDict['yData'] = [data, maxtab[:,1], mintab[:,1]]
    plotDict['xData'] = [chan, maxtab[:,0], mintab[:,0]]

    plotDict['colors'] = ['darkorchid', 'firebrick', 'dodgerblue']
    plotDict['legendLabel'] = ['raw data', 'found max', 'found min']

    plotDict['fmt'] = ['None', 'o', 'x']
    plotDict['markersize'] = [5, 9, 9]
    plotDict['alpha'] = [1.0, 0.7, 0.7]
    plotDict['ls'] = ['-', 'None', 'None']
    plotDict['lineWidth'] = 2

    # These must be a single value
    plotDict['title'] = 'Am-241'
    plotDict['xlabel'] = 'Channel Number'
    plotDict['ylabel'] = 'Counts'

    plotDict['legendAutoLabel'] = False
    plotDict['doLegend'] = True
    plotDict['legendLoc'] = 0
    plotDict['legendNumPoints'] = 3
    plotDict['legendHandleLength'] = 5

    plotDict['savePlot'] = False
    plotDict['plotFileName'] = 'Am-241plot'
    plotDict['doEPS'] = True
    plotDict['doShow'] = True

    quickPlotter(plotDict=plotDict)
