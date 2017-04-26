import numpy
from scipy.optimize import least_squares
from operator import itemgetter

from quickPlots import quickPlotter
from pulseReadIn import loadPulses, saveProcessedData


def initializeTestPlots(doShow, verbose):
    plotDict = {}
    plotDict['verbose'] = verbose
    # These must be a single value
    plotDict['title'] = 'Single Pulse Calculations'
    plotDict['xlabel'] = 'Time (us)'
    plotDict['ylabel'] = 'Voltage (V)'
    plotDict['legendAutoLabel'] = False
    plotDict['doLegend'] = True
    plotDict['legendLoc'] = 0
    plotDict['legendNumPoints'] = 3
    plotDict['legendHandleLength'] = 5
    plotDict['doShow'] = True

    # These can be a list or a single value
    plotDict['yData'] = []
    plotDict['xData'] = []
    plotDict['legendLabel'] = []
    plotDict['fmt'] = []
    plotDict['markersize'] = []
    plotDict['alpha'] = []
    plotDict['ls'] = []
    plotDict['lineWidth'] = []
    return plotDict


def appendToTestPlots(plotDict, arrayData, xData, legendLabel, fmt, markersize, alpha, ls, lineWidth):
    # These can be a list or a single value
    plotDict['yData'].append(arrayData)
    if xData is None:
        plotDict['xData'].append(range(len(arrayData)))
    else:
        plotDict['xData'].append(xData)
    plotDict['legendLabel'].append(legendLabel)
    plotDict['fmt'].append(fmt)
    plotDict['markersize'].append(markersize)
    plotDict['alpha'].append(alpha)
    plotDict['ls'].append(ls)
    plotDict['lineWidth'].append(lineWidth)
    return plotDict



def removeOutliers(data, multiplesOfMedianStdForRejection=2.0):
    dataMedian = numpy.median(data)
    difference = numpy.abs(data - dataMedian)
    medianOfDifference = numpy.median(difference)
    testValues = difference / medianOfDifference if medianOfDifference else 0.
    outliersMask = multiplesOfMedianStdForRejection < testValues
    medianArray = numpy.ones(numpy.shape(data), dtype=data.dtype) * dataMedian
    try:
        numpy.putmask(data, outliersMask, medianArray)
    except ValueError:
        print 'putmask: mask and data must be the same size'
        print 'data shape:', numpy.shape(data),  'medianArray shape', numpy.shape(medianArray)
        print 'outliersMask shape', numpy.shape(outliersMask),
        print 'testValues=', testValues
        print 'medianOfDifference', medianOfDifference
        print 'dataMedian=', dataMedian
        print 'mean(data)', numpy.mean(data)
        print 'max(data)', numpy.max(data)
        print 'min(data)', numpy.min(data)

    return data, numpy.logical_not(outliersMask)


def convData(arrayData, conv_channels):
    kernel1 = numpy.ones(conv_channels) / float(conv_channels)
    smoothedData = numpy.convolve(arrayData, kernel1, 'same')
    return smoothedData


def trimToMin(arrayData, smoothedData, xData):
     # trim the data before the minimum value
    dataMinIndex = numpy.argmin(smoothedData)
    keptData = arrayData[dataMinIndex:]
    keptXData = xData[dataMinIndex:]
    return keptData, keptXData


