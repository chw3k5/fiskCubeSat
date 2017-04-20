from constantAndConversion import yearToSec, MeVToJoule, keVToJoule

class isotope():
   def __init__(self, stable, name):
       self.name = name
       if stable:
           self.halfLife = float('inf')
       else:
           self.halfLife = 0.0
           self.decayProducts = []
           self.decayEnergies_J = []
           self.decayProbabilities = []
           self.radiationType = []


def getBa137():
    Ba137_stable = True
    Ba137 = isotope(stable=Ba137_stable, name='Ba137')
    return Ba137


def getBa137m():
    Ba137m_stable = False
    Ba137m = isotope(stable=Ba137m_stable, name='Ba137m')
    Ba137m.halfLife = float(153)

    decayProb1 =  0.9007
    decayEnergy1_MeV = 0.661659
    decayEnergy1_J =  MeVToJoule * decayEnergy1_MeV
    radiationType1 = 'gamma'
    productName1 = 'Ba137'

    decayProb1 =  0.0206
    decayEnergy1_MeV = 31.8174
    decayEnergy1_J =  keVToJoule * decayEnergy1_MeV
    radiationType1 = 'xRay'
    productName1 = 'Ba137'





    setattr(Ba137m, productName1, getBa137())



    return Ba137m





def getCs137():
    Cs137_stable = False
    Cs137 = isotope(stable=Cs137_stable, name='Cs137')
    Cs137_halfLife_yr = float(30.17)
    Cs137.halfLife = Cs137_halfLife_yr * yearToSec

    decayProb1 = 0.946
    decayEnergy1_MeV = 0.5120
    decayEnergy1_J =  MeVToJoule * decayEnergy1_MeV
    radiationType1 = '-Beta'
    productName1 = 'Ba137m'
    setattr(Cs137, productName1, getBa137m())

    decayProb2 = 0.054
    decayEnergy2_MeV = 1.174
    decayEnergy2_J =  MeVToJoule * decayEnergy2_MeV
    radiationType2 = '-Beta'
    productName2 = 'Ba137'
    setattr(Cs137, productName2, getBa137())


    Cs137.decayProducts.append(decayProb1)
    Cs137.decayProducts.append(decayProb2)
    Cs137.decayEnergies_J.append(decayEnergy1_J)
    Cs137.decayEnergies_J.append(decayEnergy2_J)
    Cs137.decayProbabilities.append(productName1)
    Cs137.decayProbabilities.append(productName2)
    Cs137.radiationType.append(radiationType1)
    Cs137.radiationType.append(radiationType2)




    return Cs137









if __name__ == "__main__":
   print Cs137.halflife_yr


