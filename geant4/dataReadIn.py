import os
import getpass


### A set of tools for unit conversion
conversionToMeters = {'km': float(1e3), 'm': float(1), 'cm': float(1e-2), 'mm': float(1e-3), 'um': float(1e-6),
                      'nm': float(1e-9), 'fm': float(1e-12)}

conversionTo_eV = {'TeV': float(1e12), 'GeV': float(1e9), 'MeV': float(1e6), 'keV': float(1e3), 'eV': float(1)}


def getConversionFactor(unit):
    if unit in conversionToMeters.keys():
        return conversionToMeters[unit], 'm'
    elif unit in conversionTo_eV.keys():
        return conversionTo_eV[unit], 'eV'
    else:
        print "unit not found:", unit
        return None, 'notFound'


### one of my favorite defs for read in that turns strings that are numbers into floats.
def isNum(testNum):
    try:
        return float(testNum)
    except:
        return testNum


"""
Read in the data, this is super general and works for many files.
It simply returns the contents of a file where each line is a single element in a list.
"""
def readInData(longFileName):
    # Read the file line by line an pu the elements into a list
    with open(longFileName) as f:
        content = f.readlines()
    return content


"""
The Geant4 output parsing code was so complicated I put the tools to make the dictonaries for secondary particles
in a new definition to make the code more readable.
"""
def secondaryParticleDict(secondaryContentList, secondaryIndexToKeyList):
    secondaryDict = {}
    startFlag = 'List of 2ndaries'


    for singleLine in secondaryContentList:
        if startFlag in singleLine:
            dataline = singleLine.replace(':', '').replace('-', '').strip().replace(startFlag, '').replace(')', '').replace(' ', '').replace('(', ',')
            for datum in dataline.split(','):
                key, value = datum.split('=')
                secondaryDict[key] = value
            for key in secondaryIndexToKeyList:
                secondaryDict[key] = []
        else:
            dataline = singleLine.replace(':', '').strip().replace(' opticalphoton', '  opticalphoton')
            while '   ' in dataline:
                dataline = dataline.replace('   ', '  ')
            for (index, valueAndUnit) in list(enumerate(dataline.split('  '))):
                key = secondaryIndexToKeyList[index]
                if ' ' in valueAndUnit:
                    value, unit = valueAndUnit.split(' ')

                    #also not right yet
                    secondaryDict[key].append((isNum(value), unit))

                else:
                    secondaryDict[key].append(isNum(valueAndUnit))

    return secondaryDict



def parseData(contentList):
    """
    This is definition is for processing the output file of the Geant 4 code. It is named as a .out file.

    :param contentList: is simply a list of all the lines in the .out file.
    :return:
    """

    """
    The output file can be divided into two parts. The first part gives all the initial states that the code used to
    run. The second part of the output shows that path of all the photons. These two parts are expected to be
    seporable by a single line specified by the 'outputKey' variable defined below. The line containing the
    outputKey is not stored.
    """
    # this is the key that separates the two part of the .out file
    outputKey = 'G4WT0 > \n'

    # Below is list where the initial input data for the simulation will be stored
    initParamsList = []

    # Below is list where the output data about the fate of photons is stored
    outputList = []

    # this variable is False until the outputKey line is read in contentList
    startOutputList = False
    for singleLine in contentList:
        if singleLine == outputKey:
            startOutputList = True
        else:
            lineToSave = singleLine.strip()
            # this is to ignore lines of all the '*' character
            if lineToSave[-2:] != '**':
                if startOutputList:
                    outputList.append(lineToSave.replace('G4WT0 > ', '').strip())
                else:
                    initParamsList.append(lineToSave)

    ###################################
    ### initParamsList data parsing ###
    ###################################
    pass

    ###############################
    ### outputList data parsing ###
    ###############################
    # Below are some variables that need to be initialized.
    masterParticleList = []
    currentParticleDict = None
    secondaryParticleDictNumber = 1
    startSecondaryList = True
    secondaryContentList = None
    firstDict = True
    for singleLine in outputList:
        # this is the trigger for a new particle
        if singleLine[0] == '*':
            # the first time through there is no dictionary started to append to this list.
            if firstDict:
                firstDict = False
            else:
                masterParticleList.append(currentParticleDict)
            currentParticleDict = {}
            secondaryParticleDictNumber = 0
            particleIDList = singleLine.replace('* G4Track Information:', '').strip().split(',')
            for idKeyAndValue in particleIDList:
                key, value = idKeyAndValue.strip().split(' = ')
                currentParticleDict[key] = isNum(value)

        # This records tha data for the header of single step data
        elif singleLine[:5] == 'Step#':
            keys = singleLine.split()
            indexToKeyList = []
            for key in keys:
                currentParticleDict[key] = []
                indexToKeyList.append(key)

        # This gets all the steps that a particle takes on it's path
        elif type(isNum(singleLine[0])) == float:
            dataline = singleLine
            while '   ' in dataline:
                dataline = dataline.replace('   ', '  ')
            dataline = dataline.split('  ')
            for (index, datum) in list(enumerate(dataline)):
                if ' ' in datum:
                    value, unit = datum.split()
                    currentParticleDict[indexToKeyList[index]].append((isNum(value), unit))
                else:
                    currentParticleDict[indexToKeyList[index]].append(isNum(datum))


        # this is for recording secondary partials that are created.
        elif singleLine[0] == ':':
            if singleLine[0:2] == ':-':
                if startSecondaryList:
                    secondaryContentList = [singleLine]
                else:
                    secondaryIndexToKeyList = indexToKeyList[1:5]
                    secondaryIndexToKeyList.append('particalType')
                    secondaryDict = secondaryParticleDict(secondaryContentList,
                                                          secondaryIndexToKeyList)
                    currentParticleDict['2ndaries' + str(secondaryParticleDictNumber)] = secondaryDict
                    secondaryParticleDictNumber += 1

                startSecondaryList = not startSecondaryList
            else:
                secondaryContentList.append(singleLine)



        else:
            print "The following line is ignored:", singleLine
    # get the last dictionary that was created.
    masterParticleList.append(currentParticleDict)

    return masterParticleList



