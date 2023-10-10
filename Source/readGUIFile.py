import sys

def readGUIFiles():
    with open("file.txt","r") as f:
        inputs=[]
        input=f.readlines()
        for line in input:
            inputs.append(line)
    return inputs
