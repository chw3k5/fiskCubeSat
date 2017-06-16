"""
This code for Chris Precod's Summer RUE project.
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

def parseData(contentList, typesList, delimiter=','):
    # Remove whitespace characters and return characters like \n and \r at the end of each line
    contentList = [x.replace(' ', '').strip() for x in contentList]
    typesList = [x.replace(' ', '').strip() for x in typesList]

    # initialize the output dictionary
    dataDict = {}
    for dataType in typesList:
        # make each dictionary entry be an empty list that can later be appended to.
        dataDict[dataType] = []

    # put the data in the dictionary
    for singleDatum in contentList:
        # split the data into the type and the value
        dataType, value = singleDatum.split(delimiter)
        if dataType in typesList:
            # if the data is a number turn it into a float from a string
            value = isNum(value)
            # append the data to the list of data in the dictionary for that data type.
            dataDict[dataType].append(value)
    return dataDict


def plotParedData(dataDict):
    # make empty list for the legend lines and label
    leglines = []
    leglabels = []

    # loop through all the dat types.
    for dataType in dataDict.keys():
        # assign special parameters for each data type.
        if dataType == 'voltage':
            color = 'green'
        elif dataType == 'degF':
            color = 'firebrick'
        elif dataType == 'degC':
            color = 'dodgerblue'
        elif dataType == 'degK':
            color = 'darkOrchid'
        else:
            color = 'black'

        # append the legend line to a list to use later.
        leglines.append(plt.Line2D(range(10), range(10), color=color))

        # append the legend label to a list to use later.
        leglabels.append(dataType)

        # plot the data
        plt.plot(dataDict[dataType], color=color)

    # make the legend
    plt.legend(leglines,leglabels, loc=0, numpoints=3, handlelength=4)

    # make a label for the x axis
    plt.xlabel("Number of points")

    # make a label for the y axis
    plt.ylabel("Data Values")

    # display the plot in pop-up window
    plt.show()
    return


if __name__ == "__main__":
    dataTypes = ['voltage', 'degC', 'degF', 'degK']
    delimiter = ':'

    # the filename
    fileName = "Serial Monitor Data.txt"

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
    dataDict = parseData(contentList=contentList, typesList=dataTypes, delimiter=delimiter)

    # plot the parsed data
    plotParedData(dataDict)






