import sys
import numpy as np

def readEnergies(energyPath,energyFile):
    path=energyPath+energyFile
    with open(path,"r") as f:
        input=f.readlines()
        energies=[]
        energiesLow=[]
        energiesHigh=[]
        selections=[]
        for line in input:
            if line[0]!="#":
                inputs=line.split(",")
                if len(inputs)>1:
                    energy=inputs[0]
                    energyLow=inputs[1]
                    try:
                        if(inputs[2]=="*"):
                            selections.append(energy)
                            energyHigh=energyLow
                        else:
                         energyHigh=inputs[2]
                         if(len(inputs)>2):
                             if(inputs[3]=="*"):
                                 selections.append(energy)

                    except:
                        energyHigh=energyLow
                    energy=float(energy)
                    energyLow=float(energyLow.replace("\n",""))
                    energyHigh=float(energyHigh.replace("\n",""))
                    energies.append(energy)
                    energiesLow.append(energyLow)
                    energiesHigh.append(energyHigh)
    energies=np.asarray(energies)
    energiesLow=np.asarray(energiesLow)
    energiesHigh=np.asarray(energiesHigh)
    if(len(selections)>1):
        if(selections>2):
            print("There is more than two is selected as starting points for linear calibration in calibration file! Program will select first and last")
        selections1=float(selection[0])
        selections2=float(selection[-1])
    else:
        selections1=float(energies[0])
        selections2=float(energies[-1])
    return energies,energiesLow,energiesHigh,selections1,selections2
