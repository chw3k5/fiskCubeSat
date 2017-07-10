import os
import getpass


def isNum(testNum):
    try:
        return float(testNum)
    except:
        return testNum


def readInData(longFileName):
    # Read the file line by line an pu the elements into a list
    with open(longFileName) as f:
        content = f.readlines()
    return content


def parseData(contentList, flagsForData=['TIME,CH1']):
    delimiter = ','

    # Remove whitespace characters and return characters like \n and \r at the end of each line
    contentList = [x.replace(' ', '').strip() for x in contentList]

    # save all the header info in a dictionary
    headerDict = {}
    flagForData = None
    dataStartIndex = 0
    for (dataIndex, dataLine) in list(enumerate(contentList)):
        if dataLine in flagsForData:
            flagForData = dataLine
            dataStartIndex = dataIndex + 1
            break
        try:
            headerType, headerValue = dataLine.split(delimiter)
            headerDict[headerType] = isNum(headerValue)
        except:
            pass

    ### save and parse the data dictionary

    # initialize the data dictionary.
    dataDict = {}
    IndexToType = {}
    for (typeIndex, dataType) in list(enumerate(flagForData.split(delimiter))):
        dataDict[dataType] = []
        IndexToType[typeIndex] = dataType

    # assign the data values to the appropriate spot in the data dictionary
    for dataLine in contentList[dataStartIndex:]:

        listForDataLine = dataLine.split(delimiter)
        for (datumIndex, datum) in list(enumerate(listForDataLine)):
            if datum == '':
                break
            dataDict[IndexToType[datumIndex]].append(isNum(datum))


    return headerDict, dataDict




if __name__ == "__main__":
    # the filenames
    fileNames = ["T0000.CSV", "T0001.CSV", "T0002.CSV"]

    for fileName in fileNames:
        # This can be used to store data the is specific to different users, such as data location.
        if getpass.getuser() == "chw3k5": # Caleb Wheeler's User name on his own computer
            # This is the location where the folders with pulse data should be stored on your computer.
            longFileName = os.path.join("/Users", "chw3k5", "Downloads", fileName)
        else:
            # write out all the directories that lead your filename, enclosed in quotes and separated by Commas
            longFileName = os.path.join("C:", "downloads", fileName)
            print getpass.getuser(), 'is your user name.'

        # read in the data
        contentList = readInData(longFileName=longFileName)

        # parse the data into a dictionary
        headerDict, dataDict = parseData(contentList, flagsForData=['TIME,CH1', 'TIME,CH2'])
