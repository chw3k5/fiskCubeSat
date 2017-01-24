#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QTimer>
#include <QLabel>
#include "SpectrometerDriver.h"

namespace Ui {
class MainWindow;
}

// The main application window
class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

private slots:
    void on_startStopButton_clicked();

    void on_clearButton_clicked();

    void on_Error(int deviceID, int errorCode, QString errorMsg);

    void on_detectorsChanged();

    void on_devicesList_itemSelectionChanged();

     void OnTimer();
signals:

    void OnDetectorsChanged();
    void OnError(int deviceID, int errorCode, QString errorMsg);


private:
    Ui::MainWindow *ui;
    QTimer *_pTimer;
    QLabel *_totalCountsStatusLabel;
    QLabel *_realTimeStatusLabel;
    QLabel *_liveTimeStatusLabel;

    // Static callback functions directly from the driver dll
    static void stdcall krErrorCallback(void *pCallbackObject, unsigned int deviceID, int errorCode,const char *pMessage);
    static void stdcall krDeviceChangedCallback(unsigned int detectorID, BOOL added, void *pCallbackObject);

    unsigned int GetSelectedDeviceID();
    void UpdateUIControls();
    void UpdateDisplay();
};

#endif // MAINWINDOW_H
