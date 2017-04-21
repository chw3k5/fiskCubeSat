import string, numpy, os, glob
from operator import itemgetter

from dataGetter import getTableData


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


def loadPulses(folderName, fileNamePrefix='', filenameSuffix='',
               skipRows=1, delimiter=',', testMode=False, verbose=True):
    searchString = fileNamePrefix +  "*" + filenameSuffix
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
                      saveAsColumns=False, verbose=False):
    # save the trimmed data
    if verbose:
        print "\nDeleting old output files..."
    deleteOutputFiles(fileBase=outPutFileBase)
    if verbose:
        print "\nSaving data in one file named " + outPutFileBase + ".\n"
    numOfHeaders = len(listOfHeaderNames)
    numberOfOutputFiles = int(numpy.ceil(float(numOfHeaders) / float(maxDataArraysPerFile)))

    listOfLengths = []
    for (arrayIndex, dataArray) in list(enumerate(listOfArrays)):
        listOfLengths.append(len(dataArray))

    if saveAsColumns:
        # minLength = numpy.min(listOfLengths)
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
        outputFileName = getNextOutputFile(outPutFileBase)
        outputFileHandle = open(outputFileName, 'w')
        modLen = int(numOfHeaders / 200.0)
        for (headerIndex, header) in list(enumerate(listOfHeaderNames)):
            dataString = ""
            for dataValue in listOfArrays[headerIndex]:
                dataString += delimiter + str(dataValue)
            outputFileHandle.write(str(header) + dataString + '\n')
            if verbose:
                if headerIndex % modLen == 0:
                    print "File writing is " + str('%02.2f' % (headerIndex * 100.0 / float(numOfHeaders))) + " % complete."
        outputFileHandle.close()
    return






