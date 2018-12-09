import tkinter as tk
from tkinter import Message ,Text
import cv2,os
import shutil
import csv
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import datetime
import time
import tkinter.ttk as ttk
import tkinter.font as font


root = tk.Tk()

canv = tk.Canvas(root, width=1080, height=1080, bg='white')
canv.grid(row=2, column=3)
root.attributes('-fullscreen', False)
image="bg2.jpg"
img = ImageTk.PhotoImage(Image.open(image))  # PIL solution
canv.create_image(20, 20, anchor='nw', image=img)

lbl = tk.Label(root, text="ROLL NO",width=15  ,height=1  ,fg="WHITE"  ,bg="BLUE" ,font=('times', 15, ' bold ') ,relief="raise",bd=8)
lbl.place(x=200, y=225)
txt = tk.Entry(root,width=20,bg="WHITE" ,fg="GREEN",font=('times', 15, ' bold '),relief="ridge",bd=5)
txt.place(x=500, y=230)

lbl2 = tk.Label(root, text="ENTER NAME",width=15  ,fg="WHITE"  ,bg="BLUE"    ,height=1 ,font=('times', 15, ' bold '),relief="raise",bd=8) 
lbl2.place(x=200, y=325)
txt2 = tk.Entry(root,width=20  ,bg="white"  ,fg="green",font=('times', 15, ' bold '),relief="ridge",bd=5)
txt2.place(x=500, y=330)

lbl3 = tk.Label(root, text="Notification",width=15  ,fg="black"  ,bg="red"  ,height=2 ,font=('times', 15, ' bold '),relief="raise",bd=8) 
lbl3.place(x=200, y=400)
message = tk.Label(root, text="" ,bg="white"  ,fg="red"  ,width=40  ,height=2, activebackground = "yellow" ,font=('times', 15, ' bold '),relief="sunken",bd=8) 
message.place(x=500, y=400)

lbl3 = tk.Label(root, text="Attendance",width=15  ,fg="black"  ,bg="green"  ,height=2 ,font=('times', 15, ' bold '),relief="raise",bd=8) 
lbl3.place(x=200, y=610)
message2 = tk.Label(root, text="" ,fg="red"   ,bg="white",activeforeground = "yellow",width=35  ,height=2  ,font=('times', 15, ' bold '),relief="sunken",bd=8)
message2.place(x=500, y=610)




 
def clear():
    txt.delete(0, 'end')    
    res = ""
    message.configure(text= res)

def clear2():
    txt2.delete(0, 'end')    
    res = ""
    message.configure(text= res)    
    
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False
 
