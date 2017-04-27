import os
import getpass





from pulse.pulseShapeDiscrim import doExtractAndSavePulseInfo, loadSavedGroupsOfPulses, removeOutlierPulses,\
    makeGroupHistograms, doFindHistPeaks

if __name__ == '__main__':
    preformStep1 = True
    preformStep2 = True
    preformStep3 = True
    preformStep4 = True
    preformStep5 = False

    """
    Default is True. If 'False' the code will run without text output unless something unexpected happens.
    the definition of the word verbose (adjective) is 'using or expressed in more words than are needed.'
    """
    verbose = True

    ####################
    ####################
    ###### Step 1 ######
    ####################
    ####################
    """
    Process all and save the results for all pulse data in folders in folderList
    """
    folderList = [
        'CHC alpha_gamma traces']
    # folderList = ['CHC alpha traces',
    #               'CHC alpha traces thrsh 180',
    #               'CHC alpha_gamma traces',
    #               'CHC gamma traces']

    """
    This is the location where the folders with pulse data should be stored on your computer.
    Enter your user name and where the data is located on you computer here.
    For a windows computer the use '\\' for a mac or unix machine use '/'.

    """
    if getpass.getuser() == "chw3k5": # Caleb Wheeler's User name on his own computer
        parentFolder = '/Users/chw3k5/Desktop/new CHC traces'
    elif getpass.getuser() == "youUserName":

        parentFolder = 'Where\\the\\data\\is\\on\\your\\windows\\computer'
    else:
        parentFolder = ''
        print getpass.getuser(), 'is your user name.'


    """
    The output folder is where the process data will be stored on you computer. The default process puts it
    within the 'parentFolder'.
    """
    outputFolder = os.path.join(parentFolder, 'output')
    # automatically create the output folder is it does not yet exist on your computer
    if not os.path.exists(outputFolder):
        os.mkdir(outputFolder)

    """
    This option lets you apply a box car convolution to smooth the pulse data before is it trimmed to the peak.
    smooth smoothChannels=1 DOES NOT apply a convolution and is the default
    """
    smoothChannels=1,


    """
    # When processing the data you can fit with a sum of exponent in the form
    # Amp1 * exp(- x / tau1) + Amp1 * exp(- x / tau1) + ...
    # these can be done currently with 1, 2, 3, or 4 exponential in the sum
    """
    numOfExponents = 2


    """
    These are the data types that will be saved in the output folder after processing.
    Current options include:
    'arrayData' the original array of Voltage data from read in
    'xData' the original array of time data from read in
    'rawDataFileName' the filename that the data was read in from, save as a string of text

    'smoothedData' a boxcar smoothed version of the original array
        (available only if smoothChannels > 1) saves an array of floats
    'keptData' the voltage data that has been trimmed to exclude the baseline data before the pulse
    'keptxData' the corresponding time data that has been trimmed to exclude the baseline data before the pulse

    'integral' the calculated integral of the pulse voltage * time, saves a single float value
    'fittedCost' This is the 'cost' of the fitting function, lower cost is a better fit, saves a single float value

    fittingFunction = Amp1 * exp(- x / tau1) + Amp2 * exp(- x / tau2) + Amp3 * exp(- x / tau3) + Amp4 * exp(- x / tau4)
    'fittedAmp1', amplitude of the first component in the sum of exponential fitting functions, saves a single float value
    'fittedTau1', the time constant of value of the first component in the sum of exponential fitting functions, saves a single float value
    'fittedAmp2', only available if numOfExponents >= 2
    'fittedTau2', only available if numOfExponents >= 2
    'fittedAmp3', only available if numOfExponents >= 3
    'fittedTau3', only available if numOfExponents >= 3
    'fittedAmp4', only available if numOfExponents >= 4
    'fittedTau4', only available if numOfExponents >= 4

    """
    pulseDataTypesToSave = ['integral', 'fittedCost']
    for index in range(numOfExponents):
        pulseDataTypesToSave.extend(['fittedAmp' + str(index + 1), 'fittedTau' + str(index + 1)])
    if verbose:
        print 'The data types to save are:', pulseDataTypesToSave


    """
    Default should be False, as it will take too much time to look at a plot for each individual pulse.
    However this is a great way to visualize the individual pulse data, or test to see how changes in
    the pulse pipeline are being implements
    """
    showTestPlots_Pulses = False


    """
    default should be False. This will limit the number of file to be read in, currently limited to 13 pulse files.
    This can be useful when making changes to the read in, but you do not want to wait for the time it takes to read
    in 1000's of files.
    """
    testModeReadIn = False

    if preformStep1:
        groupDict = doExtractAndSavePulseInfo(parentFolder,
                                              folderList,
                                              outputFolder,
                                              pulseDataTypesToSave,
                                              smoothChannels=smoothChannels,
                                              numOfExponents=numOfExponents,
                                              showTestPlots_Pulses=showTestPlots_Pulses,
                                              testModeReadIn=testModeReadIn,
                                              verbose=verbose)
    ####################
    ####################
    ###### Step 2 ######
    ####################
    ####################
    """
    Load in the saved data. If you are not loading the whole pulse than this goes much faster then the pulse
    processing function.
    """



    """
    The option for pulseDataTypesToLoad are the same options as pulse data type to save.
    This data must be saved first before it can be loaded. So it can be set equal to
    'pulseDataTypesToSave' for most purposes.
    """
    pulseDataTypesToLoad = pulseDataTypesToSave
    if preformStep2:
        groupDict = loadSavedGroupsOfPulses(outputFolder,
                                            folderList,
                                            pulseDataTypesToLoad)

    ####################
    ####################
    ###### Step 3 ######
    ####################
    ####################
    """
    This is used to remove outliers from the data. This uses a method that is simple but effective for pulses that
    have astronomically high values. We use the standard deviation from the median instead of the mean to make us
    able to remove data the has values equal to inanity, float('inf), or that are so high they would skew the mean.
    Each data type is in a tuple with the name and the value of standard deviation from the median such as
    ('cost', 1.37)
    This is available only for things that are one entry per pulse such as
    'integral', 'fittedCost', 'fittedAmp1', 'fittedTau1', 'fittedAmp2' ...
    see the documentation for pulseDataTypesToSave for more information on these types.
    """
    pulseDataTypesToRemoveOutliers = [('integral', float(100)), ('fittedCost', float(4)),
                                      ('fittedAmp1', float(10)), ('fittedTau1', float(10)),
                                      ('fittedAmp2', float(10)), ('fittedTau2', float(10))]

    if preformStep3:
        if preformStep2:
            if verbose:
                print 'Removing outliers from the loaded pulse data. '
            groupDict = removeOutlierPulses(groupDict, pulseDataTypesToRemoveOutliers)
        else:
            print "The data needs to be loaded in step 2 before step 3 can be completed. Try again."



    ####################
    ####################
    ###### Step 4 ######
    ####################
    ####################
    """
    In this step we make histograms for the data types that are one value per pulse. This can help us to make
    choices about what the characteristic values for sets of pulses.
    """



    """
    pulseDataForHistogram, is list of the data type that are to be made into histograms.
    This is available only for things that are one entry per pulse such as
    'integral', 'fittedCost', 'fittedAmp1', 'fittedTau1', 'fittedAmp2' ...
    see the documentation for pulseDataTypesToSave for more information on these types.
    """
    pulseDataForHistogram = []
    for (pulseType, number) in  pulseDataTypesToRemoveOutliers:
        pulseDataForHistogram.append(pulseType)


    """
    This is the location of the folder where the histogram plots are stored. If it does not exist it will
    be made automatically at this point.
    """
    plotFolder = os.path.join(parentFolder, 'plots')
    if not os.path.exists(plotFolder):
        os.mkdir(plotFolder)

    """
    showHistPlots toggles is the histogram plots are to be shown in a pop up window.
    """
    showHistPlots = False


    """
    saveHistPlots toggles is the histogram plots save it the folder 'plotFolder'.
    """
    saveHistPlots = False


    """
    Specifies the number of bins for all histograms.
    """
    histBins = 20

    if preformStep4:
        if preformStep2:
            if verbose:
                print 'Making histograms of the pulse data.'
            outHistDict = makeGroupHistograms(groupDict,
                                              pulseDataTypesToSave,
                                              plotFolder,
                                              saveHistPlots=saveHistPlots,
                                              showHistPlots=showHistPlots,
                                              verbose=verbose)
        else:
            print "The data needs to be loaded in step 2 before step 3 can be completed. Try again."






    if False:
        # Disabled for not Not working as well enough for prime time.
        errFactorForPeakFinder = 0
        smoothIndexesForPeakFinder = 1
        doFindHistPeaks(outHistDict, errFactorForPeakFinder, smoothIndexesForPeakFinder, verbose)