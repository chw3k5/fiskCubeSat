import string, numpy, os, glob
from operator import itemgetter

from dataGetter import getTableData, getTableRowData


def getOutPutFiles(fileBase, isCSV=False, isSeries=True):
    if isCSV:
        fileSuffix = '.csv'
    else:
        fileSuffix = '.txt'
    if isSeries:
        count = 1
        fileName = fileBase + str(count) + fileSuffix
        fileNames = []
        while os.path.isfile(fileName):
            fileNames.append(fileName)
            count += 1
            fileName = fileBase + str(count) + fileSuffix
    else:
        fileName = fileBase + fileSuffix
        fileNames = [fileName]
    return fileNames


def deleteOutputFiles(fileBase, isCSV=False, isSeries=True):
    for fileName in getOutPutFiles(fileBase, isCSV, isSeries):
        os.remove(fileName)
    return


def getNextOutputFile(fileBase, isCSV=False, isSeries=True):
    if isCSV:
        fileSuffix = '.csv'
    else:
        fileSuffix = '.txt'
    if isSeries:
        count = 1
        fileName = fileBase + str(count) + fileSuffix
        while os.path.isfile(fileName):
            count += 1
            fileName = fileBase + str(count) + fileSuffix
    else:
        fileName = fileBase + fileSuffix
    return fileName


def readInSavedRowData(fileName, pulseDataType, listOfPulseDicts=[]):
    # create the uniqueID list from list of existing pulse dictionaries.
    uniqueIDList = []
    for pulseDict in listOfPulseDicts:
        uniqueIDList.append(pulseDict['uniqueID'])
    # read-in and get the data table to assign to pulse dictionaries.
    tableDict = getTableRowData(fileName)
    # test to make sure is this data can be mapped to an existing pulse dictionary
    IDsThisTable = tableDict.keys()
    for testID in IDsThisTable:
        if testID in uniqueIDList:
            # This is the case where the uniqueID corresponds to an existing pulse dictionary
            listIndex = uniqueIDList.index(testID)
            pulseDict = listOfPulseDicts[listIndex]
            pulseDict[pulseDataType] = tableDict[testID]
        else:
            uniqueIDList.append(testID)
            listOfPulseDicts.append({'uniqueID':testID, pulseDataType:tableDict[testID]})
    return listOfPulseDicts


def loadPulses(folderName, fileNamePrefix='', filenameSuffix='',
               skipRows=1, delimiter=',', testMode=False, verbose=True):
    searchString = fileNamePrefix + "*" + filenameSuffix
    if verbose:
        print "\nLoading data from the folder " + folderName + "."
        print "Using '" + searchString + "' as the search sting.\n"
    fileNames = glob.glob(os.path.join(folderName, searchString))
    # set the part of the filename that is unique for each file.
    uniqueFileIds = []
    for fileName in fileNames:
        if fileNamePrefix == "":
            IDandSuffix = fileName
        else:
            trash, IDandSuffix = string.split(fileName, fileNamePrefix)
        if filenameSuffix == "":
            uniqueID = IDandSuffix
        else:
            uniqueID, trash = string.split(IDandSuffix, filenameSuffix)
        uniqueFileIds.append((uniqueID, fileName))
    # Sort the unique parts of each file
    sortedIDs = sorted(uniqueFileIds, key=itemgetter(0))
    numOfFiles = len(sortedIDs)
    modLen = max((int(numOfFiles / 200.0), 1))
    listOfDataDicts = []
    for (IDindex, (uniqueID, fileName)) in list(enumerate(sortedIDs)):
        if verbose:
            if IDindex % modLen == 0:
                print "File read-in is " \
                      + str('%02.2f' % (IDindex*100.0/float(numOfFiles))) + " % complete."
        tableDict = getTableData(fileName, skiprows=skipRows, delimiter=delimiter)
        tableDict['fileName'] = fileName
        tableDict['uniqueID'] = uniqueID
        listOfDataDicts.append(tableDict)
        if (testMode and (IDindex == 9)):
            break
    return listOfDataDicts


def saveProcessedData(listOfHeaderNames, listOfArrays, outPutFileBase,
                      maxDataArraysPerFile=20, delimiter=',',
                      saveAsColumns=False, appendMode=False, verbose=False):
    # save the trimmed data
    if not appendMode:
        if verbose:
            print "\nDeleting old output files..."
        deleteOutputFiles(fileBase=outPutFileBase)
    if verbose:
        print "\nSaving data a file named " + outPutFileBase + ".\n"
    numOfHeaders = len(listOfHeaderNames)
    numberOfOutputFiles = int(numpy.ceil(float(numOfHeaders) / float(maxDataArraysPerFile)))


    listOfLengths = []
    for (arrayIndex, dataArray) in list(enumerate(listOfArrays)):
        try:
            listOfLengths.append(len(dataArray))
        except TypeError:
            listOfLengths.append(1)

    if saveAsColumns:
        # minLength = numpy.min(listOfLengths)
        maxLength = numpy.min(listOfLengths)
        for jobIndex in range(numberOfOutputFiles):
            startIndex = jobIndex * maxDataArraysPerFile
            endIndex = min(((jobIndex + 1) * maxDataArraysPerFile, numOfHeaders))
            jobHeaderIndexes = range(startIndex, endIndex)

            outputFileName = getNextOutputFile(outPutFileBase, isCSV = delimiter==',', isSeries = numberOfOutputFiles>1)
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
                        dataValue = listOfArrays[headerIndex][listIndex]
                    else:
                        # the last value in the list
                        dataValue = listOfArrays[headerIndex][-1]
                    dataString += str(dataValue) + delimiter
                dataString.strip(delimiter)
                outputFileHandle.write(str(dataString) + '\n')
            outputFileHandle.close()
            if verbose:
                print "File writing is " + str('%02.2f' % ((jobIndex + 1)  * 100.0 / float(numberOfOutputFiles))) + " % complete."
    else:
        outputFileName = getNextOutputFile(outPutFileBase, isCSV=delimiter==',', isSeries=False)
        if appendMode:
            outputFileHandle = open(outputFileName, 'a')
        else:
            outputFileHandle = open(outputFileName, 'w')
        modLen = max((int(numOfHeaders / 200.0), 1))
        for (headerIndex, header) in list(enumerate(listOfHeaderNames)):
            data = listOfArrays[headerIndex]
            try:
                dataString = delimiter + str(data).replace(' ', '').replace(',', delimiter)[1:-1]
            except TypeError:
                dataString = delimiter + str(data)
            outputFileHandle.write(str(header) + dataString + '\n')
            if verbose:
                if headerIndex % modLen == 0:
                    print "File writing is " + str('%02.2f' % (headerIndex * 100.0 / float(numOfHeaders))) + " % complete."
        outputFileHandle.close()
    return






