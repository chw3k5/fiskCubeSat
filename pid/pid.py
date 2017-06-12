__author__ = 'Caleb Wheeler'


import numpy
from time import sleep
from matplotlib import pyplot as plt




def errorFunction(outputGoal, outputVal, outputVal_previous, 
                  inputVal, inputVal_previous,
                  outputErrorIntegral, outputError_previous,
                  Ki, Kp, Kd,
                  useSimpleDerivative=True,
                  verbose=False):
    # this is the difference between what you measure and your goal.
    outputError = outputGoal - outputVal

    # this is the difference in the input values from the last two steps
    inputDifference = float(inputVal - inputVal_previous)

    # Here we calculate the integral (outputDifference x inputDifference) for a single step, the previous step
    outputErrorIntegral_thisStep = outputError * inputDifference

    # Here we add the current step to the overall integral
    # The value of the previous integral steps are saved outside this function since this function only
    # operates on the current step.
    outputErrorIntegral += outputErrorIntegral_thisStep

    if inputDifference == 0.0:
        inputDifference = 1.0
    # calculate the derivative
    if useSimpleDerivative:
        # This is the ideal derivative term for a fixed goal
        # der_outputError = (outputVal_previous - outputVal)
        der_outputError = (outputVal_previous - outputVal) / inputDifference
    else:
        # This derivative is needed if the goal is changing between steps.
        # der_outputError = (outputError - outputError_previous)
        der_outputError = (outputError - outputError_previous) / inputDifference

    # Calculate the terms of the error function
    pTerm = Kp * outputError
    iTerm = Ki * outputErrorIntegral
    dTerm = Kd * der_outputError

    # Calculate the error function
    errorFunction_Output = pTerm + iTerm + dTerm

    # Convert the calculated error in output to a calculated error in input (Determining the next input value)
    if der_outputError == 0.0:
        errorFunction_Input = 0
    else:
        errorFunction_Input = errorFunction_Output / der_outputError


    if verbose:
        print "pTerm:",pTerm,'   iTerm:',iTerm,'   dTerm:',dTerm,'   errorFunction_Input:',errorFunction_Input,'   errorFunction_Output:',errorFunction_Output

    return errorFunction_Input, errorFunction_Output, outputError, outputErrorIntegral_thisStep



if __name__ == "__main__":
    # set the PID constants 
    Ki = 0.0
    Kp = 0.01
    Kd = -0.01
    
    # set your goal output
    outputGoal = 1.0

    """
    Specify how many measurements do you want to use to calculate the integral.
    Must be at least 1 and be an integer.
    The integral has a fixed width of the number of measurements unless set to float('inf')
    When set to float('inf') this is the case where the bounds of the integral span the whole measurement
    An example of this is measuring how far a car has traveled to catch up to is
    but the input you have control over is your speed.
    """
    integralLen = 5
    
    # This something that changes you output that you cannot control 
    # like heating from the sun or mass water in a lake from evaporation and rain. 
    externalFunction = numpy.sin(numpy.arange(0.0, 100.0, 0.01))
    
    # this is the thing you can control, like the voltage on a resistor or valve on a pipe
    outputFromInput = numpy.arange(-1.0, 3.0, 0.0001)
    outputFromInput_len = len(outputFromInput)
    
    # make a guess at the initial input
    # Example: how much voltage to use, how far to turn a knob
    inputVal = len(outputFromInput) / 2
    
    # get the first value from the external forcing function
    # Example: how much it rained, how much heat was absorbed 
    externalVal = externalFunction[0]

    # initialize the previous input
    inputVal_previous = inputVal


    # make the first measurement
    internalInput = outputFromInput[inputVal]
    outputVal = internalInput + externalVal

    # initialize the previous output val
    outputVal_previous = outputVal

    # initialize the output error previous output val
    outputError = outputGoal - outputVal

    # initialize the output integral list
    outputErrorIntegralList = []
    outputErrorIntegral_thisStep = 0
    outputErrorIntegral = numpy.sum(outputErrorIntegralList)


    outputErrorIntegralList.append(outputErrorIntegral_thisStep)

    # make some plot lists
    plotGoals = []
    plotExternalVals = []
    plotInternalVals = []
    plotOutputVals = []

    indexesPerPlot = 1000

    legendLoc = 0
    legendNumPoints = 3
    legendHandleLength = 4
    
    for (valIndex, externalVal) in list(enumerate(list(externalFunction[1:]))):
        # calculate the current error integral
        if integralLen == float('inf'):
            # this is the case where the bounds of the integral span the whole measurement
            outputErrorIntegral += outputErrorIntegral_thisStep
        else:
            # these are the cases of a finite integral
            # note that the last part of the integral is calculated int he error function
            outputErrorIntegralList_len = len(outputErrorIntegralList)
            if outputErrorIntegralList_len < integralLen - 1:
                # the case where you do not have as many measurements as required by the integralLen
                outputErrorIntegral = numpy.sum(outputErrorIntegralList) * (float(outputErrorIntegralList_len) / float(integralLen - 1))
            else:
                # the case where you have exactly as many measurements as required by the integralLen
                # note one measurement is removed because a measurement integral will be added inside the error function
                outputErrorIntegralList.pop(0)
                outputErrorIntegral = numpy.sum(outputErrorIntegralList)

        # This at the next step the output error becomes the previous output error.
        outputError_previous = outputError

        # apply the error function 
        errorFunction_Input, errorFunction_Output, outputError, outputErrorIntegral_thisStep \
           = errorFunction(outputGoal, outputVal, outputVal_previous, 
                 inputVal, inputVal_previous, 
                 outputErrorIntegral, outputError_previous, 
                 Ki, Kp, Kd,
                 useSimpleDerivative=True,
                 verbose=True)


        # append this to the list of integral steps.
        outputErrorIntegralList.append(outputErrorIntegral_thisStep)

        # save the previous input val
        inputVal_previous = inputVal

        # set the next input value to try
        inputVal = inputVal_previous - int(numpy.round(errorFunction_Input))

        # save the previous output val
        outputVal_previous = outputVal

        # get the next measurement
        if inputVal < 0:
            inputVal = 0
            print 'Lower Limit Warning'
        elif outputFromInput_len <= inputVal:
            inputVal = outputFromInput_len - 1
            print "Upper Limit Warning"
        internalInput = outputFromInput[inputVal]
        outputVal = internalInput + externalVal
        
        # plot the data
        plotGoals.append(outputGoal)
        plotExternalVals.append(externalVal)
        plotInternalVals.append(internalInput)
        plotOutputVals.append(outputVal)


        if valIndex == 0:
            leglines = []
            leglabels = []

            leglines.append(plt.Line2D(range(10), range(10),
                           color='green'))
            leglabels.append('Goal')

            leglines.append(plt.Line2D(range(10), range(10),
                           color='firebrick'))
            leglabels.append('External Forces')

            leglines.append(plt.Line2D(range(10), range(10),
                           color='dodgerblue'))
            leglabels.append('Internal Forces')

            leglines.append(plt.Line2D(range(10), range(10),
                           color='darkOrchid'))
            leglabels.append('Total output')


        if (valIndex % indexesPerPlot) == 0:
            plt.plot(plotGoals, color='green')
            plt.plot(plotExternalVals, color='firebrick')
            plt.plot(plotInternalVals, color='dodgerblue')
            plt.plot(plotOutputVals, color='darkOrchid')

            plt.legend(leglines,leglabels, loc=legendLoc, numpoints=legendNumPoints, handlelength=legendHandleLength)

            plt.show()


        
        
        
        
        