import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

import urllib
import json

import pandas as pd
import numpy as np

import os
import guiCommand
import readSettings
LARGE_FONT= ("Verdana", 12)
style.use("ggplot")







class energyProgramGUI(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "Energy Calibration program")


        container = tk.Frame(self,bg='blue')
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, readInputFiles, calibrationFile, settings):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent,bg='mint cream')
        if os.path.isfile("noGaussian.tmp"):
            os.remove("noGaussian.tmp")

        label = tk.Label(self, text="JuroCalib", font=("Helvetica",32),bg='mint cream')
        label.pack(pady=50,padx=50)
        buttonInput = tk.Button(self, text="Input",
                            command=lambda: controller.show_frame(readInputFiles))
        buttonInput.pack()

        buttonCalibrationFile=tk.Button(self,text="Calibration file",
                                    command=lambda: controller.show_frame(calibrationFile))
        buttonCalibrationFile.pack()


        buttonSettings = tk.Button(self, text="Settings",
                            command=lambda: controller.show_frame(settings))
        buttonSettings.pack()
        buttonStart = tk.Button(self, text="Start",
                            command=self.startCalibration)
        buttonStart.pack()


        buttonQuit = tk.Button(self, text="Quit",
                            command=quit)
        buttonQuit.pack()
        label = tk.Label(self, text="Author: Joonas Ojala \n Special thanks: Minna Luoma, Jan Sarén, George Zimba, Holly Tann", font=("Helvetica",8),bg='mint cream')
        label.pack(side='bottom')

    def startCalibration(self):
        if(not(os.path.isfile("file.txt"))):
            messagebox.showinfo(message='Choose first the input spectra for energy calibration program',icon='error',title='Missing Input')
        if(not(os.path.isfile("calibration.txt"))):
            messagebox.showinfo(message='Choose first the calibration file for the energy calibration program',icon='error',title='Missing Calibration')
        if(not(os.path.isfile("outputPath.txt"))):
            messagebox.showinfo(message='Choose first the calibration file for the energy calibration program',icon='error',title='Missing Calibration')
        if(not(os.path.isfile("settings.txt"))):
            file = open("Settings.txt","w+")
            writeSettings=[]
            writeSettings.append("Channel range (min, max):0,16384"+"\n")
            writeSettings.append("Amount of the extra peaks for calibration (min, max):0,15"+"\n")
            writeSettings.append("Peak width(in units of channels):100"+"\n")
            ##print("hep")
            for line in writeSettings:
                file.write(line)
            file.close()


        guiCommand.guiCommand()