def calcIntegral(yData, xData, plotDict):
    # calculate the the integral of the data, (non-uniform grid).
    # Using a trapezoidal method of integration using the mid points.
    numberOfKeptDataPoints = len(yData)
    midXPoints = numpy.zeros((numberOfKeptDataPoints + 1))
    midYPoints = numpy.zeros((numberOfKeptDataPoints + 1))
    # the start and end points need to be treated differently
    midXPoints[0] = xData[0]
    midXPoints[-1] = xData[-1]
    # the start and end points need to be treated differently
    midYPoints[0] = yData[0]
    midYPoints[-1] = yData[-1]
    # Calculate the midpoints of the x and y data
    if numberOfKeptDataPoints > 1:
        midXPoints[1:-1] = (xData[1:] + xData[:-1]) / 2.0
        midYPoints[1:-1] = (yData[1:] + yData[:-1]) / 2.0
    # Use the trapezoidal integral calculation method
    # dx is the bases of each trapezoid
    dx = midXPoints[1:] - midXPoints[:-1]
    # dy is the average height of the trapezoid
    dy = (midYPoints[1:] + midYPoints[:-1]) / 2.0
    integral = numpy.sum(dx * dy)
    # plot the midpoint calculation
    if plotDict['doShow']:
        plotDict = appendToTestPlots(plotDict,
                                     midYPoints,
                                     midXPoints,
                                     legendLabel='Integral Calc = ' + str('%02.6f' % integral),
                                     fmt='x',
                                     markersize=4,
                                     alpha=1.0,
                                     ls='None',
                                     lineWidth=1)
    return integral, plotDict


def naturalPower(xData, amplitude, tau):
    return amplitude * numpy.exp(-xData / tau)


def sumOfNaturalPowers(level, yData, xData):
    if level == 1:
        optimizeFunc = lambda (Amp1, Tau1): \
            naturalPower(xData, Amp1, Tau1) - yData
    elif level == 2:
        optimizeFunc = lambda (Amp1, Tau1, Amp2, Tau2): \
            naturalPower(xData, Amp1, Tau1) + \
            naturalPower(xData, Amp2, Tau2) - yData
    elif level == 3:
        optimizeFunc = lambda (Amp1, Tau1, Amp2, Tau2, Amp3, Tau3): \
            naturalPower(xData, Amp1, Tau1) + \
            naturalPower(xData, Amp2, Tau2) + \
            naturalPower(xData, Amp3, Tau3) - yData
    elif level == 4:
        optimizeFunc = lambda (Amp1, Tau1, Amp2, Tau2, Amp3, Tau3, Amp4, Tau4): \
            naturalPower(xData, Amp1, Tau1) + \
            naturalPower(xData, Amp2, Tau2) + \
            naturalPower(xData, Amp3, Tau3) + \
            naturalPower(xData, Amp4, Tau4) - yData
    else:
        optimizeFunc = None
    return optimizeFunc


def fittingSumOfPowers(yData, xData, levelNum, plotDict, upperBoundAmp=float('inf')):
    guessParams = []
    guessAmp = yData[0]
    if guessAmp < 0:
        lowerBoundAmp = -upperBoundAmp
        upperBoundAmp = float(0)
        isPositive = False
        guessAmp = numpy.max((lowerBoundAmp, guessAmp))
    else:
        lowerBoundAmp = float(0)
        upperBoundAmp = upperBoundAmp
        isPositive = True
        guessAmp = numpy.min((upperBoundAmp, guessAmp))
    guessTau = 1.0 / (1.0 + ((yData[-1] - yData[0]) / (xData[-1] - xData[0])))
    lowerBoundTau = float(0)
    upperBoundTau = float('inf')
    guessParams.append((guessAmp, lowerBoundAmp, upperBoundAmp, guessTau, lowerBoundTau, upperBoundTau))
    guessParams = guessParams * levelNum

    guesses = []
    lowerBounds = []
    upperBounds = []
    levelNum = len(guessParams)
    for (guessAmp, lowerBoundAmp, upperBoundAmp, guessTau, lowerBoundTau, upperBoundTau) in guessParams:
        guesses.append(guessAmp)
        guesses.append(guessTau)
        lowerBounds.append(lowerBoundAmp)
        lowerBounds.append(lowerBoundTau)
        upperBounds.append(upperBoundAmp)
        upperBounds.append(upperBoundTau)
    optimizeFunc = sumOfNaturalPowers(levelNum, yData, xData)
    # print yData
    # print numpy.min(yData)
    lsq_results = least_squares(optimizeFunc,
                                 tuple(guesses),
                                 bounds=(tuple(lowerBounds), tuple(upperBounds)))
    if lsq_results['success']:
        cost = lsq_results['cost']
        residuals = lsq_results['fun']
        # jac = lsq_results1['jac']
        fittedAmpTau = []
        for paramsIndex in range(levelNum):
            AmpIndex = 2 * paramsIndex
            TauIndex = (2 * paramsIndex) + 1
            fittedAmpTau.append((lsq_results['x'][AmpIndex], lsq_results['x'][TauIndex]))
        sortedFittedAmpTau = sorted(fittedAmpTau, key=itemgetter(0), reverse=isPositive)
        # print "guesses", guesses
        # print "results", sortedFittedAmpTau
        if plotDict['doShow']:
            paramString = 'Fitted (amp, tau) ['
            for (amp, tau) in sortedFittedAmpTau:
                paramString += '(' + str('%2.3f' % amp) + ', ' + str('%2.2f' % tau) + '), '
            paramString = paramString[:-2] + ']'

            plotDict = appendToTestPlots(plotDict,
                                         optimizeFunc(lsq_results['x']) + yData,
                                         xData,
                                         legendLabel=paramString,
                                         fmt='None',
                                         markersize=4,
                                         alpha=1.0,
                                         ls='solid',
                                         lineWidth=1)
            plotDict = appendToTestPlots(plotDict,
                                         residuals,
                                         xData,
                                         legendLabel='Level ' + str(levelNum) + ' Residuals, cost=' + str(cost),
                                         fmt='None',
                                         markersize=4,
                                         alpha=1.0,
                                         ls='solid',
                                         lineWidth=1)
    else:
        sortedFittedAmpTau = None
        cost = float('inf')
    return sortedFittedAmpTau, cost, plotDict


