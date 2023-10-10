import sys

def readOutput():
    with open("outputPath.txt","r") as f:
        outputPath=f.readline()
        outputPath=str(outputPath)
    return outputPath
