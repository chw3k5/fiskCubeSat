# Name: controlKeithley.py
# Purpose: remote control Keithley via RS232 - USB connection
# Author: Jenna E. Moore
# Date Created: April 29, 2017

#import necessary packages
import visa, time, serial

#get the VISA backend
rm = visa.ResourceManager()

#find keithley and open it
def selectPort():
    global keithley
    #generates a list of available ports
    ports = rm.list_resources()
    #ask user to select port
    prompt = raw_input('>>>Avaliable ports: ' + str(ports) + '\n Please select a port: ')
    #verifies selection is an available port, opens the port
    if prompt in ports:
        keithley = rm.open_resource(prompt)
        time.sleep = 1
        return keithley
    else:
        print 'You did not select a valid port. Please try again.'
        selectPort()
    return keithley

#verify the port opened is the Keithley, switch to remote control mode
def identifyYourself(keithley):
    ID = keithley.serial.query(u'*IDN?\r\n')
    verify = raw_input('>>>Is ' + ID + ' the correct instrument? (Y/N)')
    if verify == 'N':
        print('>>>Closing ' + ID)
        selectPort()
    elif verify == 'Y':
        #SCPI command for remote control mode
        keithley.serial.write(u'SYST:REM\r\n')
        print('>>>The Keithley is now in remote control mode.')
    else:
        raw_input('>>>You did not select a valid option. Please try again.')
        identifyYourself()
    return

identifyYourself(keithley=selectPort())


