from numpy import pi, sqrt, arcsin, arccos

piHalf = pi * 0.5
pi2 = pi * 2.0
pi4 = pi * 4.0
sqrtOf2 = sqrt(2.0)

stefanBoltzmann = 5.670367e-8 # W / (m^2 K^4)
elementaryCharge = 1.60217662e-19 # C = A s = F V


CiToBq = 3.7e10 # Bq / Ci
yearToSec = float(31556952) # 31556952 seconds / 1 year
eVToJoule = elementaryCharge # 1.60217662e-19 J / 1 eV
keVToJoule = elementaryCharge / float(1.0e3)  # 1.60217662e-16 J / 1 keV
MeVToJoule = elementaryCharge / float(1.0e6)  # 1.60217662e-13 J / 1 MeV

earthDistanceToSun_m = 149.6e9 # meters

diameterOfSun_m = 1.391e9
diameterOfEarth_m = 12.742e6
radiusOfEarth_m = diameterOfEarth_m * 0.5

temperatureOfSun_K = 5778.0
temperatureOfEarth_K = 287.0


solarPowerPerAreaEarth_W_sqm = 1368. # W / m^2
speedOfLight_m_s = float(299792458)
