from subprocess import call
import os
import getpass

"""
From http://geant4.cern.ch/support/download.shtml
Download Geant4 for Unix - MacOXS

This python file is written based on the youtube tutorial found here:
https://www.youtube.com/watch?v=dVF1MWGEcxg
"""


filesToDownload = [ "http://geant4.cern.ch/support/source/G4NDL.4.5.tar.gz",
                    "http://geant4.cern.ch/support/source/G4EMLOW.6.50.tar.gz",
                    "http://geant4.cern.ch/support/source/G4PhotonEvaporation.4.3.2.tar.gz",
                    "http://geant4.cern.ch/support/source/G4RadioactiveDecay.5.1.1.tar.gz",
                    "http://geant4.cern.ch/support/source/G4NEUTRONXS.1.4.tar.gz",
                    "http://geant4.cern.ch/support/source/G4PII.1.3.tar.gz",
                    "http://geant4.cern.ch/support/source/RealSurface.1.0.tar.gz",
                    "http://geant4.cern.ch/support/source/G4SAIDDATA.1.1.tar.gz",
                    "http://geant4.cern.ch/support/source/G4ABLA.3.0.tar.gz",
                    "http://geant4.cern.ch/support/source/G4ENSDFSTATE.2.1.tar.gz"]


def installShellPrograms():
    call('pip install cmake', shell=True)
    # call('pip install xml', shell=True)
    return



def changeDirectoryString(parentDirectory):
    return 'cd ' + parentDirectory + '\n'


def removeGeantFolders(localDir, geant4ZipFilename):
    commandString = changeDirectoryString(localDir)
    commandString += 'rm -fr ' + geant4ZipFilename[:-7] + '\n'
    commandString += 'rm ' + geant4ZipFilename + '\n'
    call(commandString, shell=True)
    return



def moveAndUnpackGeant(downloadsDir, localDir, geant4ZipFilename):
    commandString = changeDirectoryString(localDir)
    commandString += 'cp ' + downloadsDir + '/' + geant4ZipFilename + ' .\n'
    commandString += 'tar -zxvf ' + geant4ZipFilename + '\n'
    call(commandString, shell=True)
    return



def downloadGeantFiles(parentDirectory, filesToDownload):
    commandString = changeDirectoryString(parentDirectory)
    for fileName in filesToDownload:
        commandString +="curl -O " + fileName + "\n"
    call(commandString, shell=True)
    return

def splitFileNames(filesToDownload):
    fileNameList = []
    for website in filesToDownload:
        fileNameList.append(website.split('/')[-1])
    return fileNameList


def unpackFiles(parentDirectory, fileNames):
    commandString = changeDirectoryString(parentDirectory)
    for fileName in fileNames:
        commandString +="tar -xvzf " + fileName + "\n"
    call(commandString, shell=True)
    return


def buildInitialTarget(parentDirectory):
    buildDir = parentDirectory + "/build"
    if not os.path.exists(buildDir):
        os.mkdir(buildDir)
    commandString = changeDirectoryString(buildDir)
    commandString += 'cmake '
    commandString += '-DQT_QMAKE_EXECUTABLE=/Users/chw3k5/Library/Enthought/Canopy_64bit/User/bin/qmake '
    commandString += '-DCMAKE_BUILD_TYPE=Release '
    commandString += '-DCMAKE_INSTALL_PREFIX=/usr/local '
    # commandString += '-DXERCESC_INCLUDE_DIR=XERCESC_INCLUDE_DIR-NOTFOUND '
    # commandString += '-DXERCESC_LIBRARY=XERCESC_LIBRARY-NOTFOUND '
    commandString += '-DGEANT4_BUILD_MULTITHREADED=ON '
    commandString += '-DGEANT4_INSTALL_DATA=ON '
    # commandString += '-DGEANT4_USE_G3TOG4=OFF '
    # commandString += '-DGEANT4_USE_GDML=OFF'
    # commandString += '-DGEANT4_USE_INVENTOR=OFF '
    commandString += '-DGEANT4_USE_OPENGL_X11=ON '
    commandString += '-DGEANT4_USE_QT=ON '
    # commandString += '-DGEANT4_USE_RAYTRACER_X11=OFF '
    # commandString += '-DGEANT4_USE_SYSTEM_CLHEP=OFF '
    commandString += '-DGEANT4_USE_SYSTEM_EXPAT=ON '
    # commandString += '-DGEANT4_USE_SYSTEM_ZLIB=OFF '
    commandString += '-DGEANT4_USE_XM=ON '
    commandString += '../.\n'

    commandString += 'make -j2\n'
    commandString += 'make install\n'
    call(commandString, shell=True)
    return


def buildAndRun(parentDirectory):
    buildDir = parentDirectory + "/build"
    if not os.path.exists(buildDir):
        os.mkdir(buildDir)
    commandString = changeDirectoryString(buildDir)
    commandString += 'cmake ../.\n'
    commandString += 'make\n'
    commandString += './exampleB1\n'
    call(commandString, shell=True)
    return



def setEnvironmentVariables(geantUsrDataDir):
    commandString = ''
    commandString += 'export G4LEVELGAMMADATA=' + str(geantUsrDataDir) + '/PhotonEvaporation4.3.2\n'
    commandString += 'export G4NEUTRONXSDATA=' + str(geantUsrDataDir) + '/G4NEUTRONXS1.4\n'
    commandString += 'export G4LEDATA=' + str(geantUsrDataDir) + '/G4EMLOW6.50\n'
    commandString += 'export G4SAIDXSDATA=' + str(geantUsrDataDir) + '/G4SAIDDATA1.1\n'
    call(commandString, shell=True)
    return




if __name__ == "__main__":
    if getpass.getuser() == 'chw3k5':
        downloadsDir = '/Users/chw3k5/Downloads'
        geantUsrDataDir = '/usr/local/share/Geant4-10.3.1/data'
        localDir = '/Users/chw3k5/Documents/Fisk'
    elif getpass.getuser() == "joygarnett":
        downloadsDir = '/Users/joygarnett/Downloads'
        geantUsrDataDir = '/usr/local/share/Geant4-10.3.1/data'
        localDir = '/Users/joygarnett/Documents/'
    else:
        print 'Your username is:', getpass.getuser()
        downloadsDir = ''
        geantUsrDataDir = ''
        localDir = ''

    geant4ZipFilename = 'geant4.10.03.p01.tar.gz'
    geantLocalDir = localDir + '/geant4.10.03.p01'
    geatexampleDir = localDir + '/geant4.10.03.p01/examples/basic/B1'


    do_downloadFiles = False
    do_unpackFiles = False

    do_removeGeantFolders = True
    do_unpackGeant = True
    do_InitialBuild = True
    do_exampleBuild = True




    # these only need to be installed once
    if do_downloadFiles:
        downloadGeantFiles(geantUsrDataDir, filesToDownload)

    if do_unpackFiles:
        unpackFiles(geantUsrDataDir, fileNames=splitFileNames(filesToDownload))


    if do_removeGeantFolders:
        removeGeantFolders(localDir, geant4ZipFilename)


    if do_unpackGeant:
        moveAndUnpackGeant(downloadsDir, localDir, geant4ZipFilename)

    if do_InitialBuild:
        buildInitialTarget(geantLocalDir)
        setEnvironmentVariables(geantUsrDataDir)

    if do_exampleBuild:
        buildAndRun(geatexampleDir)







