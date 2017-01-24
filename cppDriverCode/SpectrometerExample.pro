#-------------------------------------------------
#
# Project created by QtCreator 2014-09-25T13:33:53
#
#-------------------------------------------------

QT       += core gui

win32::DEFINES += _WINDOWS

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = SpectrometerExample
TEMPLATE = app

unix:QMAKE_CXXFLAGS += -pthread

SOURCES +=  main.cpp\
            mainwindow.cpp \
            qcustomgraph.cpp \
            SpectrometerDriver.cpp \
            SpectrometerData.cpp \
            DriverMgr.cpp \
            Detector.cpp \
            Lock.cpp \
            CriticalSection.cpp



HEADERS  += mainwindow.h \
            QTableWidgetDeviceItem.h \
            qcustomgraph.h  \
            SpectrometerDriver.h \
            SpectrometerData.h \
            Detector.h \
            DriverMgr.h \
            Lock.h \
            CriticalSection.h

FORMS    += mainwindow.ui

# Make sure the correct arch variable is set (linux)
linux-g++:QMAKE_TARGET.arch = $$QMAKE_HOST.arch
linux-g++-32:QMAKE_TARGET.arch = x86
linux-g++-64:QMAKE_TARGET.arch = x86_64

contains(QMAKE_TARGET.arch, x86_64): {
win32:CONFIG(release, debug|release): LIBS += -L$$PWD/../libs/win64/release -lSpectrometerDriver
else:win32:CONFIG(debug, debug|release): LIBS += -L$$PWD/../libs/win64/debug -lSpectrometerDriver

unix:CONFIG(release, debug|release): LIBS += -L$$PWD/../libs/linux64/release -lSpectrometerDriver
else:unix:CONFIG(debug, debug|release): LIBS += -L$$PWD/../libs/linux64/debug -lSpectrometerDriver
} else {
win32:CONFIG(release, debug|release): LIBS += -L$$PWD/../libs/win32/release -lSpectrometerDriver
else:win32:CONFIG(debug, debug|release): LIBS += -L$$PWD/../libs/win32/debug -lSpectrometerDriver

unix:CONFIG(release, debug|release): LIBS += -L$$PWD/../libs/linux32/release -lSpectrometerDriver
else:unix:CONFIG(debug, debug|release): LIBS += -L$$PWD/../libs/linux32/debug -lSpectrometerDriver
}

INCLUDEPATH += $$PWD/../SpectrometerDriver
DEPENDPATH += $$PWD/../SpectrometerDriver
