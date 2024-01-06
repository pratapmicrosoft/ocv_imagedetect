

from flask import Flask, render_template, Response, request,flash, session
import cv2
import os
from flask_session import Session

app=Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config.update(SECRET_KEY=os.urandom(24))
Session(app)


#camera = cv2.VideoCapture(0)
#camera.read()

def get_Image(filePath):
    while True:
        success, frame = readImage(filePath)  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def readImage(fileName): 
    img = cv2.imread(f"media/{fileName}", cv2.COLOR_BGR2GRAY)#cv2.IMREAD_COLOR)
    #img = cv2.imread(f"media/{fileName}")
    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return True, img

def gen_frames(fileName,objectType,tscaling,teffect):  
    while True:
        success, frame = readImage(fileName)  # read the camera frame
        if not success:
            break
        else:
            cnt = 0
            #detectMultiScale(gray,scaleFactor=1.05,minNeighbors=5, minSize=(30, 30),flags=cv2.CASCADE_SCALE_IMAGE)
            
            if (objectType == "car"):
                detector=cv2.CascadeClassifier('Haarcascades/haarcascade_car.xml')
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                objectdetect=detector.detectMultiScale(gray,float(tscaling), int(teffect))
                for (x,y,w,h) in objectdetect:
                    cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2) 
                    cnt +=1
                
            elif (objectType == "body"):
                detector=cv2.CascadeClassifier('Haarcascades/haarcascade_fullbody.xml')  
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                objectdetect=detector.detectMultiScale(gray,float(tscaling), int(teffect)) 
                
                #detection=detector.detectMultiScale(frame,scaleFactor=1.5,minSize=(50,50))
                for (x,y,w,h) in objectdetect:
                    cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)  
            
            elif (objectType == "faceeye"):
                eye_cascade=cv2.CascadeClassifier('Haarcascades/haarcascade_eye.xml')  
                detector=cv2.CascadeClassifier('Haarcascades/haarcascade_frontalface_default.xml')
                objectdetect=detector.detectMultiScale(frame,float(tscaling), int(teffect))
                for (x, y, w, h) in objectdetect:   
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    cnt +=1
            else : 
                detector=cv2.CascadeClassifier('Haarcascades/haarcascade_frontalface_default.xml')
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.equalizeHist(gray)  # Normalize brightness and contrast
                gray = cv2.GaussianBlur(gray, (1, 1), 0)  # Optional noise reduction
                
                #objectdetect=detector.detectMultiScale(gray,1.08,1)
                objectdetect = detector.detectMultiScale(gray, float(tscaling), int(teffect))
                #faces1 = detector.detectMultiScale(gray, 1.05, 1)  # For smaller faces
                #faces2 = detector.detectMultiScale(gray, 1.15, 1)  # For larger faces
                #faces = faces1 + faces2  # Combine results
                for (x, y, w, h) in objectdetect:   
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    cnt +=1

            #Draw the rectangle around each face
                 
            '''
            
            faces = detector.detectMultiScale(frame, 1.3, 5)
            for (x,y,w,h) in faces:
                img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                roi_gray = frame[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]
                eyes = eye_cascade.detectMultiScale(roi_gray)
            '''
                
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            cv2.waitKey(0)
            cv2.destroyAllWindows()

@app.route('/')
def index():
    return render_template('index.html',tfileName="Peoples.jpeg")

@app.route('/video_feed')
def video_feed():
    objectType = session.get('objectType', None)
    fileName = session.get('fileName', None)
    tscaling = session['tscaling']
    teffect = session['teffect']
    return Response(gen_frames(fileName,objectType,tscaling,teffect), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/original_feed')
def original_feed():
    
    #filePath =  request.form['tfileName']
    fileName = session.get('fileName', None)
    return Response(get_Image(fileName), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/upload', methods=["POST"])
def upload():
    
    if 'file' not in request.files:
        return "No file selected!"
    else:
        #print(request.files['file'])
        # Get the file object from the request
        file = request.files["file"]
        
        # Save the file to a path
        file.save("media/" + file.filename)
    
    #flash('Files successfully uploaded')
    #request.form['tfileName'] = file.filename
    session['fileName'] = file.filename
    session['objectType'] = str(request.form['objectType'])
    session['tscaling'] = request.form["Objtscaling"]
    session['teffect'] = request.form['Objteffect']
    print("Object Type Value ")
    print(request.form['objectType'])
    #request.form['objectType']

    return render_template(f'show.html',
                           tfileName=request.form['objectType'],
                           tscaling=request.form['Objtscaling'],
                           teffect=request.form['Objteffect']
                           )

if __name__=='__main__':
    #app.run(debug=True)
    port = int(os.environ.get('PORT', 80))
    app.run(debug=True, host='0.0.0.0', port=port)