#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "SpectrometerDriver.h"
#include "QTableWidgetDeviceItem.h"
#include "QMessageBox"

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    // QT Init
    ui->setupUi(this);
    connect(this, SIGNAL(OnDetectorsChanged()), this, SLOT(on_detectorsChanged()));
    connect(this, SIGNAL(OnError(int, int, QString)), this, SLOT(on_Error(int, int, QString)) );

    // Status bar
    _totalCountsStatusLabel = new QLabel("Total Counts: 0", ui->statusBar);
    _realTimeStatusLabel = new QLabel("Real Time: 0", ui->statusBar);
    _liveTimeStatusLabel = new QLabel("Live Time: 0", ui->statusBar);
    ui->statusBar->addWidget(_totalCountsStatusLabel);
    ui->statusBar->addWidget(_realTimeStatusLabel);
    ui->statusBar->addWidget(_liveTimeStatusLabel);

    // Setup a timer to refresh the graph display / query for the spectrum of the selected device
    _pTimer = new QTimer (this);
    _pTimer->setInterval(1000);
    _pTimer->connect(_pTimer, SIGNAL(timeout()), this, SLOT(OnTimer()));
    _pTimer->start();

    int productVer, majVer, minVer, buildVer;
    kr_GetVersionInformation(&productVer, &majVer, &minVer, &buildVer);
    this->setWindowTitle(QString("Spectrometer Example (Driver version %1.%2.%3.%4)").arg(
                             QString::number(productVer),
                             QString::number(majVer),
                             QString::number(minVer),
                             QString::number(buildVer)));
    kr_SetDeviceChangedCallback(krDeviceChangedCallback, this);
    kr_Initialise(krErrorCallback, this);
}

MainWindow::~MainWindow()
{
    _pTimer->stop();
    _pTimer = NULL;
    _totalCountsStatusLabel = NULL;
    _realTimeStatusLabel = NULL;
    _liveTimeStatusLabel = NULL;

    kr_Destruct();
    delete ui;
}

void MainWindow::on_startStopButton_clicked()
{
    unsigned int deviceID = GetSelectedDeviceID();
    if (deviceID == 0)
        return;

    if (kr_IsAcquiringData(deviceID))
    {
        // Stop the current acquisition
        kr_StopDataAcquisition(deviceID);
        ui->startStopButton->setText("Start Acquisition");
    }
    else
    {
        // Start acquisition on the device
        int liveTime = ui->liveTimeNumeric->value();
        int realTime = ui->realTimeNumeric->value();

        // Set the LLD of the device to 32 channels (Default for GR1 / GR1A)
        kr_SendInt16ConfigurationCommand(deviceID, HIDREPORTNUMBER_SETLLD, 200);

        // Begin acquisition on the device. A realtime / livetime of 0 will mean acquire without a time limit
        if (kr_BeginDataAcquisition(deviceID, realTime * 1000, liveTime * 1000) != ERROR_OK)
        {
            QMessageBox msg(QMessageBox::Icon(), "Error", "Unable to read from device");
            msg.exec();
        }
        else
        {
            UpdateUIControls();
        }
    }
}

void MainWindow::on_clearButton_clicked()
{
    unsigned int deviceID = GetSelectedDeviceID();
    if (deviceID == 0)
        return;

    kr_ClearAcquiredData(deviceID);
    UpdateDisplay();
}

//===========================================================
// Name:			krErrorCallback
// Args:			pUserData: User assigned data assigned when registering the callback
//					deviceID : The id of the device that caused the error
//					errorCode: The id that identifies the error (see SpecrometerData.h)
//                  pMessage: Message string or NULL if no message is given
// Description:		Callback function raised from the device dll when an error occurs
//===========================================================
void stdcall MainWindow::krErrorCallback(void *pCallbackObject, unsigned int deviceID, int errorCode, const char *pMessage)
{
    // The error event is potentially returned on a different thread from the main application window. Pass via signal/slot to main window thread
    MainWindow *pThis = (MainWindow*)pCallbackObject;
    emit pThis->OnError(deviceID, errorCode, QString(pMessage));
}

// Event raised when an error message is received. Run on the main window thread and called from krErrorCallback()
void MainWindow::on_Error(int /*deviceID*/, int errorCode, QString errorMsg)
{
    QString msg;
    switch (errorCode)
    {
    case ERROR_NOT_INITIALISED:
        msg = "Library not initialised";
        break;

    case ERROR_ACQUISITION_COMPLETE:
        msg = "Acquisition Completed";
        UpdateUIControls();
        break;

    default:
        msg = errorMsg;
    }

    QMessageBox msgBox(QMessageBox::Icon(), "Message", msg);
    msgBox.exec();
}

//===========================================================
// Name:			krDeviceChangedCallback
// Args:			detectorID: ID of the detector that has been attached / detached
//					added: true if the device has been connected, otherwise the device has just been disconnected
//					pCallbackObject: User assigned data assigned when registering the callback
// Description:		Event raised from the device dll when a device is connected / disconnected
//===========================================================
void stdcall MainWindow::krDeviceChangedCallback(unsigned int /*detectorID*/, BOOL /*added*/, void *pCallbackObject)
{
    MainWindow *pThis = (MainWindow*)pCallbackObject;

    // The callback method has been called in a different thread. By using Qts 'emit' method this will automatically
    // get passed onto the main UI thread.
    emit pThis->OnDetectorsChanged();
}

