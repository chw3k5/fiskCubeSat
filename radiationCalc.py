'''
In 3-d the average projected area of a convex solid is 1/4 the surface area, as
Cauchy showed in the 19th century.
'''
import numpy
from constantAndConversion import piHalf, pi, pi2, pi4, sqrtOf2,\
    sqrt, arcsin, arccos, \
    stefanBoltzmann, CiToBq, \
    earthDistanceToSun_m, diameterOfSun_m, diameterOfEarth_m, radiusOfEarth_m, \
    temperatureOfSun_K, temperatureOfEarth_K, solarPowerPerAreaEarth_W_sqm, speedOfLight_m_s



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


def calcSolidAnge(distanceToCenterOfBody, radiusOfBody):
    adjacentSide = sqrt(((distanceToCenterOfBody ** 2.0) - (radiusOfBody** 2.0)))
    solidAngle = pi2 * (1.0 - (adjacentSide / distanceToCenterOfBody))
    return solidAngle


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



class radiationField():
    def __int__(self, name, planetDiameter_m, altitudeFromPlanet_m, fromSpace=True):
        self.name = name
        self.fromSpace = fromSpace
        self.planetDiameter_m = float(planetDiameter_m)
        self.altitudeFromPlanet_m = float(altitudeFromPlanet_m)
        planetRadius = (self.planetDiameter_m / 2.0)
        self.distanceFromPlanetCenter_m = planetRadius + altitudeFromPlanet_m
        planetSolidAngle = calcSolidAnge(distanceToCenterOfBody=self.distanceFromPlanetCenter_m, radiusOfBody=planetRadius)
        if fromSpace:
            self.solidAngle = pi4 - planetSolidAngle
        else:
            self.solidAngle = planetSolidAngle
        self.solidAngleFraction = self.solidAngle / pi4

    def useFreeSpaceParticleFlux(self, freeSpaceParticleFlux=None,  particleSpeed=speedOfLight_m_s):
        self.particleFlux = float(freeSpaceParticleFlux) * self.solidAngleFraction
        self.particleSpeed = float(particleSpeed)
        self.fieldDensity_kg_m3 = self.particleFlux / self.particleSpeed
        self.radioactivity_ci = self.particleFlux / CiToBq

    def useFreeSpaceFieldDensity(self, freeSpaceFieldDensity_kg_m3=None,  particleSpeed=speedOfLight_m_s):
        self.fieldDensity_kg_m3 = float(freeSpaceFieldDensity_kg_m3)
        self.particleSpeed = float(particleSpeed)
        self.particleFlux = self.fieldDensity_kg_m3 * self.particleSpeed
        self.radioactivity_ci = self.particleFlux / CiToBq

    def useRadioactivity(self, curies, particleSpeed=speedOfLight_m_s):
        self.radioactivity_ci = float(curies)
        self.particleFlux = self.radioactivity_ci * CiToBq
        self.particleSpeed = float(particleSpeed)
        self.fieldDensity_kg_m3 = self.particleFlux / self.particleSpeed







class thermalRadiationSource():
    '''

    '''
    def __init__(self, name, size_m, distance_m=earthDistanceToSun_m, temperature_K=300.0,  albedo=0.0,
                 shape='sphere'):
        self.name = name
        self.shape = shape
        self.distance_m = float(distance_m)
        self.temperature_K = float(temperature_K)
        self.albedo = float(albedo)
        # Assumes Spherical source geometry
        self.diameter_m = float(size_m[0])
        self.radius_m = self.diameter_m * 0.5
        self.luminosity = stefanBoltzmann * (self.temperature_K ** 4.0) * pi4 * (self.radius_m ** 2.0)
        self.solidAngle = calcSolidAnge(distanceToCenterOfBody=self.distance_m, radiusOfBody=self.radius_m)
        self.flux = self.luminosity / (pi4 * (self.distance_m ** 2.0))
        self.absorbedFlux_W_sqm = self.flux * (1.0 - self.albedo)


class decayRadiationSource():
    '''

    '''
    def __init__(self, name, size_m, distance_m=earthDistanceToSun_m):
        self.name = name
        self.distance_m = float(distance_m)



        self.diameter_m = float(size_m[0])
        self.radius_m = self.diameter_m * 0.5
        self.luminosity = stefanBoltzmann * (self.temperature_K ** 4.0) * pi4 * (self.radius_m ** 2.0)
        self.solidAngle = calcSolidAnge(distanceToCenterOfBody=self.distance_m, radiusOfBody=self.radius_m)
        self.flux = self.luminosity / (pi4 * (self.distance_m ** 2.0))
        self.absorbedFlux_W_sqm = self.flux * (1.0 - self.albedo)


class radCount():
    def __init__(self, name, verbose=False):
        self.name = name
        if verbose:
            print "\nStarting a quickThermalCalc object named", self.name

    def calcRadSolidAngleFraction(self, height_m, radius_m=None):
        if radius_m is None:
            radius_m = radiusOfEarth_m
        solidAngle = calcSolidAnge(distanceToCenterOfBody=height_m + radius_m, radiusOfBody=radius_m)
        self.sldAngFraction = solidAngle / pi2

    def rectangularCrossSection(self, sideA, sideB):
        self.crossSection_m2 = float(sideA) * float(sideB)

    def particleFlux(self, particleDensity):
        self.particleFlux = particleDensity * speedOfLight_m_s * self.sldAngFraction

    def calcCounts(self,  particleDensity,  efficiency=1.0):
        self.counts = self.particleFlux * self.crossSection_m2 * efficiency