#Creating readInputFiles class which takes the spectrum files paths and save them to file.txt.
class readInputFiles(tk.Frame):


    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent,bg='mint cream')
        label = tk.Label(self, text="Select input files and output folder!", font=("Helvetica",20))
        label.grid(row=0,column=1)
        buttonInput = tk.Button(self, text="Input",
                            command=self.chooseFile)
        buttonInput.grid(row=1,column=1)

        buttonRemove = tk.Button(self, text="Remove",
                            command=self.remove)
        buttonRemove.grid(row=2,column=1)

        buttonRemoveAll = tk.Button(self, text="RemoveAll",
                            command=self.removeAll)
        buttonRemoveAll.grid(row=3,column=1)

        buttonOutputFile=tk.Button(self, text="Choose output folder",
                            command=self.outputPath)
        buttonOutputFile.grid(row=4,column=1)

        buttonReadFile = tk.Button(self, text="Read input from file",
                            command=self.readFile)
        buttonReadFile.grid(row=5,column=1)

        buttonSaveFile = tk.Button(self, text="Save inputs as file",
                            command=self.saveFile)
        buttonSaveFile.grid(row=6,column=1)



        buttonBack = tk.Button(self, text="Back",
                            command=lambda: controller.show_frame(StartPage))
        buttonBack.grid(row=7,column=1)



        scrollframe=tk.Frame(self,bd=1,relief='sunken')
        scrollbar=tk.Scrollbar(self)
        self.listbox = tk.Listbox(self,selectmode='multiple')
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        if os.path.isfile("file.txt"):
            i=0
            with open("file.txt","r") as f:
                for file in f:
                    self.listbox.insert(i,file)
                    i=i+1
                    ##print(i)



        scrollframe.grid(row=1,column=2,rowspan=6)
        scrollbar.grid(row=1,column=2,rowspan=6)
        self.listbox.grid(row=1,column=2,rowspan=6)
        self.textbox = tk.Text(self,width=30,height=10,bg='mint cream')
        self.textbox.grid(row=7,column=2,rowspan=2)





    #choose file by picking them from folders and write those files on listbox and file.txt. Notce that askopenfilenames don't know the picking order. It took order how files are placed on folder
    def chooseFile(self):
        myPath=os.path.dirname(os.path.abspath("__file__"))
        myPath=str(myPath)
        myPath=myPath.replace("Source","")
        files= filedialog.askopenfilenames( initialdir= myPath+"Input/", title='Please select a directory')
        if os.path.isfile("file.txt"):
            file = open("file.txt","r")
            numberOfFiles=file.readlines()
            file.close()
            i=len(numberOfFiles)
        else:
            i=0
        file = open("file.txt","a+")
        for x in files:
            x=str(x)+"\n"
            file.write(x)
            self.listbox.insert(i,x)
            i=i+1
        file.close()

    #Remove the file from file.txt and listbox so that indexing is correct
    def remove(self):
        current_selections=self.listbox.curselection()
        files= open("file.txt","r")
        fileList=files.readlines()
        files.close()
        correctIndex=0
        for i in current_selections:
            self.listbox.delete(i-correctIndex)
            fileList[i:i+1]='0'
            correctIndex=correctIndex+1
        newFileList=[]
        for i in fileList:
            if i!='0':
                newFileList.append(i)
        if os.path.isfile("file.txt"):
            os.remove("file.txt")
        fileNew=open("file.txt","a+")
        fileNew.writelines(newFileList)
        fileNew.close()

    def removeAll(self):
        current_selections=self.listbox.delete(0,tk.END)
        if os.path.isfile("file.txt"):
            os.remove("file.txt")
        fileNew=open("file.txt","a+")
        fileNew.close()

    def readFile(self):
        myPath=os.path.dirname(os.path.abspath("__file__"))
        myPath=str(myPath)
        myPath=myPath.replace("Source","")
        inputFiles= filedialog.askopenfilename( initialdir= myPath+"Input/", title='Please select a directory')
        i=0
        files = open(inputFiles,"r")
        fileList=files.readlines()
        files.close()
        file=open("file.txt","a+")
        for f in fileList:
            f=str(f)
            file.write(f)
            self.listbox.insert(i,f)
            i=i+1

    def saveFile(self):
        f = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
        if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        files= open("file.txt","r")
        fileList=files.readlines()
        files.close()
        for x in fileList:
             x=str(x)
             f.write(x) # starts from `1.0`, not `0.0`

        f.close() # `()` was
    def outputPath(self):
        myPath=os.path.dirname(os.path.abspath("__file__"))
        #print(myPath)
        #print("path")
        myPath=str(myPath)
        myPath=myPath.replace("Source","")
        folder= filedialog.askdirectory( initialdir= myPath+"Output/", title='Please select a directory')
        file = open("outputPath.txt","w")
        x=str(folder)
        file.write(x)
        file.close()
        self.textbox.delete(1.0,tk.END)
        self.textbox.insert(tk.INSERT,"Output folder: "+x)




class calibrationFile(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent,bg='mint cream')
        self.var=tk.IntVar()
        label = tk.Label(self, text="Choose the calibration source", font=("Helvetica",20),bg='mint cream')
        label.pack(pady=10,padx=10)
        buttonEuba=tk.Radiobutton(self,text="EuBa-source",variable=self.var,value=1,command=self.euBaCalib)
        buttonEuba.pack()
        buttonOther=tk.Radiobutton(self,text="other source",variable=self.var,value=2,command=self.otherCalib)
        buttonOther.pack()
        buttonBack = tk.Button(self, text="Back",
                            command=lambda: controller.show_frame(StartPage))
        buttonBack.pack()
        self.textbox = tk.Text(self,width=30,height=10,bg='mint cream')
        self.textbox.pack()

#Read predefined Euba energy calibration file
    def euBaCalib(self):
        if os.path.isfile("calibration.txt"):
            os.remove("calibration.txt")
        myPath=os.path.dirname(os.path.abspath("__file__"))
        #print(myPath)
        #print("path")
        myPath=str(myPath)
        myPath=myPath.replace("Source","")
        path=myPath+"CalibrationFiles/EuBa.txt"
        #print(path)
        euBaCalibPath=open(path,"r")
        euBaEnergies=euBaCalibPath.readlines()
        euBaCalibPath.close()
        calibrationFile=open("calibration.txt","a")
        for energy in euBaEnergies:
            energy=str(energy)
            calibrationFile.write(energy)
        calibrationFile.close()
        self.textbox.delete(1.0,tk.END)
        self.textbox.insert(tk.INSERT,"Eu-Ba source is now chosen to be as energy calibration file")

    def otherCalib(self):
        if os.path.isfile("calibration.txt"):
            os.remove("calibration.txt")
        myPath=os.path.dirname(os.path.abspath("__file__"))
        #print(myPath)
        #print("path")
        myPath=str(myPath)
        myPath=myPath.replace("Source","")
        path=myPath+"Input/"
        #print(path)
        calibFilePath= filedialog.askopenfilename( initialdir= myPath+"CalibrationFiles/", title='Please select a directory')
        calibFile=open(calibFilePath,"r")
        calibEnergies=calibFile.readlines()
        calibrationFile=open("calibration.txt", "a")
        for energy in calibEnergies:
            energy=str(energy)
            calibrationFile.write(energy)
        calibrationFile.close()
        self.textbox.delete(1.0,tk.END)
        self.textbox.insert(tk.INSERT,"Path"+calibFilePath+"is now chosen to be as energy calibration file")


