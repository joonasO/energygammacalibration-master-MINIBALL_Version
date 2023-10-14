from pathlib import Path
def readInputFiles(inputFile,fileNumber,lengthInputFileList):
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
    return channels,counts
