from distutils.core import setup, Extension
setupSpam = False
setupPyKromek = True

if setupSpam:
    spamModule = Extension('spam', sources=['cppDriverCode/spammodule.c'])
    setup(name='spamName', version='1.0', description='this is test package for wrapping c code in python',
          ext_modules = [spamModule])

if setupPyKromek:
    pyKromekModule = Extension('pyKromek', sources=['cppDriverCode/pyKromekModule.cpp'])
    setup(name='pyKromek', version='1.0', description='A python extension for C++ Kromek driver code?',
          ext_modules = [pyKromekModule],)