import flask
import tempfile
import requests
#email sending stuff
import smtplib
from email.message import EmailMessage

import shutil
import grader as g
import json
from celery import Celery
flaskapp = flask.Flask(__name__)
celeryapp = Celery('tasks', broker='pyamqp://guest@localhost//')
flaskapp.config["DEBUG"] = True

#TODO: add database connection details
#TODO: set up celery (+rabbit mq) on server
database_connection = ""
#TODO Jason questions:Get SMtp server info. Database connection info.
#adminvpt@studypoint.com
#uploads parsed test data to database
def upload_to_database(data, examinfo):
    
    return True

def download_image(imgurl, imgpath):
    #dowloads the imgurl and writes it into imgpath.
    r = requests.get(imgurl, stream = True) 
    if r.status_code == 200:
        r.raw.decode_content=True
        shutil.copyfileobj(r.raw, imgpath)
        return True
    else:
        return False

@celeryapp.task
def grade_test(examinfo):
    errors = []
    imgurls = examinfo['Image Urls']
    test = examinfo['Test']
    email = examinfo['Email']
    for i, imgurl in enumerate(imgurls):
        page = i + 1
        if page == 3 or page == 5:
            boxes = [1,2]
        else:
            boxes = [1]
        for box in boxes:
            with tempfile.TemporaryFile() as imgpath:
                download_success = download_image(imgurl, imgpath)
                if download_success:
                    grader = g.Grader()
                    jsonData = grader.grade(imgpath, False, False, 1.0, test.lower(), box, page)
                    data = json.loads(jsonData)
                    print(data['answer']['bubbled'])
                    if data['status'] == 0:
                        upload_to_database(data['answer']['bubbled'], examinfo)
                    else:
                        errors.append(data['error'])
                else:
                    errors.append('Unable to download {imgurl}')
    if len(errors) > 0:
        send_error_message(email, errors)   

def send_error_message(email, errors):
    msg = EmailMessage()
    msg['Subject'] = 'We had trouble grading your recent test.'
    msg['From'] = 'grader@studypoint.com'
    msg['To'] = email
    msg.set_content('Unable to process test. Errors:' + errors.join('\n'))
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
  
@flaskapp.route('/v1/grader', methods=['POST'])
def handle_grader_message():
    #TODO: determine and parse POSTed message
    imageurls = []
    print(flask.request.json)
    for i in [8,9,10,11,12]:
        imageurls.append(flask.request.json[f'Field{i}_url'])
    #for jason
    examinfo = {
    'First Name': flask.request.json['Field1'],
    'Last Name': flask.request.json['Field2'], 
    'Email': flask.request.json['Field5'], 
    'Test': flask.request.json['Field6'],
    'Image Urls': imageurls
    }
    grade_test.delay(examinfo)
    return flask.Response(status=202)

@flaskapp.route('/', methods=['GET'])
def home():
    return "<h1>Grader API</h1><p.>This site is a API Portal for AutoGrader</p>"
if __name__ == "__main__":
    flaskapp.run(host='0.0.0.0', port=8000)