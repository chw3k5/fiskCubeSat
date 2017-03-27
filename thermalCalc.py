import numpy

stefanBoltzmann = 5.670367e-8 # W / (m^2 K^4)

solarPowerPerAreaEarth_W_sqm = 1368. # W / m^2

sqrtOf2 = numpy.sqrt(2.0)

def radiatedPower(temperature_K, area_sqm):
    return stefanBoltzmann * float(area_sqm) * (float(temperature_K) ** 4.0)

maxPower_1Unitlow_W = 1.
maxPower_1UnitHigh_W = 2.5
maxPower_2Unitlow_W = 2.
maxPower_2UnitHigh_W = 5.
maxPower_3Unitlow_W = 7.
maxPower_3UnitHigh_W = 20.



def convertLenUnitsTo_m(lenVal, lenIn_m=True, lenIn_cm=False, lenIn_mm=False):
    if lenIn_cm:
        lenVal = lenVal / 100.
    elif lenIn_mm:
        lenVal = lenVal / 1000.
    else:
        lenVal = float(lenVal)
    return lenVal







class quickThermalCalc():
    def __init__(self, name, area_sqm=None, heatPower_W=None, albedo=0.0, distToSun_AU=1.0,
                 verbose=False):
        self.name = name
        self.area_sqm = area_sqm
        self.heatPower_W = heatPower_W
        self.albedo = albedo
        self.distToSun_AU = distToSun_AU
        if verbose:
            print "\nStarting a quickThermalCalc object named", self.name, 'has:'
            if area_sqm is not None:
                print "a surface area of " + str(area_sqm) + " square meters,"
            if heatPower_W is not None:
                print "an internal heat power of " + str(heatPower_W) + " Watts,"
            print "the albedo (fraction of light reflected) is " + str(albedo) + "."
            print 'and ' + str(distToSun_AU) + ' astronomical units from the Sol.\n'


    def calcAreaOfRectangularPrism(self, sideA, sideB, sideC, lenIn_m=True, lenIn_cm=False, lenIn_mm=False,
                                   verbose=False):
        sideA_m = convertLenUnitsTo_m(sideA, lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
        sideB_m = convertLenUnitsTo_m(sideB, lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
        sideC_m = convertLenUnitsTo_m(sideC, lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
        self.area_sqm = (sideA_m * sideB_m * 2.0) + (sideB_m * sideC_m * 2.0) + (sideC_m * sideA_m * 2.0)
        if verbose:
            print "The calculated Surface Area of", self.name, \
                "(a rectangular prism) is", self.area_sqm, 'square meters.\n'


    def calcAreaOfAside(self, sideA, sideB, lenIn_m=True, lenIn_cm=False, lenIn_mm=False,
                        verbose=False):
        sideA_m = convertLenUnitsTo_m(sideA, lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
        sideB_m = convertLenUnitsTo_m(sideB, lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
        self.area_sqm = (sideA_m * sideB_m)
        if verbose:
            print "The calculated Surface Area for", self.name, \
                "(one side) is", self.area_sqm, 'square meters.\n'


    def calcHeatPower(self, current_A, voltage_V, verbose=False):
        self.heatPower_W = float(current_A) * float(voltage_V)
        if verbose:
            print "The calculated heat power of", self.name, "is", self.heatPower_W, 'Watts.\n'


    def calcCrossSectionsOfRectangularPrism(self, sideA, sideB, sideC, lenIn_m=True, lenIn_cm=False, lenIn_mm=False,
                                            verbose=False):
        sideA_m = convertLenUnitsTo_m(sideA, lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
        sideB_m = convertLenUnitsTo_m(sideB, lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
        sideC_m = convertLenUnitsTo_m(sideC, lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
        [minSide, middleSide, maxSide] = sorted([sideA_m, sideB_m, sideC_m])
        self.minCrossSection_sqm = minSide * middleSide
        # this is not totally correct but is close, real max is bigger
        self.maxCrossSection_sqm = middleSide * maxSide * sqrtOf2
        if verbose:
            print "The minimum calculated cross section of", self.name, \
                "(a rectangular prism) is", self.minCrossSection_sqm, 'square meters.'
        if verbose:
            print "The maximum calculated cross section of", self.name, \
                "(a rectangular prism) is", self.maxCrossSection_sqm, 'square meters.\n'


    def calcSunPower_W(self, verbose=False):
        absorbedFraction = 1.0 - self.albedo
        self.solarPowerPerArea_W_sqm = (solarPowerPerAreaEarth_W_sqm / ((self.distToSun_AU ** 2.0))) * absorbedFraction
        self.minSunPower_W = self.minCrossSection_sqm * self.solarPowerPerArea_W_sqm
        self.maxSunPower_W = self.maxCrossSection_sqm * self.solarPowerPerArea_W_sqm
        if verbose:
            print "The minimum power absorbed from the Sun by", self.name, "is", self.minSunPower_W, 'Watts.'
            print "The maximum power absorbed from the Sun by", self.name, "is", self.maxSunPower_W, 'Watts.\n'


    def calcTotalPower(self, verbose=False):
        self.minTotalPower_W = self.heatPower_W + self.minSunPower_W
        self.maxTotalPower_W = self.heatPower_W + self.maxSunPower_W
        if verbose:
            print "The minimum total power radiated by", self.name, "is", self.minTotalPower_W, 'Watts.'
            print "The maximum total power radiated by", self.name, "is", self.maxTotalPower_W, 'Watts.\n'


    def calcTemp(self, verbose=False):
        self.minTemp = (self.minTotalPower_W /  (stefanBoltzmann * self.area_sqm)) ** 0.25
        self.maxTemp = (self.maxTotalPower_W /  (stefanBoltzmann * self.area_sqm)) ** 0.25
        if verbose:
            print "The minimum Temperature of", self.name, "is", self.minTemp, 'Kevin.'
            print "The maximum Temperature of", self.name, "is", self.maxTemp, 'Kevin.\n'


if __name__ == '__main__':
    verbose = True

    # in centimeters
    sideA = 10
    sideB = 10
    sideC = 11.35 * 1.5


    testCubeSat = quickThermalCalc(name='one side for a heat sink',
                                   heatPower_W=maxPower_1UnitHigh_W * 1.5,
                                   albedo=0.0,
                                   distToSun_AU=1.0,
                                   verbose=verbose)
    testCubeSat.calcAreaOfAside(sideB, sideC, lenIn_cm=True, verbose=verbose)
    testCubeSat.calcCrossSectionsOfRectangularPrism(sideA, sideB, sideC, lenIn_cm=True, verbose=verbose)
    testCubeSat.calcSunPower_W(verbose=verbose)
    testCubeSat.calcTotalPower(verbose=verbose)
    testCubeSat.calcTemp(verbose=verbose)


    testCubeSat = quickThermalCalc(name='all sides for a heat sink',
                                   heatPower_W=maxPower_1UnitHigh_W * 1.5,
                                   albedo=0.0,
                                   distToSun_AU=1.0,
                                   verbose=verbose)
    testCubeSat.calcAreaOfRectangularPrism(sideA, sideB, sideC, lenIn_cm=True, verbose=verbose)
    testCubeSat.calcCrossSectionsOfRectangularPrism(sideA, sideB, sideC, lenIn_cm=True, verbose=verbose)
    testCubeSat.calcSunPower_W(verbose=verbose)
    testCubeSat.calcTotalPower(verbose=verbose)
    testCubeSat.calcTemp(verbose=verbose)