// Event raised when the list of detectors has changed. Called from krDeviceChangedCallback()
void MainWindow::on_detectorsChanged()
{    
    // Clear the list of devices and set headers
    ui->devicesList->clear();
    ui->devicesList->removeRow(0);
    ui->devicesList->setColumnCount(5);

    ui->devicesList->setHorizontalHeaderItem(0, new QTableWidgetItem("Device Name"));
    ui->devicesList->setHorizontalHeaderItem(1, new QTableWidgetItem("Manufacturer"));
    ui->devicesList->setHorizontalHeaderItem(2, new QTableWidgetItem("Serial"));
    ui->devicesList->setHorizontalHeaderItem(3, new QTableWidgetItem("Vendor ID"));
    ui->devicesList->setHorizontalHeaderItem(4, new QTableWidgetItem("Product ID"));

    // Enumerate each of the attached detectors
    unsigned int detectorID = 0;
    while ((detectorID = kr_GetNextDetector(detectorID)) != 0)
    {
        // Create a new row in the detectors list
        int row = ui->devicesList->rowCount();
        ui->devicesList->insertRow(row);

        const unsigned int cNumberOfCharacters = 126;  // max number of characters for a USB product.

        // Retrieve individual details about the device
        char deviceName[cNumberOfCharacters];
        int bytesOut;
        kr_GetDeviceName(detectorID, deviceName, cNumberOfCharacters, &bytesOut);

        char manufacturer[cNumberOfCharacters];
        kr_GetDeviceManufacturer(detectorID, manufacturer, cNumberOfCharacters, &bytesOut);

        char serialNumber[cNumberOfCharacters];
        kr_GetDeviceSerial(detectorID, serialNumber, cNumberOfCharacters, &bytesOut);

        int vendorID, productID;
        kr_GetDeviceVendorID(detectorID, &vendorID);
        kr_GetDeviceProductID(detectorID, &productID);

        // Add the detector details to the table, store the deviceID in each cell for easy reference later
        ui->devicesList->setItem(row, 0, new QTableWidgetDeviceItem(QString(deviceName), detectorID));
        ui->devicesList->setItem(row, 1, new QTableWidgetDeviceItem(QString(manufacturer), detectorID));
        ui->devicesList->setItem(row, 2, new QTableWidgetDeviceItem(QString(serialNumber), detectorID));
        ui->devicesList->setItem(row, 3, new QTableWidgetDeviceItem(QString("0x%1").arg(vendorID, 0, 16), detectorID));
        ui->devicesList->setItem(row, 4, new QTableWidgetDeviceItem(QString("0x%1").arg(productID, 0, 16), detectorID));
    }
}

// Get the id of the selected detector in the device list
unsigned int MainWindow::GetSelectedDeviceID()
{
    // The control is in single row selection mode so just get the first selected cell
    if ( ui->devicesList->selectedItems().size() == 0)
        return 0;

    QTableWidgetDeviceItem *pSelectedItem = static_cast<QTableWidgetDeviceItem*>(ui->devicesList->selectedItems()[0]);
    return pSelectedItem->DeviceID();
}

void MainWindow::UpdateUIControls()
{
    unsigned int deviceID = GetSelectedDeviceID();
    bool isAcquiring = deviceID != 0 && kr_IsAcquiringData(deviceID) == 1;

    ui->clearButton->setEnabled(deviceID != 0);
    ui->startStopButton->setEnabled(deviceID != 0);
    ui->startStopButton->setText(QString(isAcquiring ? "Stop Acquisition": "Start Acquisition"));

    ui->liveTimeNumeric->setEnabled(deviceID != 0 && !isAcquiring);
    ui->realTimeNumeric->setEnabled(deviceID != 0 && !isAcquiring);

}

// Update controls when a different detector is selected
void MainWindow::on_devicesList_itemSelectionChanged()
{
    UpdateUIControls();
    UpdateDisplay();
}

void MainWindow::OnTimer()
{
    UpdateDisplay();
}

// Update the display of the currently selected detectors acquisition data
void MainWindow::UpdateDisplay()
{
    unsigned int totalCounts = 0;
    unsigned int realTime = 0;
    unsigned int liveTime  = 0;
    // Allocate a buffer big enough to hold the channel data for the acquisition
    QVector<unsigned int> spectrumData;
    spectrumData.resize(TOTAL_RESULT_CHANNELS);

    unsigned int deviceID = GetSelectedDeviceID();
    if (deviceID != 0)
    {
        // Get the spectrum data for the current acquisition
        kr_GetAcquiredData(deviceID, spectrumData.data(), &totalCounts, &realTime, &liveTime);
    }

    // Update the graph control
    ui->graphView->UpdateGraph(spectrumData);

    // Update status bar
    _totalCountsStatusLabel->setText(QString("Total Counts: %1").arg(totalCounts));
    _realTimeStatusLabel->setText(QString("Real Time: %1").arg((float)realTime / 1000.0f));
    _liveTimeStatusLabel->setText(QString("Live Time: %1").arg((float)liveTime / 1000.0f));
}
