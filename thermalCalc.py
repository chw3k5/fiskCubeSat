import numpy
from numpy import pi, sqrt

stefanBoltzmann = 5.670367e-8 # W / (m^2 K^4)
earthDistanceToSun_m = 149.6e9 # meters

diameterOfSun_m = 1.391e9
diameterOfEarth_m = 12.742e6

temperatureOfSun_K = 5778.0
temperatureOfEarth_K = 287.0


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


def calcArea(size, type='rectangle',
             lenIn_m=True, lenIn_cm=False, lenIn_mm=False):
        if type == 'rectangle':
            sideA_m = convertLenUnitsTo_m(size[0], lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
            sideB_m = convertLenUnitsTo_m(size[1], lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
            area_sqm = (sideA_m * sideB_m)
        elif type == 'disk':
            radius = convertLenUnitsTo_m(size[0], lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
            area_sqm = pi * (radius ** 2)
        elif type == 'rectangularPrism':
            sideA_m = convertLenUnitsTo_m(size[0], lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
            sideB_m = convertLenUnitsTo_m(size[1], lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
            sideC_m = convertLenUnitsTo_m(size[2], lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
            area_sqm = (sideA_m * sideB_m * 2.0) + (sideB_m * sideC_m * 2.0) + (sideC_m * sideA_m * 2.0)
        elif type == 'sphere':
            radius = convertLenUnitsTo_m(size[0], lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
            area_sqm = 4.0 * pi * (radius ** 2)
        else:
            print "Type:", type, "was unexpected."
            area_sqm = raw_input('enter an area in square meters, or start over and use an expected type.')
        return area_sqm


def calcCrossSection(size, type='rectangle',
             lenIn_m=True, lenIn_cm=False, lenIn_mm=False):
        if type == 'rectangle':
            sideA_m = convertLenUnitsTo_m(size[0], lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
            sideB_m = convertLenUnitsTo_m(size[1], lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
            maxCrossSection_sqm = (sideA_m * sideB_m)
            minCrossSection_sqm = 0.0
            aveCrossSection_sqm = maxCrossSection_sqm / 2.0
        elif type == 'disk':
            radius = convertLenUnitsTo_m(size[0], lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
            maxCrossSection_sqm = pi * (radius ** 2)
            minCrossSection_sqm = 0.0
            aveCrossSection_sqm = maxCrossSection_sqm / 2.0
        elif type == 'rectangularPrism':
            sideA_m = convertLenUnitsTo_m(size[0], lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
            sideB_m = convertLenUnitsTo_m(size[1], lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
            sideC_m = convertLenUnitsTo_m(size[2], lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)

            [minSide, middleSide, maxSide] = sorted([sideA_m, sideB_m, sideC_m])
            minCrossSection_sqm = minSide * middleSide
            # this is not totally correct but is close, real max is bigger
            maxCrossSection_sqm = middleSide * maxSide * sqrtOf2
            # In 3-d the average projected area of a convex solid is 1/4 the surface area, as
            # Cauchy showed in the 19th century.
            surfaceArea = calcArea(size=size, type='rectangularPrism', lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
            aveCrossSection_sqm = surfaceArea * 0.25
        elif type == 'sphere':
            radius = convertLenUnitsTo_m(size[0], lenIn_m=lenIn_m, lenIn_cm=lenIn_cm, lenIn_mm=lenIn_mm)
            minCrossSection_sqm =  pi * (radius ** 2)
            maxCrossSection_sqm = minCrossSection_sqm
            aveCrossSection_sqm = minCrossSection_sqm
        else:
            print "Type:", type, "was unexpected."
            maxCrossSection_sqm = raw_input('enter an area in square meters for the maximum cross section, or start over and use an expected type.')
            minCrossSection_sqm = raw_input('enter an area in square meters for the minimum cross section, or start over and use an expected type.')
            aveCrossSection_sqm = raw_input('enter an area in square meters for the average cross section, or start over and use an expected type.')
        return maxCrossSection_sqm, minCrossSection_sqm, aveCrossSection_sqm





class radiationSource():
    def __init__(self, name, size_m, distance_m=earthDistanceToSun_m, temperature_K=300.0,  albedo=1.0, shape='sphere'):
        self.name = name
        self.shape = shape
        self.distance_m = float(distance_m)
        self.temperature_K = float(temperature_K)
        self.albedo = float(albedo)
        if shape == 'sphere':
            self.diameter_m = float(size_m[0])
            self.radius_m = self.diameter_m * 0.5
            self.luminosity = stefanBoltzmann * (self.temperature_K ** 4.0) * 4.0 * pi * (self.radius_m ** 2.0)
            hypotenuse = sqrt((self.radius_m ** 2.0) + (self.distance_m ** 2.0))
            self.solidAngle = 2.0 * pi * (1.0 - (self.distance_m / hypotenuse))
            self.flux = self.luminosity / (4.0 * pi * (self.distance_m ** 2.0))
            self.absorbedFlux_W_sqm = self.flux * (1.0 - self.albedo)


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
            print "The minimum power absorbed from the Sun by", self.name, "is", self.minSunPower_W, 'Watts.'
            print "The maximum power absorbed from the Sun by", self.name, "is", self.maxSunPower_W, 'Watts.'
            print "The average power absorbed from the Sun by", self.name, "is", self.aveSunPower_W, 'Watts.\n'

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

    # in centimeters
    sideA = 10
    sideB = 10
    sideC = 11.35 * 1.5

    floatAltitude = float(39624.0)
    floatRadius = floatAltitude + (diameterOfEarth_m / 2.0)

    sunAlbedo = float(0)
    earthAlbedo = float(0)



    sunSource = radiationSource(name='Sol', size_m=[diameterOfSun_m], distance_m=earthDistanceToSun_m,
                                temperature_K=temperatureOfSun_K, albedo=sunAlbedo)
    earthSource = radiationSource(name='Earth', size_m=[diameterOfEarth_m], distance_m=floatRadius,
                                temperature_K=temperatureOfEarth_K, albedo=earthAlbedo)



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








