import numpy as np
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# First order linear fit function
def firstDegree(x,*p):
    return p[1]+p[0]*(x)
# Second order linear fit function
def secondDegree(x,*p):
    return p[2]+p[1]*(x)+p[0]*(x**2)
#Program itself which does fitting, producing the figures of fit and fits residuals. The output will be the Grain gain file although the daq channel number will be as the name of the input file
def energyCalibrations(channels,energies,fileName,outputPath,preference):
    outputPath=outputPath+'/Energy_Calibration/'
    #Create folder for the figures of fit
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)

    if(len(channels)==0 or len(energies)==0):
        f= open(outputPath+'EnergyCalibration.txt',"a+")
        firstOrder=""
        secondOrder="#"
        if(preference==1):
            firstOrder="#"
            secondOrder=""
        f.write(fileName+".Offset:"+"0"+"\r\n")
        f.write(fileName+".Gain:"+"0"+"\r\n")
        f.write(firstOrder+fileName+".Type: Qint"+"\r\n")
        #f.write(firstOrder+str(fileName)+" = "+"-1"+" "+"0"+" "+"0"+" "+"0"+" #disabled\r\n")
        #f.write(secondOrder+str(fileName)+" = "+"-1"+" "+"0"+" "+"0"+" "+"0"+" #disabled\r\n")
        f.close()
        return
    polynom1=np.polyfit(channels,energies,1)
    polynom2=np.polyfit(channels,energies,2)

    slope1=str(polynom1.item(0))
    constant1=str(polynom1.item(1))
    secondO2=str(polynom2.item(0))
    slope2=str(polynom2.item(1))
    constant2=str(polynom2.item(2))
    slope1=slope1.replace('e','E')
    slope2=slope2.replace('e','E')
    secondO2=secondO2.replace('e','E')
    constant1=constant1.replace('e','E')
    constant2=constant2.replace('e','E')
    f= open(outputPath+'EnergyCalibration.txt',"a+")
    firstOrder=""
    secondOrder="#"
    if(preference==1):
        firstOrder=""
        secondOrder="#"
    f.write(firstOrder+fileName+".Offset: "+constant1+"\r\n")
    f.write(firstOrder+fileName+".Gain: "+slope1+"\r\n")
    f.write(firstOrder+fileName+".GainQuadr: "+"0"+"\r\n")
    f.write(firstOrder+fileName+".Type: Qint"+"\r\n")
    f.write(secondOrder+fileName+".Offset: "+constant1+"\r\n")
    f.write(secondOrder+fileName+".Gain: "+slope1+"\r\n")
    f.write(secondOrder+fileName+".GainQuadr: "+secondO2+"\r\n")
    #f.write(firstOrder+str(fileName)+" = "+constant1+" "+slope1+" "+"0"+" "+"0\r\n")
    #f.write(secondOrder+str(fileName)+" = "+constant2+" "+slope2+" "+secondO2+" "+"0\r\n")
    f.close()


    x_fit = np.linspace( channels[0], channels[-1], channels.size*10 )
    p1=[polynom1.item(0),polynom1.item(1)]
    y_fit1 = firstDegree( x_fit, *p1 )
    y_fit1_data=firstDegree( channels, *p1 )
    p2=[polynom2.item(0),polynom2.item(1),polynom2.item(2)]
    y_fit2 = secondDegree( x_fit, *p2 )
    y_fit2_data=secondDegree( channels, *p2 )


    fig = Figure( figsize=(20,20) )
    canvas = FigureCanvas(fig)
    ax  = fig.add_subplot(4,1,1)
    ax.set_xlabel('Channel')
    ax.set_ylabel('Energy')
    ax.plot( channels, energies, 'o' )
    ax.plot( x_fit, y_fit1, 'r-' )

    ax  = fig.add_subplot(4,1,2)
    ax.set_xlabel('Channel')
    ax.set_ylabel('Residual')
    ax.plot( channels, (y_fit1_data-energies), 'b-' )

    ax  = fig.add_subplot(4,1,3)
    ax.set_xlabel('Channel')
    ax.set_ylabel('Energy')
    ax.plot( channels, energies, 'o' )
    ax.plot( x_fit, y_fit2, 'r-' )

    ax  = fig.add_subplot(4,1,4)
    ax.set_xlabel('Channel')
    ax.set_ylabel('Residual')
    ax.plot( channels, (y_fit2_data-energies), 'b-' )


    #ax.legend( loc="lower right" )

    fig.savefig( outputPath+'Energycalibration'+fileName+'.png' )
