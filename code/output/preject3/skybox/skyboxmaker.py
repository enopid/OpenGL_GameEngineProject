from PIL import Image
import os

def seperateimage(filename,foldername=None):
    filenames=["right","left","top","bottom","front","back"]
    offset=[(1,2),(1,0),(0,1),(2,1),(1,1),(1,3)]

    image = Image.open(filename)
    w,h=image.size
    if foldername==None:
        foldername=filename.split("/")[-1].split(".")[0]
    os.mkdir("./"+foldername)

    for i in range(6):
        cropped_image = image.crop((offset[i][1]*w/4, offset[i][0]*w/4, offset[i][1]*w/4+w/4, offset[i][0]*w/4+w/4)) 
        
        filename="./"+foldername+"/"+filenames[i]+".png"
        cropped_image.save(filename)

def filenamechanger(foldername):
    filelist=os.listdir(foldername)
    for temp in filelist:
        filename=temp.split(".")[0]
        extension=temp.split(".")[-1]
        if filename=="posx":
            filename="right"
        elif filename=="negx":
            filename="left"
        elif filename=="posy":
            filename="top"
        elif filename=="negy":
            filename="bottom"
        elif filename=="posz":
            filename="front"
        elif filename=="negz":
            filename="back"

        os.rename("./"+foldername+"/"+temp, "./"+foldername+"/"+filename+"."+extension)

#filenamechanger("hotel")
#seperateimage("space.jpg")