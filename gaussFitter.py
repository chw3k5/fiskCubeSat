__author__ = 'chw3k5'
import numpy
from scipy.optimize import curve_fit
from mariscotti import mariscotti
from quickPlots import quickPlotter


def gaussian(x, a, b, c):
    x = numpy.array(x)
    a = float(a)
    b = float(b)
    c = float(c)
    return a * numpy.exp(float(-1.0) * ((x - b)**2.0) / (2.0 * (c**2)))


def singleGaussFitter(spectrum, x, guessParameters, showPlot=False, verbose=False, plotDict=None):
    if plotDict is None and showPlot:
        print "Cannot show plot, no plotDict was passed. Setting showPlot to False."
        showPlot = False

    (guessAplitude, guessMean, guessSigma) = guessParameters
    x = numpy.array(x)
    # here is where the fitting is calculated
    modelParams, pcov = curve_fit(gaussian, x, spectrum, p0=guessParameters)
    modelError = numpy.sqrt(numpy.diag(pcov))

    if showPlot:
        plotDict['yData'].extend([gaussian(x, *modelParams), gaussian(x, guessAplitude, guessMean, guessSigma)])
        plotDict['xData'].extend([x, x])
        plotDict['legendLabel'].extend(['fitted', 'guess'])
        plotDict['fmt'].extend(['o', 'd'])
        plotDict['markersize'].extend([6, 6])
        plotDict['alpha'].extend([.6, 0.6])
        plotDict['ls'].extend(['dotted', 'dashed'])
        plotDict['lineWidth'].extend([1, 1])
        return modelParams, modelError, plotDict
    else:
        return modelParams, modelError


def listGaussFitter(spectrum, guessParameters, verbose=False):


    return


def deconvolveGaussFitter():
    # loop through and see if it is worth trying to fit to the other local maxima
    gg_init=models.Gaussian1D(modelParamsList[0])
    len_maximaList = len(maximaList)
    if 1 < len_maximaList:
        for loopIndex in range(1,len_maximaList):
            R_last = R_val_current
            (x_mean,x_apml) = maximaList[loopIndex]
            gg_init=current_models+models.Gaussian1D(x_apml, x_mean, 5)
            gg_Fit = fitter(gg_init,x,counts)
            fit_info = fitter.fit_info
            R_val_current = fit_info['final_func_val']
            if showFitterPlots: testSpecPlotting(counts,x,gg_Fit,gg_init, showPlot=True)
            if R_val_current <= R_last*(1.-fractionalRimprovment):
                modelParamsList.append((gg_Fit.parameters[0], gg_Fit.parameters[1], gg_Fit.parameters[2]))
                current_models += models.Gaussian1D(modelParamsList[loopIndex])
            else:
                break

    return





if __name__ == '__main__':
    from dataGetter import getTableData
    # A few options for this data
    endIndex = 100
    verbose = True
    numberOfIndexesToSmoothOver = 5
    errFactor = 20
    showPlot_peakFinder = False
    showPlot_gaussFitters = True

    peakNum = 3

    # Get the test data
    testDataFile = "testData/Am-241.csv"
    if verbose:
        print "Getting the test data in the file.", testDataFile
    testData = getTableData(testDataFile)
    chan = testData['chan'][:endIndex]
    data = testData['data'][:endIndex]

    # apply the mariscotti peak finding algorithm
    gaussParametersArray = numpy.array(mariscotti(data, nsmooth=numberOfIndexesToSmoothOver,
                                                  errFactor=errFactor, plot=showPlot_peakFinder, verbose=verbose))

    #################
    ### NEW STUFF ###
    #################
    energyOffset = float(chan[0])
    energySpacing = (float(chan[-1]) - float(chan[0]))/float(len(chan) - 1)
    gaussParametersArray_absouleUnits = gaussParametersArray
    gaussParametersArray_absouleUnits[:,1] = gaussParametersArray[:,1] + energyOffset
    gaussParametersArray_absouleUnits[:,2] = gaussParametersArray[:,2] * energySpacing

    guessParameters = gaussParametersArray_absouleUnits[peakNum, :]

    if showPlot_gaussFitters:
        plotDict = {}
        plotDict['verbose'] = verbose
        plotDict['doShow'] = showPlot_gaussFitters

        # These can be a list or a single value, here we initialize a list.
        plotDict['yData'] = []
        plotDict['xData'] = []
        plotDict['legendLabel'] = []
        plotDict['fmt'] = []
        plotDict['markersize'] = []
        plotDict['alpha'] = []
        plotDict['ls'] = []
        plotDict['lineWidth'] = []

        # These must be a single value
        plotDict['title'] = ''
        plotDict['xlabel'] = 'Channel Number'
        plotDict['legendAutoLabel'] = False
        plotDict['doLegend'] = True
        plotDict['legendLoc'] = 0
        plotDict['legendNumPoints'] = 3
        plotDict['legendHandleLength'] = 5

        # append the plot values for the raw data
        plotDict['yData'].append(data)
        plotDict['xData'].append(chan)
        plotDict['legendLabel'].append('rawData')
        plotDict['fmt'].append('None')
        plotDict['markersize'].append(5)
        plotDict['alpha'].append(1.0)
        plotDict['ls'].append('solid')
        plotDict['lineWidth'].append(3)

        modelParams, modelError, plotDict = \
            singleGaussFitter(data, chan, guessParameters,
                              showPlot=True,
                              verbose=verbose, plotDict=plotDict)

        quickPlotter(plotDict=plotDict)
    else:
        modelParams, modelError = \
            singleGaussFitter(data, chan, guessParameters,
                              showPlot=False,
                              verbose=verbose, plotDict=None)






