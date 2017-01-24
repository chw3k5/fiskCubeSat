#include "qcustomgraph.h"
#include "QPainter"

#define MARGIN_X 10
#define MARGIN_Y 10

QCustomGraph::QCustomGraph(QWidget *parent) :
    QWidget(parent)
{

}

void QCustomGraph::paintEvent(QPaintEvent *)
{
    QPainter painter(this);
    QPen pen(Qt::yellow, 1.0f);
    painter.setPen(pen);

    painter.fillRect(rect(), Qt::black);

    if (_spectrumData.size() > 0)
    {
        // Determine the max counts in any particular channel
        unsigned int maxCounts = 0;
        QVector<unsigned int>::const_iterator it;
        for (it = _spectrumData.constBegin(); it != _spectrumData.constEnd(); ++it)
        {
            if ((*it) > maxCounts)
                maxCounts = *it;
        }

        int drawAreaX = rect().width() - (MARGIN_X * 2);
        int drawAreaY = rect().height() - (MARGIN_Y * 2);
        float drawX = (rect().width() - drawAreaX) / 2.0f;
        float drawY = rect().height() - MARGIN_Y;//drawAreaY - ((rect().height() - drawAreaY) / 2.0f);

        // Work out spacing for each bin on the graph
        float binPixSize = (float)drawAreaX / _spectrumData.size();
        float yScale = (float)drawAreaY / maxCounts;

        // Draw lines between each channel representing the counts
        QVector<QPointF> graphPoints;
        graphPoints.resize(_spectrumData.size());

        for (int i = 0; i < _spectrumData.size(); ++i)
        {
            QPointF &point = graphPoints[i];
            point.setX(drawX + (i * binPixSize));
            point.setY(drawY - (_spectrumData[i] * yScale));
        }

        painter.drawPolyline(graphPoints.data(), graphPoints.size());
    }
    painter.end();
}

// Redraw the graph using the data given
void QCustomGraph::UpdateGraph(QVector<unsigned int> spectrumData)
{
    _spectrumData = spectrumData;
    this->repaint();
}
