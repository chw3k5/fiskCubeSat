import numpy
from radiationCalc import piHalf, pi, pi2, pi4, maxPower_1UnitHigh_W, stefanBoltzmann,\
    earthDistanceToSun_m, temperatureOfEarth_K, diameterOfEarth_m,\
    temperatureOfSun_K, diameterOfSun_m, calcArea, calcCrossSection, thermalRadiationSource



class quickThermalCalc():
    def __init__(self, name, radiationSources, heatPower_W=None,
                 verbose=False):
        self.name = name
        self.heatPower_W = heatPower_W
        self.radiationSources = radiationSources
        if verbose:
            print "\nStarting a quickThermalCalc object named", self.name, 'has:'
            if heatPower_W is not None:
                print "an internal heat power of " + str(heatPower_W) + " Watts,"

            if self.radiationSources != []:
                print "\nThere are", len(self.radiationSources), "radiation sources.\n"
                for (sourceIndex, radiationSource) in list(enumerate(self.radiationSources)):
                    print "Radiation source number", 1 + sourceIndex, "is:", radiationSource.name
                    print 'at a distance of', radiationSource.distance_m, 'meters,'
                    print 'a luminosity of ', radiationSource.luminosity, 'Watts,'
                    print 'a flux of ', radiationSource.flux, 'Watts / m^2'
                    if radiationSource.distance_m > 1.0e9:
                        print 'at a distance of', radiationSource.distance_m / earthDistanceToSun_m, 'AU.'
                    else:
                        print 'at a distance of', radiationSource.distance_m, 'meters.\n'
                    print "The albedo for an absorber seeing this source (fraction of light reflected) is " + str(radiationSource.albedo) + ".\n"

                print ' '




    def calcAbsorberArea(self, size, type='rectangularPrism',
                         lenIn_m=True, lenIn_cm=False, lenIn_mm=False,
                         verbose=False):
        self.absorberType = type
        self.absorberArea_sqm = calcArea(size=size, type=type,
                                         lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
        if verbose:
            print "The calculated Convex Absorber Area for an absorber of type", self.radiatorType, \
                 'is', self.radiatorArea_sqm, 'square meters.\n'


    def calcRadiatorArea(self, size, type='rectangle',
                     lenIn_m=True, lenIn_cm=False, lenIn_mm=False,
                     verbose=False):
        self.radiatorType = type
        self.radiatorArea_sqm = calcArea(size=size, type=type,
                                         lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
        if verbose:
            print "The calculated Radiator Area for a radiator of type", self.radiatorType, \
                 'is', self.radiatorArea_sqm, 'square meters.\n'


    def calcHeatPower(self, current_A, voltage_V, verbose=False):
        self.heatPower_W = float(current_A) * float(voltage_V)
        if verbose:
            print "The calculated heat power of", self.name, "is", self.heatPower_W, 'Watts.\n'


    def calcCrossSections(self, size, type='rectangularPrism', lenIn_m=True, lenIn_cm=False, lenIn_mm=False,
                                            verbose=False):
        self.crossSectionType = type
        self.maxCrossSection_sqm, self.minCrossSection_sqm, self.aveCrossSection_sqm = \
            calcCrossSection(size=size, type=type, lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
        if verbose:
            print "The minimum calculated cross of", self.crossSectionType, " cross section for", self.name, \
                self.minCrossSection_sqm, 'square meters.'
            print "The maximum calculated cross of", self.crossSectionType, " cross section for",\
                self.maxCrossSection_sqm, 'square meters.'
            print "The average calculated cross of", self.crossSectionType, " cross section for",\
                self.aveCrossSection_sqm, 'square meters.\n'

    def calcAbsorbedPower(self, verbose=False):
        self.absorbedFlux_W_sqm = 0.0
        for radiationSource in self.radiationSources:
            self.absorbedFlux_W_sqm += radiationSource.absorbedFlux_W_sqm
        self.minSunPower_W = self.minCrossSection_sqm * self.absorbedFlux_W_sqm
        self.maxSunPower_W = self.maxCrossSection_sqm * self.absorbedFlux_W_sqm
        self.aveSunPower_W = self.aveCrossSection_sqm * self.absorbedFlux_W_sqm
        if verbose:
            print "The minimum power absorbed by", self.name, "is", self.minSunPower_W, 'Watts.'
            print "The maximum power absorbed by", self.name, "is", self.maxSunPower_W, 'Watts.'
            print "The average power absorbed by", self.name, "is", self.aveSunPower_W, 'Watts.\n'

    def calcTotalPower(self, verbose=False):
        self.minTotalPower_W = self.heatPower_W + self.minSunPower_W
        self.maxTotalPower_W = self.heatPower_W + self.maxSunPower_W
        self.aveTotalPower_W = self.heatPower_W + self.aveSunPower_W
        if verbose:
            print "The minimum total power radiated by", self.name, "is", self.minTotalPower_W, 'Watts.'
            print "The maximum total power radiated by", self.name, "is", self.maxTotalPower_W, 'Watts.'
            print "The average total power radiated by", self.name, "is", self.aveTotalPower_W, 'Watts.\n'

    def calcTemp(self, verbose=False):
        self.minTemp = (self.minTotalPower_W /  (stefanBoltzmann * self.radiatorArea_sqm)) ** 0.25
        self.maxTemp = (self.maxTotalPower_W /  (stefanBoltzmann * self.radiatorArea_sqm)) ** 0.25
        self.aveTemp = (self.aveTotalPower_W /  (stefanBoltzmann * self.radiatorArea_sqm)) ** 0.25
        if verbose:
            print "The minimum Temperature of", self.name, "is", self.minTemp, 'Kevin.'
            print "The maximum Temperature of", self.name, "is", self.maxTemp, 'Kevin.'
            print "The average Temperature of", self.name, "is", self.aveTemp, 'Kevin.\n'

if __name__ == '__main__':
    verbose = True

    doAllSides = True
    doOneSide = False

    # in centimeters
    sideA = 10
    sideB = 10
    sideC = 11.35 * 1.5

    floatAltitude = float(33.5e3)
    floatRadius = floatAltitude + (diameterOfEarth_m / 2.0)

    sunAlbedo = float(0.0)
    earthAlbedo = float(0.0)

    protonFlux = 4.0 / (100.0 ** 2.0) # protons / (m^2 s)


    sunSource = thermalRadiationSource(name='Sol', size_m=[diameterOfSun_m], distance_m=earthDistanceToSun_m,
                                temperature_K=temperatureOfSun_K, albedo=sunAlbedo)
    earthSource = thermalRadiationSource(name='Earth', size_m=[diameterOfEarth_m], distance_m=floatRadius,
                                temperature_K=temperatureOfEarth_K, albedo=earthAlbedo)


    if doOneSide:
        testCubeSat = quickThermalCalc(name='one side for a heat sink',
                                       radiationSources = [sunSource, earthSource],
                                       heatPower_W=maxPower_1UnitHigh_W * 1.5,
                                       verbose=verbose)
        testCubeSat.calcRadiatorArea(size=[sideB, sideC], type='rectangle', lenIn_cm=True, verbose=verbose)
        testCubeSat.calcAbsorberArea(size=[sideA, sideB, sideC], type='rectangularPrism', lenIn_cm=True, verbose=verbose)
        testCubeSat.calcCrossSections(size=[sideA, sideB, sideC], type='rectangularPrism',
                                                        lenIn_cm=True, verbose=verbose)
        testCubeSat.calcAbsorbedPower(verbose=verbose)
        testCubeSat.calcTotalPower(verbose=verbose)
        testCubeSat.calcTemp(verbose=verbose)

    if doAllSides:
        testCubeSat = quickThermalCalc(name='all sides for a heat sink', radiationSources = [sunSource, earthSource],
                                       heatPower_W=maxPower_1UnitHigh_W * 1.5,
                                       verbose=verbose)

        testCubeSat.calcRadiatorArea(size=[sideA, sideB, sideC], type='rectangularPrism', lenIn_cm=True, verbose=verbose)
        testCubeSat.calcAbsorberArea(size=[sideA, sideB, sideC], type='rectangularPrism', lenIn_cm=True, verbose=verbose)
        testCubeSat.calcCrossSections(size=[sideA, sideB, sideC], type='rectangularPrism',
                                                        lenIn_cm=True, verbose=verbose)
        testCubeSat.calcAbsorbedPower(verbose=verbose)
        testCubeSat.calcTotalPower(verbose=verbose)
        testCubeSat.calcTemp(verbose=verbose)








