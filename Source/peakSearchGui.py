import matplotlib.pyplot as plt
import numpy as np
import sys
import os
from scipy import signal
def peakSearchGui(channels,counts,inputFile,startChannel,stopChannel,outputPath,output,prominenceOrig,peaknumber,minPeaks,maxPeaks,peakInChannelWidth):
    #Creates the folder for peaks
    outputPath=outputPath+'/Peaks/'
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)

        #counts_peakArea is the region of interest where the program start to find those peaks
    if(startChannel==-1 and stopChannel==-1):
        startChannel=channels[0]
        stopChannel=channels[-1]
    startChannels=int(startChannel/(channels[1]-channels[0]))
    stopChannels=int(stopChannel/(channels[1]-channels[0]))
    counts_peakArea=counts[startChannels:stopChannels]
    #Prominence means that how much the peak is differing towards the baseline


    peaks,peakProperties =signal.find_peaks(counts_peakArea, prominence=prominenceOrig,wlen=peakInChannelWidth,distance=peakInChannelWidth/2)
    prominence=prominenceOrig
    prominenceStep1=0
    prominenceStep2=0
    while((len(peaks)<(peaknumber+minPeaks) or len(peaks)>(peaknumber+maxPeaks))and prominence>1):

        if(len(peaks)<(peaknumber+minPeaks)):
            prominenceStep1=prominence
            prominence=prominence-abs(prominence-prominenceStep2)/2
            prominenceStep2=prominenceStep1
            if(prominence==prominenceStep2):
                break

        if (len(peaks)>(peaknumber+maxPeaks) and prominenceStep1!=0):

            prominenceStep1=prominence
            prominence=prominence+abs(prominence-prominenceStep2)/2
            prominenceStep2=prominenceStep1
            if(prominence==prominenceStep2):
                break
        if (len(peaks)>(peaknumber+maxPeaks) and prominenceStep1==0):
            prominence=prominence*2
        peaks,peakProperties= signal.find_peaks(counts_peakArea, prominence=prominence,wlen=peakInChannelWidth,distance=peakInChannelWidth/2)



    if(prominence<1):
        prominence=prominenceOrig


    #Peak index so that peakwidth works. The peak_index take account the changes in start Channel and stop channel
    peak_index=[]
    maxHeight=0
    for peak in peaks:
        peak=peak+startChannels
        peak_index.append(peak)
        max=counts[peak]
        for maximum in range(peak-5,peak+5):
            if counts[maximum]>=max:
                max=counts[maximum]
                peak=maximum
        if(counts[peak]>maxHeight):
            maxHeight=counts[peak]+50




    peaksWidth=signal.peak_widths(counts,peak_index)

    plt.plot(channels,counts)
    plt.plot(channels[peak_index],counts[peak_index],"x")
    #This gives approximately the FWHM of peak
    peaksWidth_half=signal.peak_widths(counts,peak_index,rel_height=0.5)
    halfWidth=(peaksWidth_half[0])
    #The relation between width of 1/20 of Gaussian FWTM and Gaussian FWHM: FWTM/FWHM≈2.
    #Also we add constant 5 for width to make background approximation better for Gaussian fit.
    Width=2*halfWidth+5

    if(output=="Y"):
        plt.hlines(*peaksWidth_half[1:], color="C2")
        plt.axis([startChannels*(channels[1]-channels[0]),stopChannels*(channels[1]-channels[0]),0,maxHeight])
        plt.savefig(outputPath+'Plot_Peaks_'+inputFile+'_Spectrum.png')
        for i in range(1,5,1):
            plt.axis([(startChannels+int(i-1)*(stopChannels-startChannels)/5)*(channels[1]-channels[0]),(startChannels+int((i)*(stopChannels-startChannels)/5))*(channels[1]-channels[0]),0,maxHeight])
            plt.savefig(outputPath+'Plot_Peaks_'+inputFile+str(i)+'.png')
        plt.cla()

    return peak_index,Width,prominence
