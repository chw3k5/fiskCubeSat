__author__ = 'chw3k5'
import numpy
from matplotlib import pyplot as plt
from astropy.modeling import models, fitting

from dataGetter import getTableData

def findHighIntensitySpec(specDataCube, plotData=False):
    val_Max = 0
    val_galLat = -1
    val_galLon = -1
    mean_Max = 0
    mean_galLat = -1
    mean_galLon = -1
    len_galLon = len(specDataCube[0,0,:])
    len_galLat = len(specDataCube[0,:,0])
    len_spec = len(specDataCube[:,0,0])
    for galLatIndex in range(len_galLat):
        print galLatIndex
        for galLonIndex in range(len_galLon):
            testSpec=specDataCube[:,galLatIndex,galLonIndex]
            test_val = max(testSpec)
            if val_Max < test_val:
                val_Max = test_val
                val_galLat = galLatIndex
                val_galLon = galLonIndex
            test_mean = numpy.mean(testSpec)
            if mean_Max < test_mean:
                mean_Max = test_mean
                mean_galLat = galLatIndex
                mean_galLon = galLonIndex
    if plotData:
        plt.plot(specDataCube[:,val_galLat,val_galLon])
        plt.show()
        plt.plot(specDataCube[:,mean_galLat,mean_galLon])
        plt.show()
    return (val_galLat,mean_galLon), (val_galLat,mean_galLon)


def testSpecPlotting(testSpec,x, gg_fit, gg_init, showPlot=True):
    plt.plot(x, testSpec, 'ko')
    plt.plot(x, gg_fit(x), 'r-', lw=4)

    for initmodelIndex in range(len(gg_init.parameters)/3):
        baseIndex=initmodelIndex*3
        model_ginit = models.Gaussian1D(gg_init.parameters[baseIndex],
                                        gg_init.parameters[baseIndex+1],
                                        gg_init.parameters[baseIndex+2])
        plt.plot(model_ginit(x),'b-', lw=1)

    # for submodel in gg_fit._submodels:
    #     plt.plot(submodel(x),'b-', lw=1)
    for modelIndex in range(len(gg_fit._parameters)/3):
        baseIndex=modelIndex*3
        model_g = models.Gaussian1D(gg_fit._parameters[baseIndex],
                                    gg_fit._parameters[baseIndex+1],
                                    gg_fit._parameters[baseIndex+2])
        plt.plot(model_g(x),'g-', lw=1)
    if showPlot:plt.show()
    return

def getSpecLocalMaxima(inputSpec, doConv=False,sigma=5.0,convRadius=10,doPlot=False,minSignifigance=0.5):
    """
    This function is used to find the local maxima of a spectrum
    :param inputSpec: should just be a 1D array of regularly spaced spectral data
    :param doConv: changes the behavior of the function to include a convolution with a gaussian kernel
    :type doConv: bool
    :param sigma: in units of the regular spacing of the function parameter inputSpec and is the sigma used to specify
    the sigma of the gaussian convolution kernel to be applied to the data in the array inputSpec
    :type sigma: float
    :param convRadius: in units of the regular spacing of the function parameter inputSpec, this is the radius of the
    gaussian convolution kernel to be applied to the data in the array inputSpec. The actual size of the kernel is
    2*convRadius+1
    :type convRadius: int
    :param minSignifigance: in units of the regular spacing of the function parameter inputSpec, this is the minimum
    number of standard deviations that that a maxima can be from zero and still be returned by this function
    :return final_maximaList: this is a list of tuples the is the form (index_of_maxima,value_of_maxima)
    """
    if doConv:
        convRadius=abs(convRadius)
        convX = range(-1*convRadius,convRadius+1)
        lostConvLen = convRadius
        g = models.Gaussian1D(1, 0, sigma)
        convSpec = numpy.convolve(inputSpec,g(convX),'valid')
        convSpec*=numpy.mean(inputSpec)/numpy.mean(convSpec)
        testSpec=convSpec
    else:
        testSpec=inputSpec
        lostConvLen=0

    maximaTruthArray = numpy.r_[True, testSpec[1:] > testSpec[:-1]] & numpy.r_[testSpec[:-1] > testSpec[1:], True]
    maximaList=[]
    for maximaIndex in range(len(maximaTruthArray)):
        isMaxima = maximaTruthArray[maximaIndex]
        if isMaxima:
            x_val = maximaIndex+lostConvLen
            test_val = testSpec[maximaIndex]
            maximaList.append((x_val,test_val))
    maximaList.sort(key=lambda tup: tup[1])
    maximaList.reverse()

    if doConv:
        residual = inputSpec[convRadius:-convRadius]-convSpec
    else:
        residual = inputSpec
    residual_Error = numpy.std(residual)
    lowerCutoff = residual_Error*minSignifigance
    final_maximaList=[]
    for maxima in maximaList:
        (x_val,test_val) = maxima
        if lowerCutoff <= test_val:
            final_maximaList.append(maxima)

    if doPlot:
        x_lenInputSpec = len(inputSpec)
        x_inputSpec = range(x_lenInputSpec)
        plt.plot(x_inputSpec, inputSpec, 'k-')
        if doConv:
            x_conv = range(lostConvLen,len(convSpec)+lostConvLen)
            plt.plot(x_conv, convSpec, 'g-',linewidth=3)
            x_res=x_conv
        else:
            x_res=x_inputSpec
        x_resLen = len(x_res)
        plt.plot(x_res, residual, color='darkorchid')
        plt.plot(x_res, residual_Error*numpy.ones(x_resLen), color = 'dodgerblue')
        plt.plot(x_res, lowerCutoff*numpy.ones(x_resLen), color = 'orchid')
        for (x_val, test_val) in maximaList:plt.plot(x_val,test_val,'ro')
        for (x_val, test_val) in final_maximaList:plt.plot(x_val,test_val,'go')
        plt.show()
    return final_maximaList


if __name__ == "__main__":
    # Getting data here and selecting a test spectrum
    endIndex = 200

    testData = getTableData("testData/Am-241.csv")
    channels = testData['chan'][:endIndex]
    counts = testData['data'][:endIndex]

    fractionalRimprovment = 0.005
    showMaximaPlot = False
    maximaConvSigma = 5.
    maximaConvRadius = 20

    showFitterPlots = True

    # start putting this code below into definitions

    # initialize the model
    maximaList = getSpecLocalMaxima(counts,doConv=True,sigma=maximaConvSigma,convRadius=maximaConvRadius,doPlot=showMaximaPlot)
    len_spec = len(counts)
    x = range(len_spec)
    if maximaList == []:
        print 'No local maxima were found'
        x_mean = float(raw_input('Enter the channel number in range:('+str(min(x))+','+str(max(x))+')'))
        x_apml = float(raw_input('Enter the amplitude in range:('+str(min(counts))+','+str(max(counts))+')'))
    else:
        (x_mean,x_apml) = maximaList[0]
    g_first = models.Gaussian1D(x_apml, x_mean, 5)
    fitter = fitting.SLSQPLSQFitter()
    g_firstFit = fitter(g_first,x,counts)
    fit_info = fitter.fit_info
    R_val = fit_info['final_func_val']
    first_Rvalue = R_val
    R_val_current = R_val
    if showFitterPlots: testSpecPlotting(counts,x,g_firstFit,g_first, showPlot=True)
    modelParamsList = [(g_firstFit.parameters[0],g_firstFit.parameters[1],g_firstFit.parameters[2])]
    current_models = models.Gaussian1D(modelParamsList[0])

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

