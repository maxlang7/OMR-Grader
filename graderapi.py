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
celeryapp = Celery('tasks', broker='pyampq://guest@localhost//')
flaskapp.config["DEBUG"] = True

#TODO: add database connection details
#TODO: set up celery (+rabbit mq) on server
database_connection = ""
#TODO Jason questions: wufoo setup account etc, zapier setup (post to http://18.222.170.104/v1/grader),
#Get SMtp server info. Database connection info. Email from adress for errors with grading.

#uploads parsed test data to database
def upload_to_database(data):
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
def grade_test(imgurls, test, email ):
    errors = []

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
                        upload_to_database(data)
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
    print(flask.request.json)
    #imgurls = ['http://langhorst.com/sat_test_1a.png']
    #test = 'SAT'
    #email = 'max@langhorst.com'
    #grade_test.delay(imgurls, test, email)
    return flask.Response(status=202)


@flaskapp.route('/', methods=['GET'])
def home():
    return "<h1>Grader API</h1><p.>This site is a API Portal for AutoGrader</p>"

flaskapp.run(host='0.0.0.0', port=8000)