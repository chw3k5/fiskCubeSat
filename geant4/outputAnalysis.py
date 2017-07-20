from geant4.dataReadIn import getGeantOutput
from quickPlots import quickHistograms
import getpass, os
from matplotlib import pyplot as plt



class singleGamma():
    def __init__(self, longFileName):
        self.outputParticleList = getGeantOutput(longFileName)
        self.filename = longFileName

    def finalDestinations(self, valueToGet='KineE', thingsToGroupBy=['Volume','Process'], showPlots=True):
        """
        This method looks at the last step of a particle records values specified by 'valueToGet' while grouping
        those values by unique parings of the values specified by 'thingsToGroupBy'

        :param thingToHistogram (string): This is the type of value that will be recorded into a dictionary, in
            self.finalDestination
            Options are 'Step#', 'X', 'Y', 'Z', 'KineE', 'dEStep', 'StepLeng', 'TrakLeng', 'Volume', 'Process'
        :param thingsToGroupBy (list): This is list of strings the options are:
            'Volume', 'Process', and 'Step#' or any entry that is not a floating point number
        :param showPlots (bool): Toggles an optional plot to visualize the data.
        :return:
        """

        self.finalDestinationDict = {}
        for particleDict in self.outputParticleList:
            groupingKeyList = []
            for groupElement in thingsToGroupBy:
                groupingKeyList.append(particleDict[groupElement][-1])
            groupingKey = tuple(groupingKeyList)
            if groupingKey in self.finalDestinationDict.keys():
                self.finalDestinationDict[groupingKey].append(particleDict[valueToGet][-1])
            else:
                self.finalDestinationDict[groupingKey] = [particleDict[valueToGet][-1]]


        if showPlots:
            quickHistograms(self.finalDestinationDict, columns=2, bins=10, keys=None,
                    plotFileName='hist', savePlots=False, doEps=False, showPlots=True,
                    verbose=True)




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




        testGamma = singleGamma(longFileName)
        testGamma.finalDestinations(valueToGet='KineE', thingsToGroupBy=['Volume','Process'], showPlots=True)
