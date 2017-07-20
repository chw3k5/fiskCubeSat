# import serial, time
# serialPort = '/dev/cu.usbserial-A6004SPG'
#
# def makeCurrentString(maxAmps=0.01,verbose=False):
#     currentString = 'SOUR:CURR '+str('%1.4f'% maxAmps)+'A'
#     if verbose: print 'the string to set the Keithley amperage is: '+currentString
#     return currentString
#
# def makeVoltageString(voltage=0.0,verbose=False):
#     voltageString = 'SOUR:VOLT '+str('%2.4f'%voltage)+'V'
#     if verbose: print 'the string to set the Keithley voltage is: '+voltageString
#     return voltageString
#
# def openkeithley():
#     global keithley
#     global iskeithleyOpen
#     keithley = serial.Serial(port=serialPort, baudrate=9600, bytesize=8, stopbits=1, timeout=2)
#     iskeithleyOpen=True
#     time.sleep(1)
#     keithley.write(b'SYST:REM\n')
#     return
#
# def setkeithleyCurrent(maxAmps=0.01,verbose=False):
#     if not iskeithleyOpen: openkeithley()
#     keithley.write(makeCurrentString(maxAmps=maxAmps,verbose=False))
#     if verbose: print "setting the Keithley at " + serialPort + " to have a current limit of "+str(maxAmps)+ " Amps"
#     return
#
# def setkeithleyVoltage(voltage=0.0,verbose=False):
#     if not iskeithleyOpen: openkeithley()
#     keithley.write(makeVoltageString(voltage=voltage,verbose=False))
#     if verbose: print "setting the Keithley at " + serialPort + " to have a voltage of "+str(voltage)+ " Volts"
#     return
#
# def getkeithleyVoltage():
#     if not iskeithleyOpen: openkeithley()
#     keithley.write('SOUR:VOLT?')
#     voltage = float(keithley.read())
#     return voltage
#
#
# def keithley_Output_ON(verbose=False):
#     if not iskeithleyOpen: openkeithley()
#     keithley.write("OUTPUT ON")
#     if verbose: print "The Keithley at " + serialPort + " has be set for output 'ON'"
#     return
#
# def keithley_Output_OFF(verbose=False):
#     if not iskeithleyOpen: openkeithley()
#     keithley.write("OUTPUT OFF")
#     if verbose: print "The Keithley at " + serialPort + " has be set for output 'OFF'"
#     return
#
# def DisableDrive():
#     # Disable drive
#     status = False
#     if keithley.isOpen():
#         keithley.write(b'DRIVE0\n')
#         status = True
#     else:
#         print "The port is not open, returning status False"
#     return status

# Name: controlKeithley.py
# Purpose: Remote control Keithley 2231A-30-3 Triple Channel DC Power Supply
# Author: Jenna Moore
# Email: jenna.moore94@gmail.com
# Date Created: April 27, 2017

# import libraries, define serial port
import serial, time, scpi

keithley = serial.Serial('/dev/tty.usbserial-A6004SPG', timeout=1, rtscts=True)


# boot up, set to remote control mode, beep test, select channel, turn output on
def bootKeithley():
    if not keithley.is_open: keithley.open()
    time.sleep(1)

    keithley.write(b'SYST:REM\n')
    keithley.write(b'SYST:BEEP\n')
    keithley.write(b'INST {CH1}\n')
    keithley.write(b'OUTP ON\n')
    print "Keithley is awake and ready to go!"
    return


# set voltage
def setVoltage(voltage=0.0, verbose=False):
    if not keithley.is_open: bootKeithley()
    voltage = str('%2.4f' % voltage)
    keithley.write(b'APP:VOLT +voltage\n')
    if verbose: print "The voltage is set at " + str(voltage) + "V"
    return


# shutdown
def shutdownKeithley():
    keithley.close()
    return


if __name__ == '__main__':
    # setkeithleyCurrent(maxAmps=0.11,verbose=True)
    # setkeithleyVoltage(voltage=11,verbose=True)
    # keithley_Output_ON(verbose=True)
    # sleep(5)
    # keithley_Output_OFF(verbose=True)
    #
    # setKeithley12Current(maxAmps=0.12,verbose=True)
    # setKeithley12Voltage(voltage=12,verbose=True)
    # Keithley12_Output_ON(verbose=True)
    # sleep(5)
    # Keithley12_Output_OFF(verbose=True)
    # print getKeithley12Currnet()
    # measVolt=getKeithley12Voltage()
    # print measVolt
    # setKeithley12Voltage(voltage=measVolt+0.0005,verbose=True)
    # getKeithley12Voltage()
    # print getKeithley12Currnet()
    shutdownKeithley()
    keithley.a