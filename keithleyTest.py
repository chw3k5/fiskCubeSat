import serial

portName = 'COM3'
voltage = 1.0
device = serial.Serial(port=portName, baudrate='9600', bytesize =7, stopbits =1, parity = 'O', timeout= 5)

beep = 'SYST:BEEP\n'
voltSet = "SOUR:VOLT" + str('%2.3f' % voltage) + ' V'
idInfo = '*IDN?\n'

device.write(idInfo)
print device.read(), " is the device output."
