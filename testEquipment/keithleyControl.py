import serial
from time import sleep
from sys import platform, exit

"""
MAC OSX instructions for installing the USB to serial Driver
1) go to http://www.prolific.com.tw/US/ShowProduct.aspx?p_id=229&pcid=41
2) Install the driver for you mac operating system your computer has, mine is El Capitan so Installed
    PL2303_MacOSX_1.6.1_20160309.zip
3) Restart you computer
4) make sure you have the 2331A USB to serial adaptor plugged into your computer
5) in the mac terminal 'ls /dev/cu*" to see the Keithley usb device my was named '/dev/cu.usbserial'

Windows instructions for installing the USB to serial Driver
1) go to http://www.tek.com/dc-power-supply/2231a-30-3-software
2) download, unpack, and install the driver 2231A-001USBdriver.zip
3)

"""

if platform == 'win32':
    portNames = ['COM3', 'COM4']
elif platform == 'darwin':
    portNames = ['/dev/cu.usbserial']
else:
    portNames = ['']

isKeithley1_Open=False


def makeCurrentString(maxAmps=0.01,verbose=False):
    currentString = 'SOUR:CURR '+str('%1.4f'% maxAmps)+'A'
    if verbose:
        print 'the string to set the Keithley amperage is: '+currentString
    return currentString


def makeVoltageString(voltage=0.0,verbose=False):
    voltageString = 'SOUR:VOLT '+str('%2.4f'%voltage)+'V'
    if verbose:
        print 'the string to set the Keithley voltage is: '+voltageString
    return voltageString


def openKeithley1(verbose=False):
    global keithley1
    global isKeithley1_Open
    global portName
    isKeithley1_Open = False
    for portName in portNames:
        try:
            keithley1 = serial.Serial(port=portName, baudrate='9600', bytesize=7, stopbits=1, parity = 'O', timeout= 5)
            keithley1.write('SYST:REM')
            isKeithley1_Open = True
            break
        except:
            pass
    if not isKeithley1_Open:
        print "Keithley1 failed to be connected be the serial port"
        print "Port names tried:", portNames
        print "Exiting program because of this failure."
        exit()


    if verbose:
        print "The Keithley at " + portName + " is now open."
    return


def closeKeithley1(verbose=False):
    keithley1.close()
    global isKeithley1_Open
    isKeithley1_Open = False
    if verbose:
        print "The Keithley at " + portName + " is now closed."
    return


def beepKeithley():
    keithley1.write('SYST:BEEP\n')
    return


def setKeithley1Current(maxAmps=0.01, verbose=False):
    if not isKeithley1_Open: openKeithley1()
    keithley1.write(makeCurrentString(maxAmps=maxAmps,verbose=False))
    if verbose: print "setting the Keithley at " + portName + " to have a current limit of "+str(maxAmps)+ " Amps"
    return

def getKeithley1Currnet(verbose=False):
    if not isKeithley1_Open: openKeithley1()
    current = float(keithley1.write('MEAS:CURR?\n'))
    if verbose:
        print current, "is the current"
    return current

def setKeithley1Voltage(voltage=0.0, verbose=False):
    if not isKeithley1_Open: openKeithley1()
    keithley1.write(makeVoltageString(voltage=voltage,verbose=False))
    if verbose: print "setting the Keithley at " + portName + " to have a voltage of "+str(voltage)+ " Volts"
    return


def getKeithley1Voltage(verbose=False):
    if not isKeithley1_Open: openKeithley1()
    voltage = float(keithley1.write('SOUR:VOLT?\n'))
    if verbose:
        print voltage, "is the voltage"
    return voltage


def Keithley1_Output_ON(verbose=False):
    if not isKeithley1_Open: openKeithley1()
    keithley1.write("OUTPUT ON")
    if verbose: print "The Keithley at " + portName + " has be set for output 'ON'"
    return


def Keithley1_Output_OFF(verbose=False):
    if not isKeithley1_Open: openKeithley1()
    keithley1.write("OUTPUT OFF")
    if verbose: print "The Keithley at " + portName + " has be set for output 'OFF'"
    return




if __name__ == '__main__':
    verbose = True
    sleepTime = 5

    try:
        openKeithley1(verbose=verbose)
        beepKeithley()

        setKeithley1Voltage(voltage=5.0, verbose=verbose)
        Keithley1_Output_ON(verbose=verbose)
        sleep(sleepTime)

        measCurrent = getKeithley1Currnet(verbose=verbose)
        measVolt = getKeithley1Voltage(verbose=verbose)

        Keithley1_Output_OFF(verbose=verbose)
        beepKeithley()
    except:
        raise
        # print "Something when wrong!"
    finally:
        closeKeithley1(verbose=verbose)
