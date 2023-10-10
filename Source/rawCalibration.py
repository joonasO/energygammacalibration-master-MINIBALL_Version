import numpy as np
import scipy
import matplotlib.pyplot as plt
import os
#
#Author:Minna Luoma
#Places of peaks (channel numbers)

#Energies of the peaks

writeToFile="Y"
def remove_negs(num_list):
    r = num_list[:]
    #print(r)
    r=list(r)
    for item in num_list:
        if item <= 0:
           r.remove(item)
    #print(r)
    return r
#raw_calibration function need to know: places of the peaks, energies of the peaks
#and energy difference between a calculated energy value and given energy value where the function try to find peaks
def rawCalibration(channels,energies,energyLow,energyHigh,energyCalibration1,energyCalibration2,fileName,outputPath,writeToFile):
    outputPath=outputPath+'/RawCalibration/'
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
    Np = 2 #Number of parameters
    channels=remove_negs(channels)



    #Determine the energies for starting calibration calculations
    energyCalibrations = (energyCalibration1,energyCalibration2)

    #Define the matrix to which the calculated constants are stored
    F = np.zeros((Np,len(channels),len(channels)))
    #Solve the linear equation group and record the calculated values from there
    for i in range(0,len(channels),1):
        for j in range(i+1,len(channels),1):
            chosenChannels = (channels[i],channels[j])
            E = np.zeros( (len(chosenChannels),Np) )
            E[:,0] = 1
            E[:,1] = chosenChannels
            coefficients = np.linalg.lstsq(E, energyCalibrations,rcond=None)[0]
            F[0][i][j] = coefficients[0] #calculated constant term
            F[1][i][j] = coefficients[1] #slope for channels

    #Define a matrix to which the calculated energies are stored
    calculatedEnergies = np.zeros((len(channels),len(channels),len(channels)))

    #This loop calculate energies with different calibrations
    for i in range(0,len(channels),1):
        for j in range(i+1,len(channels),1):
            for k in range(0,len(channels),1):
                if (F[1][i][j]*channels[k]+F[0][i][j] > 0): #Stores only energies with positive values
                    calculatedEnergies[i][j][k] = F[1][i][j]*channels[k]+F[0][i][j]
                    #if i==0 and j>1:
                        #print(str(calculatedEnergies[i][j][k])+"\n")

    #Define a matrix to which found peaks and coresponding channel numbers are stored

    L = np.zeros((Np,len(channels)))
    channelEnergies = np.zeros((Np,len(channels)))

    #Intialise variables for different peaks
    foundPeaks0 = 0
    foundPeaks1 = 0
    Va = 0 #Variable for "best" estimate of constant
    Vb = 0 #Variable for "best" estimate of slope

    #Next check how many peak energies can be found by using the fit function and the limit what user has defined for peak. This limit is defined in calibration file.
    for i in range(0, len(channels),1):
        for j in range(i+1, len(channels),1):
            for k in range(0, len(channels),1):
                for e in range(0, len(energies),1):
                    if (energies[e]-energyLow[e] < calculatedEnergies[i][j][k] < energyHigh[e]+energies[e]):
                        foundPeaks0 = foundPeaks0 + 1
                        L[0][foundPeaks0-1] = energies[e]
                        L[1][foundPeaks0-1]= channels[k]
                        if (L[0][foundPeaks0-2]==L[0][foundPeaks0-1]):
                            file = open(outputPath+"raw_calibration"+fileName+"_TwoPeaks.txt","w+")
                            file.write("L[0][foundPeaks0-2]:"+str(L[0][foundPeaks0-2]) + "\n")
                            file.write("L[0][foundPeaks0-1]:"+str(L[0][foundPeaks0-1]) + "\n")
                            if(abs(calculatedEnergies[i][j][k]-energies[e])<=abs(calculatedEnergies[i][j][k-1]-energies[e])):
                                L[0][foundPeaks0-2]=L[0][foundPeaks0-1]
                                L[1][foundPeaks0-2]= channels[k]
                                foundPeaks0=foundPeaks0-1
                                file.write("abs(calculatedEnergies[i][j][k]-energies[e])<=abs(calculatedEnergies[i][j][k-1]-energies[e]):"+"calculatedEnergies[i][j][k-1]:"+str(calculatedEnergies[i][j][k-1])+"calculatedEnergies[i][j][k]:"+str(calculatedEnergies[i][j][k])+"energies[e]"+str(energies[e]) + "\n")
                            if(abs(calculatedEnergies[i][j][k]-energies[e])>abs(calculatedEnergies[i][j][k-1]-energies[e])):
                                file.write("abs(calculatedEnergies[i][j][k]-energies[e])>abs(calculatedEnergies[i][j][k-1]-energies[e]):"+"calculatedEnergies[i][j][k-1]:"+str(calculatedEnergies[i][j][k-1])+"calculatedEnergies[i][j][k]:"+str(calculatedEnergies[i][j][k])+"energies[e]"+str(energies[e]) + "\n")
                                foundPeaks0=foundPeaks0-1
                            file.close()


            if foundPeaks0 > foundPeaks1:
                foundPeaks1 = foundPeaks0
                foundPeaks0 = 0
                Va = F[0][i][j]
                Vb = F[1][i][j]
                channelEnergies = np.copy(L)
            foundPeaks0 = 0

    channelEnergies[1,:].sort()
    channelEnergies[0,:].sort()
    Va=str(Va)
    Vb=str(Vb)
    stringFoundPeaks1 = str(foundPeaks1)
    stringChannelEnergies = str(channelEnergies)

    if (writeToFile == 'Y'):
        try:
            file = open(outputPath+"raw_calibration"+fileName+"_file.txt","w+")
            file.write("Number of peaks:"+stringFoundPeaks1 + "\n")
            file.write("Constant:"+Va + "\n")
            file.write("Slope:"+Vb + "\n")
            file.write("Energies and channels:"+stringChannelEnergies+"\n")
            file.write("Calculated Energies:"+str(calculatedEnergies))
            file.close()
        except IOError:
            print ("problem to write file")
    

    return channelEnergies[1,:], channelEnergies[0,:]
