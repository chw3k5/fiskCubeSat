from matplotlib import pyplot as plt
import random




colors=['BlueViolet','Brown','CadetBlue','Chartreuse', 'Chocolate','Coral','CornflowerBlue','Crimson','Cyan',
        'DarkBlue','DarkCyan','DarkGoldenRod', 'DarkGreen','DarkMagenta','DarkOliveGreen','DarkOrange',
        'DarkOrchid','DarkRed','DarkSalmon','DarkSeaGreen','DarkSlateBlue','DodgerBlue','FireBrick','ForestGreen',
        'Fuchsia','Gold','GoldenRod','Green','GreenYellow','HotPink','IndianRed','Indigo','LawnGreen',
        'LightCoral','Lime','LimeGreen','Magenta','Maroon', 'MediumAquaMarine','MediumBlue','MediumOrchid',
        'MediumPurple','MediumSeaGreen','MediumSlateBlue','MediumTurquoise','MediumVioletRed','MidnightBlue',
        'Navy','Olive','OliveDrab','Orange','OrangeRed','Orchid','PaleVioletRed','Peru','Pink','Plum','Purple',
        'Red','RoyalBlue','SaddleBrown','Salmon','SandyBrown','Sienna','SkyBlue','SlateBlue','SlateGrey',
        'SpringGreen','SteelBlue','Teal','Tomato','Turquoise','Violet','Yellow','YellowGreen']


default_plotDict = {}

# These can be a list or a single value
default_plotDict['colors'] = random.shuffle(colors)

default_plotDict['fmt'] = 'o'
default_plotDict['markersize'] = 5
default_plotDict['alpha'] = 1.0
default_plotDict['ls'] = '-'
default_plotDict['marker'] = None
default_plotDict['lineWidth'] = '1'

default_plotDict['ErrorMaker'] = '|'
default_plotDict['ErrorCapSize'] = 4
default_plotDict['Errorls'] = 'None'
default_plotDict['Errorliw'] = 1
default_plotDict['xErrors'] = 'None'
default_plotDict['yErrors'] = 'None'
default_plotDict['legendAutoLabel'] = True
default_plotDict['legendLabel'] = ''

# These must be a single value
default_plotDict['title'] = ''
default_plotDict['xlabel'] = ''
default_plotDict['ylabel'] = ''

default_plotDict['doLegend'] = False
default_plotDict['legendLoc'] = 0
default_plotDict['legendNumPoints'] = 3
default_plotDict['legendHandleLength'] = 5

default_plotDict['savePlot'] = False
default_plotDict['plotFileName'] = 'plot'
default_plotDict['doEPS'] = True
default_plotDict['doShow'] = False


# this definition uses the default values defined above is there is no user defined value in dataDict
def extractPlotVal(plotDict, valString, listIndex=0, keys=None):
    # extract the plot value for the list or use a the singleton value
    if keys is not 'None':
        keys = plotDict.keys()
    if valString in keys:
        if isinstance(plotDict[valString], list):
            val = plotDict[valString][listIndex]
        else:
            val = plotDict[valString]
    else:
        val = default_plotDict[valString]
    return val

