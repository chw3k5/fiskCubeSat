import numpy
from scipy.optimize import least_squares
from operator import itemgetter

from quickPlots import quickPlotter
from pulseReadIn import loadPulses, saveProcessedData


def initializeTestPlots(doShow, verbose, doSave=False, plotFileName='plot', title=None):
    plotDict = {}
    plotDict['verbose'] = verbose
    # These must be a single value
    if title is None:
        plotDict['title'] = 'Single Pulse Calculations'
    else:
        plotDict['title'] = title
    plotDict['xlabel'] = 'Time (S)'
    plotDict['ylabel'] = 'Voltage (V)'
    plotDict['legendAutoLabel'] = False
    plotDict['doLegend'] = True
    plotDict['legendLoc'] = 0
    plotDict['legendNumPoints'] = 3
    plotDict['legendHandleLength'] = 5
    plotDict['doShow'] = doShow

    # These can be a list or a single value
    plotDict['yData'] = []
    plotDict['xData'] = []
    plotDict['legendLabel'] = []
    plotDict['fmt'] = []
    plotDict['markersize'] = []
    plotDict['alpha'] = []
    plotDict['ls'] = []
    plotDict['lineWidth'] = []

    if doSave:
        plotDict['savePlot'] = True
        plotDict['plotFileName'] = plotFileName
    else:
        plotDict['savePlot'] = False
        plotDict['plotFileName'] = ''

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
    if (plotDict['doShow'] or plotDict['savePlot']):
        plotDict = appendToTestPlots(plotDict,
                                     midYPoints,
                                     midXPoints,
                                     legendLabel='Integral Calc = ' + str('%.6E' % integral),
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
        lowerBoundAmp = -numpy.abs(upperBoundAmp)
        upperBoundAmp = float(0)
        isPositive = False
        guessAmp = numpy.max((lowerBoundAmp, guessAmp))
    else:
        lowerBoundAmp = float(0)
        upperBoundAmp = numpy.abs(upperBoundAmp)
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
        if (plotDict['doShow'] or plotDict['savePlot']):
            paramString = 'Fitted (amp, tau) ['
            for (amp, tau) in sortedFittedAmpTau:
                paramString += '(' + str('%.3E' % amp) + ', ' + str('%.2E' % tau) + '), '
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
                                         legendLabel='Level ' + str(levelNum) + ' Residuals, cost=' + str('%.6E' % cost),
                                         fmt='None',
                                         markersize=4,
                                         alpha=1.0,
                                         ls='solid',
                                         lineWidth=1)
    else:
        sortedFittedAmpTau = None
        cost = float('inf')
    return sortedFittedAmpTau, cost, plotDict


def pulsePipeline(pulseDict, plotDict, multiplesOfMedianStdForRejection=None, conv_channels=1, trimBeforeMin=True,
                  numOfExponents=1, calcFitForEachPulse=False, upperBoundAmp=float('inf')):
    arrayData = pulseDict['arrayData']
    xData = pulseDict['xData']

    # Remove Outliers from this data
    if multiplesOfMedianStdForRejection is not None:
        arrayData, removalMask \
            = removeOutliers(arrayData, multiplesOfMedianStdForRejection=multiplesOfMedianStdForRejection)


    # Make x data, and send the raw data to the plot
    if (plotDict['doShow'] or plotDict['savePlot']):
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
        if (plotDict['doShow'] or plotDict['savePlot']):
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
        keptLen = len(keptXData)
        xStep = keptXData[1] - keptXData[0]
        pulseDict['keptLen'] = keptLen
        pulseDict['keptXData'] = numpy.arange(0.0, keptLen * float(xStep), xStep)
        pulseDict['deltaX'] = pulseDict['keptXData'][-1] - pulseDict['keptXData'][0]

        if (plotDict['doShow'] or plotDict['savePlot']):
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
    if calcFitForEachPulse:
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


