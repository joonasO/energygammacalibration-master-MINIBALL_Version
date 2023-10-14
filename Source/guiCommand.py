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
    for inputFile in inputFiles:
        process=int(float(fileNumber)/float(lengthInputFileList)*100)
        print(str(process)+"%")
        print("File name: "+inputFile)
        file=Path(inputFile)
        if(file.is_file()):
            with open(inputFile,"r") as f:
                counts=[]
                channels=[]
                for line in f:
                    channel,count=line.split(" ")
                    channel=float(channel)
                    count=float(count.strip())
                    channels.append(channel)
                    counts.append(count)

        #Need to change the array type
            channels=np.asarray(channels)
            counts=np.asarray(counts)
            inputFile=inputFile.replace('.dat','')
            path,slash,fileName=inputFile.rpartition('/')


            peakPosition_channel,peakWidth,prominence=peakSearchGui.peakSearchGui(channels,counts,fileName,channelStart,channelStop,outputPath,output,prominence,peaksnumber,minPeaks,maxPeaks,peakInChannelWidth)

            if(fitGaussian==1):
                peaks=[]
                for i in range(len(peakPosition_channel)):
                    position=gaussianFit.gaussianFitOnData(channels,counts,peakPosition_channel[i],peakWidth[i],fileName,outputPath,output)
                    peaks=np.append(peaks,position)
                positionsOrig=[]
                for peak in peaks:
                    peak=peak/(channels[1]-channels[0])
                    positionsOrig=np.append(positionsOrig,peak)
            #If user don't want to use gaussian. Remeber to take central bin
            else:
                positionsOrig=[]
                for peak in peakPosition:
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
