from flask import render_template,request
from flask import redirect, url_for, flash
import os
from PIL import Image
import cv2
import os

from app.utils import pipeline_model, pipeline_model1

UPLOAD_FOLDER = "static/uploads"


def base():
    
    return render_template('base.html')
    
def index():
    return render_template('index.html')

def faceapp():
    return render_template('faceapp.html')

def getwidth(path):
    img= Image.open(path)
    size= img.size
    aspect= size[0]/size[1] # width/ height
    w = 300 *aspect
    return int(w)

def gender(): 
    filelist = [ f for f in os.listdir("static/uploads/")  ]
    for f in filelist:
        os.remove(os.path.join("static/uploads/", f))
        
        
    filelist1 = [ f for f in os.listdir("static/predict/")  ]
    for f in filelist1:
        os.remove(os.path.join("static/predict/", f))
    
        
    avgMale=[]
    avgFemale=[]
    if request.method == "POST":
        f = request.files['image']
        filename=  f.filename
        extension= filename.split('.')[1]
        if extension == 'jpg':  
            path = os.path.join(UPLOAD_FOLDER,filename)
            f.save(path)
            w = getwidth(path)
            # prediction (pass to pipeline model)
            pipeline_model(path,filename,color='bgr')
            return render_template('gender.html',fileupload=True,img_name=filename,extension=extension,  w=w)
        
        elif extension=='mp4':
            
            path = os.path.join(UPLOAD_FOLDER,filename)
            f.save(path)
            
            video = cv2.VideoCapture(path)
            width= int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            flash(width)
            height= int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            size = (width, height)
            fps = int(video.get(cv2.CAP_PROP_FPS))
            filename=filename.split('.')[0]
            #fourcc = cv2.VideoWriter_fourcc(*'H264')
            fourcc = cv2.VideoWriter_fourcc(*"vp80")
            #out = cv2.VideoWriter('Videos/output.mp4',fourcc, fps, (1080,1080))
            writer = cv2.VideoWriter( 'static/predict/'+ str(filename)+'.webm', 
                                    fourcc,
                                    fps, size)
            #writer = cv2.VideoWriter('C:/Digital Engineering/Gender Detection/Web_App/' + str(filename), cv2.VideoWriter_fourcc(*'VIDX'),25, (width, height))

                    # writer = cv2.VideoWriter('./static/uploads/' + str(filename) + '.avi', 
                    # 						cv2.VideoWriter_fourcc(*'MJPG'),
                    # 						20, size)
            
                    # writer = cv2.VideoWriter('./static/uploads/' + str(filename), cv2.VideoWriter_fourcc(*'MP4V'), fps , size)
                    # writer = cv2.VideoWriter('./static/uploads/' + str(filename), cv2.VideoWriter_fourcc(*'MPEG-4'), fps , size)
            
            #filename= os.path.join(app.config['UPLOAD_FOLDER'], filename)
            while True:
                ret,frame= video.read()
                if ret == True:
                    frame, score1, predict = pipeline_model1(frame,filename,color='bgr')
                    writer.write(frame)
                    if predict == 0:
                        avgMale.append(score1)
                    else:
                        avgFemale.append(score1)
                    
                else :
                    break
                
            video.release()
            writer.release()
            cntMale=0
            sumMale=0
            cntFemale=0
            sumFemale=0

            for i in avgMale:
                if i != None:
                    sumMale=sumMale+i
                    cntMale=cntMale+1
                    
            for i in avgFemale:
                if i != None:
                    sumFemale=sumFemale+i
                    cntFemale=cntFemale+1
                    
            if cntMale==0:
                averageMale=0
            else:
                
                averageMale=sumMale/cntMale
                averageMale=averageMale*100
                averageMale = str(round(averageMale, 2))
            
            
            if cntFemale==0:
                averageFemale=0
            else:
                averageFemale=sumFemale/cntFemale
                averageFemale=averageFemale*100
                averageFemale = str(round(averageFemale, 2))
            #flash(average)
            
            
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #print('upload_video filename: ' + filename)
    
            flash('Video successfully uploaded and displayed below')
            
            #filename='earth.webm'
            
            filename=filename+'.webm'
            flash(filename)
            return render_template('gender.html',fileupload=True,img_name=filename,extension=extension, averageMale=averageMale, averageFemale=averageFemale, cntMale=cntMale,cntFemale=cntFemale, )
        
        

    return render_template('gender.html', fileupload=False, img_name='freeai.png', width="300")