def pulsePipeline(pulseDict, plotDict, multiplesOfMedianStdForRejection=None, conv_channels=1, trimBeforeMin=True, numOfExponents=1, upperBoundAmp=float('inf')):
    arrayData = pulseDict['arrayData']
    xData = pulseDict['xData']

    # Remove Outliers from this data
    if multiplesOfMedianStdForRejection is not None:
        arrayData, removalMask \
            = removeOutliers(arrayData, multiplesOfMedianStdForRejection=multiplesOfMedianStdForRejection)


    # Make x data, and send the raw data to the plot
    if plotDict['doShow']:
        plotDict = appendToTestPlots(plotDict,
                                     arrayData,
                                     xData,
                                     legendLabel='Read In Data ' + str(pulseDict['uniqueID']),
                                     fmt='None',
                                     markersize=6,
                                     alpha=1.0,
                                     ls='solid',
                                     lineWidth=2)
    # Convolutions
    if conv_channels > 1:
        smoothedData = convData(arrayData, conv_channels)
        pulseDict['smoothedData'] = smoothedData
        if plotDict['doShow']:
            plotDict = appendToTestPlots(plotDict,
                                         smoothedData,
                                         xData,
                                         legendLabel='Smoothed Data, n=' + str(conv_channels),
                                         fmt='None',
                                         markersize=6,
                                         alpha=1.0,
                                         ls='dotted',
                                         lineWidth=1)
    else:
        smoothedData = arrayData
        pulseDict['smoothedData'] = None

    # trim all the data prior to the minimum
    if trimBeforeMin:
        keptData, keptXData = trimToMin(arrayData, smoothedData, xData)
        pulseDict['keptData'] = keptData
        pulseDict['keptXData'] = keptXData
        if plotDict['doShow']:
            plotDict = appendToTestPlots(plotDict,
                                         keptData,
                                         keptXData,
                                         legendLabel='trimmed data',
                                         fmt='None',
                                         markersize=6,
                                         alpha=1.0,
                                         ls='dashed',
                                         lineWidth=1)
    else:
        keptData = smoothedData
        keptXData = xData
        pulseDict['keptData'] = None
        pulseDict['keptXData'] = None

    # calculate integral
    pulseDict['integral'], plotDict = calcIntegral(pulseDict['keptData'],
                                                   pulseDict['keptXData'],
                                                   plotDict)

    # fit with a sum of exponential
    fittedAmpTau, pulseDict['fittedCost'], plotDict \
        = fittingSumOfPowers(pulseDict['keptData'], pulseDict['keptXData'], numOfExponents, plotDict, upperBoundAmp)
    if fittedAmpTau is not None:
        for (index, (amp, tau)) in list(enumerate(fittedAmpTau)):
            pulseDict['fittedAmp' + str(index + 1)] = amp
            pulseDict['fittedTau' + str(index + 1)] = tau
    else:
        for index in range(numOfExponents):
            pulseDict['fittedAmp' + str(index + 1)] = None
            pulseDict['fittedTau' + str(index + 1)] = None
    return pulseDict, plotDict