def TakeImages():        
    Id=(txt.get())
    name=(txt2.get())
    if(is_number(Id) and name.isalpha()):
        cam = cv2.VideoCapture(0)
        harcascadePath = "haarcascade_frontalface_default.xml"
        detector=cv2.CascadeClassifier(harcascadePath)
        sampleNum=0
        while(True):
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)        
                #incrementing sample number 
                sampleNum=sampleNum+1
                #saving the captured face in the dataset folder TrainingImage
                cv2.imwrite("TrainingImage\ "+name +"."+Id +'.'+ str(sampleNum) + ".jpg", gray[y:y+h,x:x+w])
                #display the frame
                cv2.imshow('frame',img)
            #wait for 100 miliseconds 
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            # break if the sample number is morethan 100
            elif sampleNum>100:
                break
        cam.release()
        cv2.destroyAllWindows() 
        res = "Images Saved for ID : " + Id +" Name : "+ name
        row = [Id , name]
        with open('StudentDetails\StudentDetails.csv','a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        csvFile.close()
        message.configure(text= res)
    else:
        if(is_number(Id)):
            res = "Enter Alphabetical Name"
            message.configure(text= res)
        if(name.isalpha()):
            res = "Enter Numeric Id"
            message.configure(text= res)
    
def TrainImages():
    recognizer = cv2.face_LBPHFaceRecognizer.create()
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector =cv2.CascadeClassifier(harcascadePath)
    faces,Id = getImagesAndLabels("TrainingImage")
    recognizer.train(faces, np.array(Id))
    recognizer.save("TrainingImageLabel\Trainner.yml")
    res = "Image Trained"#+",".join(str(f) for f in Id)
    message.configure(text= res)

def getImagesAndLabels(path):
    #get the path of all the files in the folder
    imagePaths=[os.path.join(path,f) for f in os.listdir(path)] 
    #print(imagePaths)
    
    #create empty face list
    faces=[]
    #create empty ID list
    Ids=[]
    #now looping through all the image paths and loading the Ids and the images
    for imagePath in imagePaths:
        #loading the image and converting it to gray scale
        pilImage=Image.open(imagePath).convert('L')
        #Now we are converting the PIL image into numpy array
        imageNp=np.array(pilImage,'uint8')
        #getting the Id from the image
        Id=int(os.path.split(imagePath)[-1].split(".")[1])
        # extract the face from the training image sample
        faces.append(imageNp)
        Ids.append(Id)        
    return faces,Ids

def TrackImages():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("TrainingImageLabel\Trainner.yml")
    harcascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath);    
    df=pd.read_csv("StudentDetails\StudentDetails.csv")
    cam = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX        
    col_names =  ['Id','Name','Date','Time']
    attendance = pd.DataFrame(columns = col_names)    
    while True:
        ret, im =cam.read()
        gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
        faces=faceCascade.detectMultiScale(gray, 1.2,5)    
        for(x,y,w,h) in faces:
            cv2.rectangle(im,(x,y),(x+w,y+h),(225,0,0),2)
            Id, conf = recognizer.predict(gray[y:y+h,x:x+w])                                   
            if(conf < 50):
                ts = time.time()      
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                aa=df.loc[df['Id'] == Id]['Name'].values
                tt=str(Id)+"-"+aa
                attendance.loc[len(attendance)] = [Id,aa,date,timeStamp]
                
            else:
                Id='Unknown'                
                tt=str(Id)  
            if(conf > 75):
                noOfFile=len(os.listdir("ImagesUnknown"))+1
                cv2.imwrite("ImagesUnknown\Image"+str(noOfFile) + ".jpg", im[y:y+h,x:x+w])            
            cv2.putText(im,str(tt),(x,y+h), font, 1,(255,255,255),2)        
        attendance=attendance.drop_duplicates(subset=['Id'],keep='first')    
        cv2.imshow('im',im) 
        if (cv2.waitKey(1)==ord('q')):
            break
    ts = time.time()      
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    Hour,Minute,Second=timeStamp.split(":")
    fileName="Attendance\Attendance_"+date+"_"+Hour+"-"+Minute+"-"+Second+".csv"
    attendance.to_csv(fileName,index=False)
    cam.release()
    cv2.destroyAllWindows()
    #print(attendance)
    res=attendance
    message2.configure(text= res)

  
clearButton = tk.Button(root, text="Clear", command=clear  ,fg="red"  ,bg="silver"  ,width=10  ,height=1 ,activebackground = "Red" ,font=('times', 15, ' bold '))
clearButton.place(x=850, y=230)
clearButton2 = tk.Button(root, text="Clear", command=clear2  ,fg="red"  ,bg="silver"  ,width=10  ,height=1, activebackground = "Red" ,font=('times', 15, ' bold '))
clearButton2.place(x=850, y=330)    
takeImg = tk.Button(root, text="Take Images", command=TakeImages  ,fg="white"  ,bg="black"  ,width=15  ,height=1, activebackground = "green" ,font=('times', 15, ' bold '))
takeImg.place(x=200, y=500)
trainImg = tk.Button(root, text="Train Images", command=TrainImages  ,fg="white"  ,bg="black"  ,width=12  ,height=1, activebackground = "green" ,font=('times', 15, ' bold '))
trainImg.place(x=420, y=500)
trackImg = tk.Button(root, text="Track Images", command=TrackImages  ,fg="white"  ,bg="black"  ,width=15  ,height=1, activebackground = "green" ,font=('times', 15, ' bold '))
trackImg.place(x=650, y=500)
quitWindow = tk.Button(root, text="Quit", command=root.destroy  ,fg="black"  ,bg="red"  ,width=13  ,height=1, activebackground = "Red" ,font=('times', 15, ' bold '))
quitWindow.place(x=890, y=500)

 
root.mainloop()



