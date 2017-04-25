import string, numpy


def getTableData(filename, skiprows=1, delimiter=','):
    f = open(filename, 'r')
    # the first line is the header information naming the columns of data
    firstLine = f.readline()
    columnNames = string.split(firstLine.strip(), delimiter)

    f.close()

    tableData = numpy.loadtxt(filename, skiprows=skiprows, delimiter=delimiter)

    tableDict = {}
    for (n, columnName) in list(enumerate(columnNames)):
        tableDict[columnName] = tableData[:,n]
    return tableDict

def getTableRowData(filename, delimiter=','):
    tableDict = {}
    f = open(filename, 'r')
    for line in f:
        rowInfo = line.split(delimiter)
        rowHeader = rowInfo[0].strip()
        rowDataList = [float(datum) for datum in rowInfo[1:]]
        dataSize = len(rowDataList)
        if dataSize > 1:
            tableDict[rowHeader] = numpy.array(rowDataList)
        elif dataSize == 1:
            tableDict[rowHeader] = rowDataList[0]
        else:
            tableDict[rowHeader] = None
    f.close()

    return tableDict

