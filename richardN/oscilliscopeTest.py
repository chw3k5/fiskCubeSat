"""
This code for Richard Nederlander's Summer RUE project.
This test code will need to be packaged some where else when it is completed

"""

import os
import getpass
from matplotlib import pyplot as plt


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



def plotParedData(headerDict, dataDict):
    xAxisKey = 'TIME'

    # make empty list for the legend lines and label
    leglines = []
    leglabels = []

    # get all the keys for the data
    dataKeys = dataDict.keys()

    xData = None
    # get the x axis data
    if xAxisKey in dataKeys:
        xData = dataDict[xAxisKey]
        dataKeys.remove(xAxisKey)


    # loop through all the dat types.
    for dataType in dataKeys:
        # assign special parameters for each data type.
        if dataType == 'CH1':
            color = 'firebrick'
        elif dataType == 'Ch2':
            color = 'dodgerblue'
        else:
            color = 'black'

        # append the legend line to a list to use later.
        leglines.append(plt.Line2D(range(10), range(10), color=color))

        # append the legend label to a list to use later.
        leglabels.append(dataType)

        # plot the data
        if xData is None:
            plt.plot(dataDict[dataType], color=color)
        else:
            plt.plot(xData, dataDict[dataType], color=color)

    # make the legend
    plt.legend(leglines,leglabels, loc=0, numpoints=3, handlelength=4)

    # make a label for the x axis
    plt.xlabel(headerDict['HorizontalUnits'])

    # make a label for the y axis
    plt.ylabel(headerDict['VerticalUnits'])

    # display the plot in pop-up window
    plt.show()
    return



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

        # make a simple plot
        plotParedData(headerDict, dataDict)


