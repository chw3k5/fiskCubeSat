import string, numpy, getpass, os, glob
from operator import itemgetter

from dataGetter import getTableData
from quickPlots import quickPlotter



def getOutPutFiles(fileBase):
    count = 1
    fileName = fileBase + str(count) + '.txt'
    fileNames = []
    while os.path.isfile(fileName):
        fileNames.append(fileName)
        count += 1
        fileName = fileBase + str(count) + '.txt'
    return fileNames

def deleteOutputFiles(fileBase):
    for fileName in getOutPutFiles(fileBase):
        os.remove(fileName)
    return

def getNextOutputFile(fileBase):
    count = 1
    fileName = fileBase + str(count) + '.txt'
    while os.path.isfile(fileName):
        count +=1
        fileName = fileBase + str(count) + '.txt'
    return fileName

def trimAndSave(folderName, fileNamePrefix='', filenameSuffix='',
                columnNamesToRemove=['time'], skipRows=1, delimiter=',',
                trimBeforeMin=True,
                conv_channels=1,
                outPutFileBase='trimmedData.csv', saveAsColumns=True, maxDataArraysPerFile=100,
                showTestPlots=False,
                testMode=False,
                verbose=True):
    searchString = fileNamePrefix +  "*" + filenameSuffix
    fileNames = glob.glob(os.path.join(folderName, searchString))

    # set the part of the filename that is unique for each file.
    uniqueFileIds = []
    for fileName in fileNames:
        if fileNamePrefix == "":
            IDandSuffix = fileName
        else:
            trash, IDandSuffix = string.split(fileName, fileNamePrefix)

        if filenameSuffix == "":
            uniquieID = IDandSuffix
        else:
            uniquieID, trash = string.split(IDandSuffix, filenameSuffix)
        uniqueFileIds.append((uniquieID, fileName))

    # Sort the unique parts of each file
    sortedIDs = sorted(uniqueFileIds, key=itemgetter(0))

    listOfTrimmedDataArrays = []
    listOfHeaderNames = []
    listOfLengths = []
    numOfFiles = len(sortedIDs)
    modLen = max((int(numOfFiles / 200.0), 1))
    if verbose:
        print "\nLoading data from the folder " + folderName + "."
        if conv_channels > 1:
            print "The data is to be smoothed with a top hat kernel of " + str(conv_channels) + " channels."
        if trimBeforeMin:
            print "All the data values before the minimum value will be trimmed away before being saved."
        print " "
    for (IDindex, (uniquieID, fileName)) in list(enumerate(sortedIDs)):
        if showTestPlots:
            plotDict = {}
            plotDict['verbose'] = verbose
            # These must be a single value
            plotDict['title'] = 'Pulse Data Read in and Trim.'
            plotDict['xlabel'] = 'Time'
            plotDict['ylabel'] = 'Voltage'
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


        if verbose:
            if IDindex % modLen == 0:
                print "File read-in and operations are " + str('%02.2f' % (IDindex*100.0/float(numOfFiles))) + " % complete."
        tableDict = getTableData(fileName, skiprows=skipRows, delimiter=delimiter)

        # Get rid of unwanted columns
        xData = None
        for key in tableDict.keys():
            for columnNameToRemove in columnNamesToRemove:
                if key.lower() == columnNameToRemove.lower():
                    if key.lower() == 'time':
                        xData = tableDict[key]
                    del tableDict[key]
        for key in tableDict.keys():
            header = key.replace(' ', '_') + '_' + uniquieID
            listOfHeaderNames.append(header)

            arrayData = tableDict[key]
            if showTestPlots:
                # These can be a list or a single value
                plotDict['yData'].append(arrayData)
                if xData is None:
                    plotDict['xData'].append(range(len(arrayData)))
                else:
                    plotDict['xData'].append(xData)
                plotDict['legendLabel'].append('Read In Data')
                plotDict['fmt'].append('None')
                plotDict['markersize'].append(6)
                plotDict['alpha'].append(1.0)
                plotDict['ls'].append('solid')
                plotDict['lineWidth'].append(2)

            # smooth the data
            if conv_channels > 1:
                kernel1 = numpy.ones(conv_channels)
                # gsd stands for generalized second derivative
                smoothedData = numpy.convolve(arrayData, kernel1, 'same')
                if showTestPlots:
                # These can be a list or a single value
                    plotDict['yData'].append(arrayData)
                    if xData is None:
                        plotDict['xData'].append(range(len(smoothedData)))
                    else:
                        plotDict['xData'].append(xData)
                    plotDict['legendLabel'].append('Smoothed Data, n=' + str(conv_channels))
                    plotDict['fmt'].append('None')
                    plotDict['markersize'].append(6)
                    plotDict['alpha'].append(1.0)
                    plotDict['ls'].append('dotted')
                    plotDict['lineWidth'].append(1)

            else:
                smoothedData = arrayData

            # trim all the data prior to the minimum
            if trimBeforeMin:
                # trim the data before the minimum value
                dataMinIndex = numpy.argmin(smoothedData)
                keptData = arrayData[dataMinIndex:]
                if showTestPlots:
                    # These can be a list or a single value
                    plotDict['yData'].append(keptData)
                    if xData is None:
                        plotDict['xData'].append(range(len(keptData)))
                    else:
                        plotDict['xData'].append(xData[dataMinIndex:])
                    plotDict['legendLabel'].append('trimmed data')
                    plotDict['fmt'].append('None')
                    plotDict['markersize'].append(6)
                    plotDict['alpha'].append(1.0)
                    plotDict['ls'].append('dashed')
                    plotDict['lineWidth'].append(1)
            else:
                keptData = smoothedData
            listOfTrimmedDataArrays.append(keptData)
            listOfLengths.append(len(keptData))


        if showTestPlots:
            quickPlotter(plotDict=plotDict)

        if (testMode and (IDindex == 9)):
             break

    # save the trimmed data
    if verbose:
        print "\nDeleting old output files..."
    deleteOutputFiles(fileBase=outPutFileBase)
    
    if verbose:
        print "\nSaving data in one file named " + outPutFileBase + ".\n"
    numOfHeaders = len(listOfHeaderNames)
    numberOfOutputFiles = int(numpy.ceil(float(numOfHeaders) / float(maxDataArraysPerFile)))


    if saveAsColumns:
        minLength = numpy.min(listOfLengths)
        maxLength = numpy.min(listOfLengths)
        for jobIndex in range(numberOfOutputFiles):
            startIndex = jobIndex * maxDataArraysPerFile
            endIndex = min(((jobIndex + 1) * maxDataArraysPerFile, numOfHeaders))
            jobHeaderIndexes = range(startIndex, endIndex)

            outputFileName = getNextOutputFile(outPutFileBase)
            outputFileHandle = open(outputFileName, 'w')

            headerString = ''
            for headerIndex in jobHeaderIndexes:
                headerName = listOfHeaderNames[headerIndex]
                headerString += headerName + delimiter
                headerString.strip(delimiter)
            outputFileHandle.write(headerString + '\n')

            for listIndex in range(maxLength):
                dataString = ""
                for headerIndex in jobHeaderIndexes:
                    # test to see to the row number (denoted by the list index) is greater then
                    # the size of the trimmed data
                    if listIndex < listOfLengths[headerIndex]:
                        dataValue = listOfTrimmedDataArrays[headerIndex][listIndex]
                    else:
                        # the last value in the list
                        dataValue = listOfTrimmedDataArrays[headerIndex][-1]
                    dataString += str(dataValue) + delimiter
                dataString.strip(delimiter)
                outputFileHandle.write(str(dataString) + '\n')
            outputFileHandle.close()
            if verbose:
                print "File writing is " + str('%02.2f' % ((jobIndex + 1)  * 100.0 / float(numberOfOutputFiles))) + " % complete."



    else:
        outputFileName = getNextOutputFile(outPutFileBase)
        outputFileHandle = open(outputFileName, 'w')
        modLen = int(numOfFiles / 200.0)
        for (headerIndex, header) in list(enumerate(listOfHeaderNames)):
            dataString = ""
            for dataValue in listOfTrimmedDataArrays[headerIndex]:
                dataString += delimiter + str(dataValue)
            outputFileHandle.write(str(header) + dataString + '\n')
            if verbose:
                if headerIndex % modLen == 0:
                    print "File writing is " + str('%02.2f' % (headerIndex * 100.0 / float(numOfHeaders))) + " % complete."
        outputFileHandle.close()


    return






if __name__ == "__main__":
    # folderList = [
    #     'CHC alpha traces',
    #     'CHC alpha traces thrsh 180',
    #     'CHC alpha_gamma traces',
    #     'CHC gamma traces']
    folderList = [
        'CHC alpha traces']

    for singleFolder in folderList:
        if getpass.getuser() == "chw3k5": # Caleb Wheeler's User name on his own computer
            parentFolder = '/Users/chw3k5/Desktop/new CHC traces'
        else:
            parentFolder = ''
        folderName = os.path.join(parentFolder, singleFolder)
        outPutFileBase = os.path.join(parentFolder, singleFolder + '_trimmedData')



        trimAndSave(folderName=folderName,
                    fileNamePrefix=singleFolder + '_',
                    filenameSuffix='.txt',
                    columnNamesToRemove=['time'],
                    skipRows=3,
                    delimiter='\t',
                    trimBeforeMin=True,
                    conv_channels=5,
                    outPutFileBase=outPutFileBase,
                    saveAsColumns=True,
                    maxDataArraysPerFile=100,
                    showTestPlots=False,
                    testMode = False,
                    verbose=True)