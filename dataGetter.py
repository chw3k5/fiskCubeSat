import string, numpy


def getTableData(filename):
    f = open(filename, 'r')
    # the first line is the header information naming the columns of data
    firstLine = f.readline()
    columnNames = string.split(firstLine,',')
    f.close()

    tableData = numpy.loadtxt(filename, skiprows=1, delimiter=',')

    tableDict = {}
    for (n, columnName) in list(enumerate(columnNames)):
        tableDict[columnName] = tableData[:,n]
    return tableDict