def rescaleListUnits(listOfTuples):
    newList = []
    newUnit = None
    errorFlag = False
    for (value, unit) in listOfTuples:
        factor, parentUnit = getConversionFactor(unit)
        if newUnit is None:
            newUnit = parentUnit
        elif newUnit != parentUnit:
            print "There is a unit mismatch between", parentUnit, 'and', newUnit
            print "Something went went this should not be allowed to happen!"
            errorFlag = True
        newList.append(value * factor)
    if errorFlag:
        return None, None
    else:
        return newList, newUnit




def rescaleToCommonUnits(particleList):
    for particleDict in particleList:
        for key in particleDict.keys():

            if type(particleDict[key]) is tuple:
                value, unit = particleDict[key]
                factor, newUnit = getConversionFactor(unit)
                particleDict[key] = value * factor
                particleDict[key+'_Units'] = newUnit

            if type(particleDict[key]) is list:
                if type(particleDict[key][0]) is tuple:
                    particleDict[key], particleDict[key+'_Units'] = rescaleListUnits(particleDict[key])

            elif type(particleDict[key]) is dict:
                secondariesDict = particleDict[key]
                for key in secondariesDict.keys():
                    if type(secondariesDict[key]) is list:
                        if type(secondariesDict[key][0]) is tuple:
                            secondariesDict[key], secondariesDict[key+'_Units'] = rescaleListUnits(secondariesDict[key])

    return particleList


def getGeantOutput(longFileName):
    # read in the data
    contentList = readInData(longFileName=longFileName)

    # parse the data into a lists for each column
    particleList = parseData(contentList)

    # rescale the data units to be in a single common unit
    particleList = rescaleToCommonUnits(particleList)
    return particleList


if __name__ == "__main__":
    # the filenames
    fileNames = ["twopmts.out"]

    for fileName in fileNames:
        # This can be used to store data the is specific to different users, such as data location.
        if getpass.getuser() == "chw3k5": # Caleb Wheeler's User name on his own computer
            # This is the location where the folders with pulse data should be stored on your computer.
            longFileName = os.path.join("/Users", "chw3k5", "Downloads", fileName)
        elif getpass.getuser() == "joygarnett": # Caleb Wheeler's User name on his own computer
            # This is the location where the folders with pulse data should be stored on your computer.
            longFileName = os.path.join("/Users", "chw3k5", "Downloads", fileName)
        else:
            # write out all the directories that lead your filename, enclosed in quotes and separated by Commas
            longFileName = os.path.join("C:", "downloads", fileName)
            print getpass.getuser(), 'is your user name.'


        particleList = getGeantOutput(longFileName)
        print 'The read-in test has completed for ', longFileName



