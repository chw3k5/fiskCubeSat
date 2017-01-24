#ifndef QCUSTOMGRAPH_H
#define QCUSTOMGRAPH_H

#include <QWidget>

// Custom graph control that draws a simple line graph from an array of channel data (counts per channel)
class QCustomGraph : public QWidget
{
    Q_OBJECT
public:
    explicit QCustomGraph(QWidget *parent = 0);

    void UpdateGraph(QVector<unsigned int> spectrumData);
signals:

public slots:

protected:
    void paintEvent(QPaintEvent*);

private:
    QVector<unsigned int> _spectrumData;
};

#endif // QCUSTOMGRAPH_H