def extractPulseInfo(folderName, fileNamePrefix='', filenameSuffix='',
                     columnNamesToIgnore=['time'],
                     skipRows=1, delimiter=',',
                     trimBeforeMin=True,
                     multiplesOfMedianStdForRejection=None,
                     conv_channels=1,
                     numOfExponents=1,
                     upperBoundAmp=float('inf'),
                     showTestPlots_Pulses=False,
                     testModeReadIn=False,
                     verbose=True):

    listOfDataDicts = loadPulses(folderName,
                                 fileNamePrefix=fileNamePrefix,
                                 filenameSuffix=filenameSuffix,
                                 skipRows=skipRows,
                                 delimiter=delimiter,
                                 testMode=testModeReadIn,
                                 verbose=verbose)

    numOfDataDicts = len(listOfDataDicts)
    modLen = max((int(numOfDataDicts / 200.0), 1))
    if verbose:
        if conv_channels > 1:
            print "The data is to be smoothed with a top hat kernel of " + str(conv_channels) + " channels."
        if trimBeforeMin:
            print "All the data values before the minimum value will be trimmed away before being saved."
        print " "
    columnNamesToIgnore.append('fileName'.lower())
    columnNamesToIgnore.append('uniqueID'.lower())
    columnNamesToIgnore.append('xData'.lower())

    # initialize the dictionary to extract data from processed pulses
    listOfPulseDicts = []


    for IDindex in range(numOfDataDicts):
        tableDict = listOfDataDicts[IDindex]
        uniqueID = tableDict['uniqueID']
        tableDict = listOfDataDicts[IDindex]
        dataKeys = []
        tableDict['xData'] = None
        tableDictKeys = tableDict.keys()
        for testKey in tableDictKeys:
            if not testKey.lower() in columnNamesToIgnore:
                dataKeys.append(testKey)
            if 'time' == testKey.lower():
                tableDict['xData'] = tableDict[testKey]
        plotDict = initializeTestPlots(showTestPlots_Pulses, verbose)
        for key in dataKeys:
            # make a new dictionary for each pulse, there may be many pulses in tableDict
            pulseDict = {}
            # assign the pulse yData
            pulseDict['arrayData'] = tableDict[key]
            # if the pulse has x Data, assign it
            if tableDict['xData'] is None:
                pulseDict['xData'] = len(pulseDict['arrayData'])
            else:
                pulseDict['xData'] = tableDict['xData']
            # assign a unique iD to this pulse for later identification.
            pulseDict['uniqueID'] = key.replace(' ', '_') + '_' + uniqueID
            pulseDict['rawDataFileName'] = tableDict['fileName']

            # process the pulse
            pulseDict, plotDict = pulsePipeline(pulseDict, plotDict,
                                                multiplesOfMedianStdForRejection,
                                                conv_channels, trimBeforeMin,
                                                numOfExponents, upperBoundAmp)
            listOfPulseDicts.append(pulseDict)

        if showTestPlots_Pulses:
            quickPlotter(plotDict  = plotDict)

        if verbose:
            if IDindex % modLen == 0:
                print "Pulse operations are " \
                      + str('%02.2f' % (IDindex * 100.0 / float(numOfDataDicts))) + " % complete."

    return listOfPulseDicts