class settings(tk.Frame):



    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent,bg='mint cream')
        self.var=tk.IntVar()

        label1=tk.Label(self, text="Channel range (min, max)")
        label2=tk.Label(self, text="Amount of the extra peaks for calibration (min, max)")
        label3=tk.Label(self, text="Peaks search window width (in units of channels)")
        label1.grid(row=0,column=0)
        label2.grid(row=1,column=0)
        label3.grid(row=2,column=0)

        minRange,maxRange,minPeaks,maxPeaks,peakWidth,gaussianFit=self.readSettings()
        self.e11 = tk.Entry(self)
        self.e12 = tk.Entry(self)
        self.e21 = tk.Entry(self)
        self.e22 = tk.Entry(self)
        self.e3 = tk.Entry(self)
        self.e11.insert(10,minRange)
        self.e12.insert(10,maxRange)
        self.e21.insert(10,minPeaks)
        self.e22.insert(10,maxPeaks)
        self.e3.insert(10,peakWidth)
        self.e11.grid(row=0,column=1)
        self.e12.grid(row=0,column=2)
        self.e21.grid(row=1,column=1)
        self.e22.grid(row=1,column=2)
        self.e3.grid(row=2,column=1)
        labelRadioButton=tk.Label(self, text="Do you want to use Gaussian fit")
        labelRadioButton.grid(row=4,column=1)
        radioYesButton=tk.Radiobutton(self,text="Yes",variable=self.var,value=1,command=self.yesGaussian)
        radioNoButton=tk.Radiobutton(self,text="No",variable=self.var,value=2,command=self.noGaussian)
        radioYesButton.grid(row=5,column=1)
        radioNoButton.grid(row=5,column=2)

        buttonSave =tk.Button(self, text='Save', command=self.saveSettings)
        buttonSave.grid(row=7,column=1)
        buttonCancel = tk.Button(self, text="Back",
                            command=lambda: [self.yesGaussian,controller.show_frame(StartPage)])
        buttonCancel.grid(row=7,column=2)
        self.textbox = tk.Text(self,width=30,height=10,bg='mint cream')
        self.textbox.grid(row=8,column=1)


    def isFloat(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def noGaussian(self):
        file = open("noGaussian.tmp","w+")
        file.write("+ ")
        file.close()
    def yesGaussian(self):
        if os.path.isfile("noGaussian.tmp"):
            os.remove("noGaussian.tmp")


    def readSettings(self):
        myPath=os.path.dirname(os.path.abspath("__file__"))
        myPath=str(myPath)
        if os.path.isfile("Settings.txt"):
            minRange,maxRange,minPeaks,maxPeaks,peakWidth,gaussianFit=readSettings.readSettings()
            return minRange,maxRange,minPeaks,maxPeaks,peakWidth,gaussianFit

        else:
            return "min","max","min","max","width"

    def saveSettings(self):
        file = open("Settings.txt","w+")
        writeSettings=[]
        #print("TAAhep")
        e11=self.e11.get()
        e12=self.e12.get()
        e21=self.e21.get()
        e22=self.e22.get()
        e3=self.e3.get()
        gaussianFit="1"
        if(self.isFloat(e11) and self.isFloat(e12) and self.isFloat(e21) and self.isFloat(e22) and self.isFloat(e3) and float(e11)>=0 and float(e21)>=0 and float(e11)<float(e12) and float(e21)<float(e22)):
            writeSettings.append("Channel range (min, max):"+e11+","+e12+"\n")
            writeSettings.append("Amount of the extra peaks for calibration (min, max):"+e21+","+e22+"\n")
            writeSettings.append("Peak width(in units of channels):"+e3+"\n")
            if os.path.isfile("noGaussian.tmp"):
                gaussianFit="0"
                os.remove("noGaussian.tmp")
            writeSettings.append("Gaussian fit:"+gaussianFit+"\n")
            #print("hep")
            for line in writeSettings:
                file.write(line)
                #print("hep")
            file.close()
            self.textbox.delete(1.0,tk.END)
            self.textbox.insert(tk.INSERT,"Settings are now saved!")


        else:
            messagebox.showinfo(message='Use only numbers and check that 0<=min<max',icon='error',title='Settings')



#Just checking that is there a file.txt file.
if os.path.isfile("file.txt"):
    os.remove("file.txt")
if os.path.isfile("outputPath.txt"):
    os.remove("outputPath.txt")
app = energyProgramGUI()
app.mainloop()
