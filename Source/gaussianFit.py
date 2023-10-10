# -*- coding: utf-8 -*-
#Author:Jan Saren, modified by Joonas Ojala
# This code will fit Gaussian function to energy spectrum peak

import numpy as np
import scipy
from scipy.optimize import curve_fit
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import os

#gaussFit for Gaussian on the linear function. This function will be used in curvefit
# par[0]=height
# par[1]=position
# par[2]=deviation
# par[3]=constant
# par[4]=linear term
def gaussFit( x, *par ):
    return par[0]*np.exp( -(x-par[1])**2/(2*par[2]**2) )*0.5*(1+scipy.special.erf(par[3]*((x-par[1])/par[2]))) + par[4] + par[5]*(x)
#Fitting the background for estimate. Fit is first order polynomy
def firstDegree(x,*p):
    return p[1]+p[0]*(x)
#So that on can loop float number same way as range()
def frange(start, stop, step):
    i = start
    while i < stop:
        yield i
        i += step
#Fittig gaussFit in loop with different skewnes parameter alpha and width. The parameters of fit with the smallest reduced Chi^2 values are picked.
def fitGaussianInLoop(channels,counts,p0,counts_err,inputFile,outputPath):
        best_chi2=-1
        try:

            p=p0
            ptest, pcovtest = curve_fit( gaussFit, channels, counts, p0, sigma=counts_err, absolute_sigma=False )
            residuals = ( gaussFit( channels, *ptest ) - counts ) / counts_err

            ptest[0]=-ptest[0]
            ptest[4]=-ptest[4]
            ptest[5]=-ptest[5]
            maxGauss = scipy.optimize.fmin( gaussFit, ptest[1],args=(ptest[0],ptest[1],ptest[2],ptest[3],ptest[4],ptest[5]),disp=False,full_output=False)
            ptest[0]=-ptest[0]
            ptest[4]=-ptest[4]
            ptest[5]=-ptest[5]
            if(maxGauss>0 and maxGauss<10000):
                positionPeak=maxGauss
            else:
                positionPeak=-1

            chi2 = np.sum( residuals**2 )
            dof  = channels.size - 5
            p=ptest

            pcov=pcovtest
        except RuntimeError:
            peak=p[1]
            f= open(outputPath+'GaussianFit_'+inputFile+"{}Errors.txt".format(peak),"w+")
            f.write( "Error position:    = ("+ str(p)+")" )
            f.close()
            p=p0
            positionPeak=0
            pcov=np.array([[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]])

        return p,pcov,positionPeak
# The fitting function which takes data and peak positions and width of the peak. Also take out the information that does the user want to save the figures from fits.
def gaussianFitOnData(channels_orig,counts_orig,peak,width,inputFile,outputPath,output):
    outputPath=outputPath+'/GaussianFit/'
    #Create folder for the figures of fits
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
    # Choose data so that channel position is the in middle of bin

    counts_err_orig=np.sqrt(counts_orig)
    min=int(peak-width/2-6)
    if(min<0):
        min=0
    max=int(peak+width/2+6)
    slope=(-counts_orig[max]-counts_orig[min])/(max-min)
    constant=counts_orig[min]-slope*min
    a=[constant,slope,0]
    counts = counts_orig[min:max]
    counts_err = counts_err_orig[min:max]
    channels = channels_orig[min:max] + 0.5*(channels_orig[1]-channels_orig[0])
    countsBackground= counts_orig[min:min+5]
    countsBackground= np.append(countsBackground,counts_orig[max-5:max])
    channelsBackground=channels_orig[min:min+5]
    channelsBackground=np.append(channelsBackground,channels_orig[max-5:max])

    a=np.polyfit( channelsBackground,countsBackground,1 )
    constant=a.item(1)
    slope=a.item(0)
    x_fit = np.linspace( channels[0], channels[-1], channels.size*10 )
    y_fit = firstDegree( x_fit,*a )
    y_fit_data = firstDegree( channels, *a)



    fig = Figure( figsize=(20,20) )
    canvas = FigureCanvas(fig)
    ax  = fig.add_subplot(4,1,1)

    ax.set_xlabel('x')
    ax.set_ylabel('N')
    ax.errorbar( channels, counts, counts_err, fmt='o' )
    ax.errorbar( channelsBackground, countsBackground,yerr=0, fmt='o' )
    ax.plot( x_fit, y_fit, 'r-' )


    ax  = fig.add_subplot(4,1,2)
    ax.set_xlabel('x')
    ax.set_ylabel('(model-y)/sqrt(y)')
    ax.errorbar( channels, (y_fit_data-counts)/counts_err, 1, fmt='o' )



    # Initial quesses and fitting
    p0 = [counts_orig[peak]*2, peak*(channels_orig[1]-channels_orig[0]), (width-5)*(1/(2.333*2)),0, a[1], a[0]]

    p,pcov,peakPostion=fitGaussianInLoop(channels,counts,p0,counts_err,inputFile,outputPath)
    count_err=np.sqrt(gaussFit(channels,*p))
    p,pcov,peakPostion=fitGaussianInLoop(channels,counts,p0,counts_err,inputFile,outputPath)


    residuals = ( gaussFit( channels, *p ) - counts ) / counts_err
    chi2 = np.sum( residuals**2 )
    dof  = channels.size - 5
    if(output=='Y'):
        f= open(outputPath+'GaussianFit_'+inputFile+"{}.txt".format(peak),"w+")
        f.write( 'norm_chi2    = {:g}\r\n'.format( chi2 ) )
        f.write( 'dof          = {:d}\r\n'.format( dof ) )
        f.write( 'normchi2/dof = {:g}\r\n'.format( chi2/dof ) )
        f.write("Initial parameters\r\n")
        f.write( "A     = {:g}\r\n".format( counts_orig[peak] ))
        f.write( "x0    = {:g}\r\n".format( peak ))
        f.write( "sigma = {:g}\r\n".format((width-5)*(1/(2.3332*2)) ))
        f.write( "bgrA  = {:g}\r\n".format( slope))
        f.write( "bgrB  = {:g}\r\n".format( constant ))
        f.write("Fit parameters\r\n")
        f.write( "A     = {:g} +-{:g}\r\n".format( p[0], np.sqrt(pcov[0,0]) ) )
        f.write( "x0    = {:g} +-{:g}\r\n".format( p[1], np.sqrt(pcov[1,1]) ) )
        f.write( "sigma = {:g} +-{:g}\r\n".format( p[2], np.sqrt(pcov[2,2]) ) )
        f.write( "bgrA  = {:g} +-{:g}\r\n".format( p[3], np.sqrt(pcov[3,3]) ) )
        f.write( "bgrB  = {:g} +-{:g}\r\n".format( p[4], np.sqrt(pcov[4,4]) ) )
        f.close()

    # Using the function from fit and produce the figure of it
    x_fit = np.linspace( channels[0], channels[-1], channels.size*10 )
    y_fit = gaussFit( x_fit, *p )
    y_fit_data = gaussFit( channels, *p )

    ax  = fig.add_subplot(4,1,3)

    ax.set_xlabel('x')
    ax.set_ylabel('N')
    ax.errorbar( channels, counts, counts_err, fmt='o' )
    ax.plot( x_fit, y_fit, 'r-' )

    ax  = fig.add_subplot(4,1,4)
    ax.set_xlabel('x')
    ax.set_ylabel('(model-y)/sqrt(y)')
    ax.errorbar( channels, (y_fit_data-counts)/counts_err, 1, fmt='o' )

    fig.savefig( outputPath+'GaussianFit_'+inputFile+'{}.png'.format(peak) )
    return peakPostion
