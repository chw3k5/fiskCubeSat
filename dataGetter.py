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


