'''
In 3-d the average projected area of a convex solid is 1/4 the surface area, as
Cauchy showed in the 19th century.
'''

import numpy
radiusOrEarth_m = 6.371e6
speedOfLight_m_s = float(299792458)


class radCount():
    def __init__(self, name, verbose=False):
        self.name = name
        if verbose:
            print "\nStarting a quickThermalCalc object named", self.name

    def calcRadSolidAngleFraction(self, height_m, radius_m=None):
        if radius_m is None:
            radius_m = radiusOrEarth_m
        self.sldAngFraction = 1.0 - numpy.sqrt(1.0 - ((radius_m ** 2) / ((radius_m + height_m) ** 2)) )

    def rectangularCrossSection(self, sideA, sideB):
        self.crossSection_m2 = float(sideA) * float(sideB)

    def particleFlux(self, particleDensity):
        self.particleFlux = particleDensity * speedOfLight_m_s * self.sldAngFraction

    def calcCounts(self,  particleDensity,  efficiency=1.0):
        self.counts = self.particleFlux * self.crossSection_m2 * efficiency