def calcP_funcForSI(charArray1, charArray2,
                    charArrayTestPlotsFilename=None,
                    useFittedFunction=True,
                    xStep=1.0e-8,
                    xTruncateAfter_s=float('inf'),
                    numOfExponents=2,
                    upperBoundAmp=float('inf'),
                    verbose=True):
    if charArrayTestPlotsFilename is None:
        savePlot = False
    else:
        savePlot = True
    plotDict = initializeTestPlots(doShow=False,
                                   verbose=verbose,
                                   doSave=savePlot,
                                   plotFileName=charArrayTestPlotsFilename,
                                   title='Characteristic Functions')
    # Calculations for Characteristic Function 1
    char1Len = len(charArray1)
    dateLen1_s = char1Len * float(xStep)
    if dateLen1_s > xTruncateAfter_s:
        char1Len = int(numpy.round(xTruncateAfter_s / float(xStep)))
    charPulseDict1 = {'keptData':numpy.array(charArray1[:char1Len]), 'keptXData':numpy.arange(0.0, char1Len * float(xStep), xStep)}
    plotDict = appendToTestPlots(plotDict,
                                 charPulseDict1['keptData'],
                                 charPulseDict1['keptXData'],
                                 legendLabel='Function 1',
                                 fmt='None',
                                 markersize=4,
                                 alpha=1.0,
                                 ls='solid',
                                 lineWidth=1)

    # fit with a sum of exponential
    fittedAmpTau1, charPulseDict1['fittedCost'], junk \
        = fittingSumOfPowers(charPulseDict1['keptData'], charPulseDict1['keptXData'], numOfExponents, plotDict, upperBoundAmp)
    if fittedAmpTau1 is not None:
        for (index, (amp, tau)) in list(enumerate(fittedAmpTau1)):
            charPulseDict1['fittedAmp' + str(index + 1)] = amp
            charPulseDict1['fittedTau' + str(index + 1)] = tau
    else:
        for index in range(numOfExponents):
            charPulseDict1['fittedAmp' + str(index + 1)] = None
            charPulseDict1['fittedTau' + str(index + 1)] = None

    # Calculations for Characteristic Function 2
    char2Len = len(charArray2)
    dateLen2_s = char2Len * float(xStep)
    if dateLen2_s > xTruncateAfter_s:
        char2Len = int(numpy.round(xTruncateAfter_s / float(xStep)))
    charPulseDict2 = {'keptData':numpy.array(charArray2[:char2Len]), 'keptXData':numpy.arange(0.0, char2Len * float(xStep), xStep)}
    plotDict = appendToTestPlots(plotDict,
                                 charPulseDict2['keptData'],
                                 charPulseDict2['keptXData'],
                                 legendLabel='Function 2',
                                 fmt='None',
                                 markersize=4,
                                 alpha=1.0,
                                 ls='solid',
                                 lineWidth=1)

    # fit with a sum of exponential
    fittedAmpTau2, charPulseDict2['fittedCost'], junk \
        = fittingSumOfPowers(charPulseDict2['keptData'], charPulseDict2['keptXData'], numOfExponents, plotDict, upperBoundAmp)
    if fittedAmpTau2 is not None:
        for (index, (amp, tau)) in list(enumerate(fittedAmpTau2)):
            charPulseDict2['fittedAmp' + str(index + 1)] = amp
            charPulseDict2['fittedTau' + str(index + 1)] = tau
    else:
        for index in range(numOfExponents):
            charPulseDict2['fittedAmp' + str(index + 1)] = None
            charPulseDict2['fittedTau' + str(index + 1)] = None


    # replace the real-data average with a fitted function for the shaping indicator (SI) calculation
    if useFittedFunction:
        fit1_success = True
        for sumIndex in range(numOfExponents):
            if charPulseDict1['fittedAmp' + str(sumIndex + 1)] is None:
                fit1_success = False
                break
            if charPulseDict1['fittedTau' + str(sumIndex + 1)] is None:
                fit1_success = False
                break

        if fit1_success:
            newArray = numpy.zeros((char1Len))
            for sumIndex in range(numOfExponents):
                newArray += naturalPower(charPulseDict1['keptXData'],
                                         charPulseDict1['fittedAmp' + str(sumIndex + 1)],
                                         charPulseDict1['fittedTau' + str(sumIndex + 1)])
            charArray1 = newArray
        else:
            plotDict = appendToTestPlots(plotDict,
                                         charPulseDict1['keptData'],
                                         charPulseDict1['keptXData'],
                                         legendLabel='Function 1 FIT FAILED SHOWING AVERAGE PULSE',
                                         fmt='None',
                                         markersize=4,
                                         alpha=1.0,
                                         ls='dashed',
                                         lineWidth=1)

        fit2_success = True
        for sumIndex in range(numOfExponents):
            if charPulseDict2['fittedAmp' + str(sumIndex + 1)] is None:
                fit2_success = False
                break
            if charPulseDict2['fittedTau' + str(sumIndex + 1)] is None:
                fit2_success = False
                break

        if fit2_success:
            newArray = numpy.zeros((char2Len))
            for sumIndex in range(numOfExponents):
                newArray += naturalPower(charPulseDict2['keptXData'],
                                         charPulseDict2['fittedAmp' + str(sumIndex + 1)],
                                         charPulseDict2['fittedTau' + str(sumIndex + 1)])
            charArray2 = newArray
        else:
            plotDict = appendToTestPlots(plotDict,
                                         charPulseDict2['keptData'],
                                         charPulseDict2['keptXData'],
                                         legendLabel='FUNCTION 2 FIT FAILED SHOWING AVERAGE PULSE',
                                         fmt='None',
                                         markersize=4,
                                         alpha=1.0,
                                         ls='dashed',
                                         lineWidth=1)


    # Calculate the shaping indicator SI
    minCharLen = numpy.min((char1Len, char2Len))

    # Normalize the characteristic functions to have the maximum value equal to one
    # (that should be first value of the array)
    if charArray1[0] < 0.0:
        charArray1_forPfunc = charArray1[:minCharLen] / numpy.min(charArray1[:minCharLen])
    else:
        charArray1_forPfunc = charArray1[:minCharLen] / numpy.max(charArray1[:minCharLen])
    if charArray2[0] < 0.0:
        charArray2_forPfunc = charArray2[:minCharLen] / numpy.min(charArray2[:minCharLen])
    else:
        charArray2_forPfunc = charArray2[:minCharLen] / numpy.max(charArray2[:minCharLen])

    # The P-function calculation
    Pfunc = (charArray1_forPfunc - charArray2_forPfunc) / (charArray1_forPfunc + charArray2_forPfunc)
    plotDict = appendToTestPlots(plotDict,
                                 Pfunc,
                                 numpy.arange(0.0, minCharLen * float(xStep), xStep),
                                     legendLabel='Calculated P(t)' ,
                                     fmt='None',
                                     markersize=4,
                                     alpha=1.0,
                                     ls='dotted',
                                     lineWidth=2)

    quickPlotter(plotDict)

    # calculate integrals
    charPulseDict1['integral'], junk = calcIntegral(charPulseDict1['keptData'],
                                                        charPulseDict1['keptXData'],
                                                        plotDict)
    charPulseDict2['integral'], junk = calcIntegral(charPulseDict2['keptData'],
                                                        charPulseDict2['keptXData'],
                                                        plotDict)
    return Pfunc, charPulseDict1, charPulseDict2











def extractPulseInfo(folderName, fileNamePrefix='', filenameSuffix='',
                     columnNamesToIgnore=['time'],
                     skipRows=1, delimiter=',',
                     trimBeforeMin=True,
                     multiplesOfMedianStdForRejection=None,
                     conv_channels=1,
                     numOfExponents=1,
                     calcFitForEachPulse=False,
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
                                                numOfExponents, calcFitForEachPulse,
                                                upperBoundAmp)
            listOfPulseDicts.append(pulseDict)

        if showTestPlots_Pulses:
            quickPlotter(plotDict  = plotDict)

        if verbose:
            if IDindex % modLen == 0:
                print "Pulse operations are " \
                      + str('%02.2f' % (IDindex * 100.0 / float(numOfDataDicts))) + " % complete."

    return listOfPulseDicts
