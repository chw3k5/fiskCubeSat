#ifndef QTABLEWIDGETDEVICEITEM_H
#define QTABLEWIDGETDEVICEITEM_H

#include "QTableWidgetItem"

// A simple table entry item for the device list. Stores the DeviceID along with the table entry
class QTableWidgetDeviceItem : public QTableWidgetItem
{
public:

    QTableWidgetDeviceItem(QString text, unsigned int deviceID)
        : QTableWidgetItem(text)
        , _deviceID(deviceID)
    {

    }

    virtual ~QTableWidgetDeviceItem()
    {

    }

    unsigned int DeviceID() const {return _deviceID;}

private:

    unsigned int _deviceID;
};

#endif // QTABLEWIDGETDEVICEITEM_H
