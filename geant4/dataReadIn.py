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


def parseData(contentList):
    # Remove 'G4WT0 > ' from each line
    contentList = [x.replace('G4WT0 >  ', '') for x in contentList]
    contentList = [x.replace('pmt', '') for x in contentList]
    contentList = [x.replace('Transportation', '') for x in contentList]

    # Remove whitespace characters at the beginning and return characters like \n and \r at the end of each line
    contentList = [x.strip() for x in contentList]

    #split the data by white space
    contentList = [x.split() for x in contentList]

    # get rid of all the extra data on the header
    dataStartIndex = 3
    contentList = contentList[3:]

    # make the list in terms of columns from (now it is in rows) transpose
    contentList =  [list(x) for x in zip(*contentList)]

    # make everything a number
    newList = []
    for dataColumn in contentList[:]:
        newColumnList = []
        for datum in dataColumn:
            newColumnList.append(isNum(datum))
        newList.append(newColumnList)
    contentList = newList

    return contentList




if __name__ == "__main__":
    # the filenames
    fileNames = ['fresh.txt']#"twopmts.out"]

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
        dataDict = parseData(contentList)



