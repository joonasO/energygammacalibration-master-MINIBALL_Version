import sys

def readSettings():
        mySettings="Settings.txt"
        settingsFile=open(mySettings,"r")
        settings=settingsFile.readlines()
        channelStart=0
        channelStop=16384
        minPeaks=2
        maxPeaks=5
        peakWidth=50
        gaussianFit=1
        for line in settings:
            inputs=line.split(":")
            if inputs[0]=="Channel range (min, max)":
                channelStart,channelStop=inputs[1].split(",")
            if inputs[0]=="Amount of the extra peaks for calibration (min, max)":
                minPeaks,maxPeaks=inputs[1].split(",")
            if inputs[0]=="Peak width(in units of channels)":
                    peakWidth=inputs[1]
            if inputs[0]=="Gaussian fit":
                    gaussianFit=inputs[1]
        settingsFile.close()
        return channelStart,channelStop,minPeaks,maxPeaks,peakWidth,gaussianFit
