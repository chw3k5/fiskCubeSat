"""
This code for John Tomhas' Summer RUE project.
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


class coordinatesWithUnits():
    def __init__(self, coordinates, unit = None):
        self.coordinates = coordinates
        self.unit = unit


class coordinatesListWithUnits():
    def __init__(self, coordinatesList):
        unitsTypes = []
        unitDict = {}
        self.coordinatesList = []
        for coordinates in coordinatesList:
            unit = coordinates.unit
            coordinateTuple = coordinates.coordinates
            if unit in unitsTypes:
                unitDict[unit].append(coordinateTuple)
            else:
                unitsTypes.append(unit)
                unitDict[unit] = [coordinateTuple]
        keys = unitDict.keys()
        if len(keys) == 1:
            self.units = keys[0]
            self.coordinatesList = unitDict[self.units]
        else:
            print 'Warning, multiple units detected:', keys
            print "returning a unit dictionary (self.unitDict) is place of the coordinatesList (self.coordinatesList)"
            self.unitDict = unitDict


def readInData(longFileName):
    # Read the file line by line an pu the elements into a list
    with open(longFileName) as f:
        content = f.readlines()
    return content


def parseData(contentList, typesList, unitsTypes, delimiter=','):
    # Remove whitespace characters and return characters like \n and \r at the end of each line
    contentList = [x.replace(' ', '').strip() for x in contentList]
    typesList = [x.replace(' ', '').strip() for x in typesList]

    # get rid of blank lines
    contentList = [x for x in contentList if x != '']

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
            # find out if there are units in the value
            unit = None
            for unitType in unitsTypes:
                if unitType in value:
                    # save the unit type for later
                    unit = unitType
                    # take this out of the value now that we found the unit
                    value = value.replace(unit, '')
                    # stop the loop since we found what we are looking for
                    break

            # find out if the data is a set of several numbers
            preTupleStringList = value.split(',')

            preTupleList = []
            for singleStringValue in preTupleStringList:
                # turn the values in a vector into number if possible
                preTupleList.append(isNum(singleStringValue))
            # turn the list into tuple
            aTuple = tuple(preTupleList)
            # use the coordinatesWithUnits with units class to save this information
            aCoordinate = coordinatesWithUnits(coordinates=aTuple, unit=unit)
            # Append this data to the dictionary
            dataDict[dataType].append(aCoordinate)
    # most of these should only have one unit, here we check that.
    keys = dataDict.keys()
    for key in keys:
        dataDict[key] = coordinatesListWithUnits(coordinatesList=dataDict[key])
    return dataDict


def plotParedData(dataDict):


    # loop through all the dat types.
    for dataType in dataDict.keys():
        # make empty list for the legend lines and label
        leglines = []
        leglabels = []
        # assign special parameters for each data type.

        # linear acceleration
        if dataType == 'A':
            (xAccelList, yAccelList, zAccelList) = ([], [], [])
            coordinatesList = dataDict[dataType].coordinatesList
            for (xAccel, yAccel, zAccel) in coordinatesList:
                xAccelList.append(xAccel)
                yAccelList.append(yAccel)
                zAccelList.append(zAccel)
            listOfPlotLists = [xAccelList, yAccelList, zAccelList]
            # choose the colors
            colors = ['firebrick', 'dodgerblue', 'darkorchid']
            # add things to the legend labels
            legLabelSeeds = [' x ', ' y ', ' z ']
            units = dataDict[dataType].units
            if units is None:
                units = ''
            # make a label for the y axis
            plt.ylabel("Acceleration (" + str(units) + ")")
            # make a title
            plt.title('Linear Acceleration')

        # rotation rate
        elif dataType == 'G':
            (xRotationRateList, yRotationRateList, zRotationRateList) = ([], [], [])
            coordinatesList = dataDict[dataType].coordinatesList
            for (xRotRate, yRotRate, zRotRate) in coordinatesList:
                xRotationRateList.append(xRotRate)
                yRotationRateList.append(yRotRate)
                zRotationRateList.append(zRotRate)
            listOfPlotLists = [xRotationRateList, yRotationRateList, zRotationRateList]
            colors = ['DarkGoldenRod', 'OliveDrab', 'Tomato']
            # add things to the legend labels
            legLabelSeeds = [' x Rotation Rate ', ' y Rotation Rate ', ' z Rotation Rate ']
            units = dataDict[dataType].units
            if units is None:
                units = ''
            # make a label for the y axis
            plt.ylabel("Rotation Rate (" + str(units) + ")")
            # make a title
            plt.title('Rotation Rate About Different Axes')

        # magnetic Field
        elif dataType == 'M':
            (xMagFieldList, yMagFieldList, zMagFieldList) = ([], [], [])
            coordinatesList = dataDict[dataType].coordinatesList
            for (xMagField, yMagField, zMagField) in coordinatesList:
                xMagFieldList.append(xMagField)
                yMagFieldList.append(yMagField)
                zMagFieldList.append(zMagField)
            listOfPlotLists = [xMagFieldList, yMagFieldList, zMagFieldList]
            colors = ['CadetBlue', 'Chartreuse', 'Pink']
            # add things to the legend labels
            legLabelSeeds = [' x Magnetic Field ', ' y Magnetic Field ', ' z Magnetic Field ']
            units = dataDict[dataType].units
            if units is None:
                units = ''
            # make a label for the y axis
            plt.ylabel("Magnetic Field (" + str(units) + ")")
            # make a title
            plt.title('3 Axis Magnetic Field')

        elif dataType == 'Pitch,Roll':
            (pitchList, rollList) = ([], [])
            coordinatesList = dataDict[dataType].coordinatesList
            for (pitch, roll) in coordinatesList:
                pitchList.append(pitch)
                rollList.append(roll)

            listOfPlotLists = [pitchList, rollList]
            colors = ['Chocolate', 'CornflowerBlue']
            # add things to the legend labels
            legLabelSeeds = [' pitch ', ' roll ']
            units = dataDict[dataType].units
            if units is None:
                units = ''
            # make a label for the y axis
            plt.ylabel("Pitch and Roll " + units)
            # make a title
            plt.title('Pitch and Roll')

        else:
            coordinatesList = dataDict[dataType].coordinatesList
            dataList = []
            for datum in coordinatesList:
                dataList.append(datum)
            listOfPlotLists = [dataList]
            colors = ['Sienna']
            # add things to the legend labels
            legLabelSeeds = [' ']
            units = dataDict[dataType].units
            if units is None:
                units = ''
            # make a label for the y axis
            plt.ylabel(dataType + units)
            # make a title
            plt.title(dataType)



        for (listIndex, dataList) in list(enumerate(listOfPlotLists)):
            color = colors[listIndex]
            # append the legend label to a list to use later.
            leglabels.append(dataType + ':' + legLabelSeeds[listIndex])
            # append the legend line to a list to use later.
            leglines.append(plt.Line2D(range(10), range(10), color=color))
            # plot the data
            plt.plot(dataList, color=color)

        # make the legend
        plt.legend(leglines,leglabels, loc=0, numpoints=3, handlelength=4)

        # make a label for the x axis
        plt.xlabel("Number of points")



        # display the plot in pop-up window
        plt.show()
    return


if __name__ == "__main__":
    dataTypes = ['G', 'A', 'M', 'Pitch,Roll', 'Heading']
    # Important 'g' must go after 'gauss' since 'g' is in the string 'gauss'
    unitsTypes = ['deg/s', 'gauss', 'g']
    delimiter = ':'

    # the filename
    fileName = "accel.txt"

    # This can be used to store data the is specific to different users, such as data location.
    if getpass.getuser() == "chw3k5": # Caleb Wheeler's User name on his own computer
        # This is the location where the folders with pulse data should be stored on your computer.
        longFileName = os.path.join("/Users", "chw3k5", "Downloads", fileName)
    elif getpass.getuser() == "jTomhas": # John Tomhas' User name on his own computer
        # This is the location where the folders with pulse data should be stored on your computer.
        longFileName = os.path.join("C:", "jTomhas", "Downloads", fileName)
    else:
        # write out all the directories that lead your filename, enclosed in quotes and separated by Commas
        longFileName = os.path.join("C:", "downloads", fileName)
        print getpass.getuser(), 'is your user name.'

    # read in the data
    contentList = readInData(longFileName=longFileName)

    # parse the data into a dictionary
    dataDict = parseData(contentList=contentList, typesList=dataTypes, unitsTypes=unitsTypes, delimiter=delimiter)

    # plot the parsed data
    plotParedData(dataDict)






