import peakSearchGui
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import gaussianFit
import energyCalibration
import readEnergies
import rawCalibration
import readGUIFile
import readSettings
import readInputFile
import readOutput
import datetime
from pathlib import Path
#Author:Joonas Ojala
#2019

#guiCommand controls the data flow from program to program. The principle here is that one program is doing one task. It also tell user the phase of the calibration at terminal
def guiCommand():

    #Forming the list filled with path to input files
    inputFiles=readGUIFile.readGUIFiles()
    #Forming the list filled with path to outout folder
    outputPath=readOutput.readOutput()
    #It is possible to choose the just have gain output but this is not recomended
    output="Y"
    output=output.replace("\n","").replace(" ","")


    newList=[]
    #Take of few extra marks written in file
    for i in inputFiles:
        i=i.replace('\n','').replace('\r ','')
        newList.append(i)
    inputFiles=newList

    #Read the energy file which is written by user and contains the energy
    energiesOrig,energiesLow,energiesHigh,selection1,selection2=readEnergies.readEnergies("","calibration.txt")
    #Read the settings file which is written based the settings select by user
    channelStart,channelStop,minPeaks,maxPeaks,peakInChannelWidth,fitGaussian=readSettings.readSettings()
    #Change type of the parameters
    channelStart=int(channelStart)
    channelStop=int(channelStop)
    minPeaks=int(minPeaks)
    maxPeaks=int(maxPeaks)
    peakInChannelWidth=float(peakInChannelWidth)
    fitGaussian=int(fitGaussian)
    #Initialation prominence which describes the how peak stick out from background
    prominence=10000
    peaksnumber=len(energiesOrig)
    lengthInputFileList=len(inputFiles)
    #Initialation of filenumber which is just for to produce the precent number for user of status of process
    fileNumber=0

    #Write some information to EnergyCalibration.txt
    outputPathEnergyCalib=outputPath+'/Energy_Calibration/'
    #Create folder for the figures of fit
    if not os.path.exists(outputPathEnergyCalib):
        os.makedirs(outputPathEnergyCalib)

    f= open(outputPathEnergyCalib+'EnergyCalibration.txt',"a+")
    now = datetime.datetime.now()
    f.write("#This calibration is made in: "+str(now.strftime('%Y-%m-%d %H:%M:%S'))+"\r\n")
    f.write("#(c)Joonas Ojala 2019"+"\r\n")
    f.write("#This file contains the first and second order polynomial for gains to Grain.\r\n")
    f.write("#User need to change the right DAQ channel number according to tdrname file.\r\n")
    f.close()


    #Looping over the input files and doing the calibration for each calibration spectrum
    #channels, counts= readInputFile.readInputFiles(inputFiles,fileNumber,lengthInputFileList)
    for inputFile in inputFiles:
            channels, counts= readInputFile.readInputFiles(inputFile,fileNumber,lengthInputFileList)

        #Need to change the array type
            channels=np.asarray(channels)
            counts=np.asarray(counts)
            inputFile=inputFile.replace('.dat','')
            path,slash,fileName=inputFile.rpartition('/')


            peak_index,peakWidth_index,prominence,peak_channel,peak_width=peakSearchGui.peakSearchGui(channels,counts,fileName,channelStart,channelStop,outputPath,output,prominence,peaksnumber,minPeaks,maxPeaks,peakInChannelWidth)
            print(peak_index)
            if(fitGaussian==1):
                peaks=[]
                for i in range(len(peak_index)):
                    position=gaussianFit.gaussianFitOnData(channels,counts,peak_index[i],peak_channel[i],peakWidth_index[i],peak_width[i],fileName,outputPath,output)
                    peaks=np.append(peaks,position)
                positionsOrig=[]
                for peak in peaks:
                    peak=peak/(channels[1]-channels[0])
                    positionsOrig=np.append(positionsOrig,peak)
            #If user don't want to use gaussian. Remeber to take central bin
            else:
                positionsOrig=[]
                for peak in peak_index:
                    peakCenter=peak#+0.5*(channels[1]-channels[0])
                    positionsOrig=np.append(positionsOrig,peakCenter)
            positions,energies=rawCalibration.rawCalibration(positionsOrig,energiesOrig,energiesLow,energiesHigh,selection1,selection2,fileName,outputPath,output)
            positions=np.trim_zeros(positions,'fb')

            if(len(positions)<=len(energiesOrig)-len(energiesOrig)*0.15):
                for i in range(0,len(energiesOrig),1):
                    for j in range(i+1, len(energiesOrig),1):
                        positions1,energies1=rawCalibration.rawCalibration(positionsOrig,energiesOrig,energiesLow,energiesHigh,energiesOrig[i],energiesOrig[j],fileName,outputPath,output)
                        positions1=np.trim_zeros(positions1,'fb')
                        energies1=np.trim_zeros(energies1,'fb')
                        if len(positions1)>len(positions):
                            positions=positions1
                            energies=energies1

            positions=positions*(abs(channels[0]-channels[1]))
            energies=np.trim_zeros(energies,'fb')
            positions=np.trim_zeros(positions,'fb')

            energyCalibration.energyCalibrations(positions,energies,fileName,outputPath,1)

    else:
        print("No file")
        fileNumber=fileNumber+1
    print("100% \nCalibration complete!")