def quickPlotter(plotDict):
    keys = plotDict.keys()
    if 'verbose' in keys:
        verbose = plotDict['verbose']
    else:
        verbose = True
    if verbose: print 'Starting the quick plotting program...'

    # decide if the user wants to plot a legend
    if 'doLegend' in keys:
        doLegend = plotDict['doLegend']
    else:
        doLegend = default_plotDict['doLegend']
    leglabels = []
    leglines = []

    # plot the lists of data
    for (listIndex, yData) in list(enumerate(plotDict['yData'])):
        # Extract the x data for this plot, or use the length of the yData to make x array
        if 'xData' not in keys:
            if verbose: print 'no axis found, using the length of the yData'
            xData = range(len(yData))
        else:
            xData = plotDict['xData'][listIndex]

        # extract the plot color for this yData
        if 'colors' in keys:
            if isinstance(plotDict['colors'], list):
                color = plotDict['colors'][listIndex]
            else:
                color = plotDict['colors']
        else:
            color = default_plotDict['colors'][listIndex]

        # extract the plot line style
        ls = extractPlotVal(plotDict, 'ls', listIndex, keys=keys)
        # extract the plot line width
        lineWidth = extractPlotVal(plotDict, 'lineWidth', listIndex, keys=keys)
        # extract the plot marker format
        fmt = extractPlotVal(plotDict, 'fmt', listIndex, keys=keys)
        # exact the marker size
        markersize = extractPlotVal(plotDict, 'markersize', listIndex, keys=keys)
        # extract the marker transparency
        alpha = extractPlotVal(plotDict, 'alpha', listIndex, keys=keys)
        # extract the error marker
        ErrorMaker = extractPlotVal(plotDict, 'ErrorMaker', listIndex, keys=keys)
        # extract the error marker's cap  size
        ErrorCapSize = extractPlotVal(plotDict, 'ErrorCapSize', listIndex, keys=keys)
        # extract the error marker line style
        Errorls = extractPlotVal(plotDict, 'Errorls', listIndex, keys=keys)
        # extract the erro marker line width
        Errorliw = extractPlotVal(plotDict, 'Errorliw', listIndex, keys=keys)

        if doLegend:
            # create the legend line and label
            leglines.append(plt.Line2D(range(10), range(10),
                                       color=color, ls=ls,
                                       linewidth=lineWidth, marker=fmt,
                                       markersize=markersize, markerfacecolor=color,
                                       alpha=alpha))
            leglabels.append(extractPlotVal(plotDict, 'legendLabel', listIndex, keys=keys))

        # plot the yData for this loop
        if verbose: print 'plotting data in index', listIndex
        plt.plot(xData, yData,linestyle=ls, color=color,
                 linewidth=lineWidth, marker=fmt, markersize=markersize,
                 markerfacecolor=color, alpha=alpha)

        if (('xErrors' in keys) or ('yErrors' in keys)):
            # extract the x error (default is "None")
            xError = extractPlotVal(plotDict, 'xErrors', listIndex, keys=keys)
            # extract the y error (default is "None")
            yError = extractPlotVal(plotDict, 'yErrors', listIndex, keys=keys)

            plt.errorbar(xData, yData, xerr=xError, yerr=yError,
                         marker=ErrorMaker, color=color, capsize=ErrorCapSize,
                         linestyle=Errorls, elinewidth=Errorliw)

    # now we will add the title and x and y axis labels
    plt.title(extractPlotVal(plotDict, 'title', keys=keys))
    plt.xlabel(extractPlotVal(plotDict, 'xlabel', keys=keys))
    plt.ylabel(extractPlotVal(plotDict, 'ylabel', keys=keys))

    # now we will make the legend (doLegend is True)
    if doLegend:
        # extract the legend info
        if verbose: print 'rendering a legend for this plot'
        legendLoc = extractPlotVal(plotDict, 'legendLoc', keys=keys)
        legendNumPoints = extractPlotVal(plotDict, 'legendNumPoints', keys=keys)
        legendHandleLength = extractPlotVal(plotDict, 'legendHandleLength', keys=keys)
        # call the legend command
        plt.legend(leglines,leglabels, loc=legendLoc, numpoints=legendNumPoints, handlelength=legendHandleLength)

    # here the plot can be saved
    if extractPlotVal(plotDict, 'savePlot', keys=keys):
        plotFileName = extractPlotVal(plotDict, 'plotFileName', keys=keys)
        if extractPlotVal(plotDict, 'doEPS', keys=keys):
            plotFileName += '.eps'
        else:
            plotFileName += '.png'
        if verbose: print 'saving the plot', plotFileName
        plt.savefig(plotFileName)

    # here the plot can be shown
    if extractPlotVal(plotDict, 'doShow', keys=keys):
        if verbose: print 'showing the plot in a pop up window'
        plt.show()


    if verbose: print '...the quick plotting program has finished.'
    return
