import hashlib
import json
import os
import shutil
#email sending stuff
import smtplib
import ssl
import tempfile
import traceback
from collections import OrderedDict
from datetime import date
from email.message import EmailMessage

import flask
import pyodbc
import requests
from celery import Celery
from dotenv import load_dotenv

import grader as g

flaskapp = flask.Flask(__name__)
celeryapp = Celery('tasks', broker='pyamqp://guest@localhost//')
flaskapp.config["DEBUG"] = True
load_dotenv()

adminemail=os.getenv('ADMIN_EMAIL')
DB_SERVER_NAME=os.getenv('DB_SERVER_NAME')
DB_USER=os.getenv('DB_USER')
DB_PASSWORD=os.getenv('DB_PASSWORD')
DB_NAME=os.getenv('DB_NAME')
SMTP_HOST=os.getenv('SMTP_HOST')
SMTP_USERNAME=os.getenv('SMTP_USERNAME')
SMTP_PASSWORD=os.getenv('SMTP_PASSWORD')
SMTP_PORT=os.getenv('SMTP_PORT')

#TODO .Heic
#TODO If uploaded wrong page to wrong upload, then we can try it agianst other configs to see if they match.
#TODO Try multipe config scalings in case the box detection is bad

#uploads parsed test data to database
def upload_to_database(examinfo, page_answers):
    conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                      f'Server={DB_SERVER_NAME};'
                      f'Database={DB_NAME};'
                      f'UID={DB_USER};'
                      f'PWD={DB_PASSWORD};'
                      'Trusted_Connection=no;')

    cursor = conn.cursor()
    cursor.execute("insert into Grader_Submissions "\
                   "(First_Name, Last_Name, Email_Address, Test_Type, Test_ID, Submission_JSON) "  \
                   "values (?,?,?,?,?,?)", examinfo['First Name'], examinfo['Last Name'], 
                   examinfo['Email'], examinfo['Test'], examinfo['Test ID'], json.dumps(page_answers))
    cursor.execute("SELECT @@IDENTITY")

    submission_id = int(cursor.fetchone()[0])
    print(f'created subission id {submission_id}')
        
    for section, answers in page_answers.items():
        print(f'Inserting answers for section {section} right meow')
        for qnum, answer in answers.items():
            cursor.execute("insert into Grader_Submissions_Answers "\
                        "(Submission_ID, Test_Section, Test_Question_Number, Test_Question_Answer)" \
                        " values (?,?,?,?)", submission_id, section, qnum, answer)
    conn.commit()

def download_image(imgurl, imgfile):
    #dowloads the imgurl and writes it into imgfile.
    r = requests.get(imgurl, stream = True) 
    if r.status_code == 200:
        for block in r.iter_content(1024):
            imgfile.write(block)
        return True
    else:
        return False
    imgfile.flush()

def handle_system_error(email, adminerrors):
    send_error_message(adminemail, 'Grader System Error', adminerrors)
    student_message = 'Sorry, our system was unable to grade your test. ' +\
                      'Don\'t worry, it is us, not you. ' +\
                      'We will let you know when the problem is resolved.' 
    send_error_message(email, 'Grader System Error',[student_message]) 

@celeryapp.task
def grade_test(examinfo):
    try:
        usererrors = []
        adminerrors = []
        imgurls = examinfo['Image Urls']
        test = examinfo['Test']
        email = examinfo['Email']
        page_answers = OrderedDict()
        print(f'trying to grade from: {email} {test}')
        for i, imgurl in enumerate(imgurls):
            page = i + 1
            with tempfile.TemporaryDirectory() as tmpdirname:
                imgpath = f'{tmpdirname}/tmpimg'
                with open(imgpath, 'wb') as imgfile:
                    download_success = download_image(imgurl, imgfile)
                if download_success:
                    print(f'Wrote image into temporary file succesfully. Grading page {page}')
                    grader = g.Grader()
                    jsonData = grader.grade(imgpath, False, False, 1.0, test.lower(), page)
                    data = json.loads(jsonData)
                    if data['status'] == 0:
                        for box in data['boxes']:
                            print(box['results']['bubbled'])
                            if not box['name'] in page_answers:
                                page_answers[box['name']] = OrderedDict()
                            page_answers[box['name']].update(box['results']['bubbled'])
                    elif 'boxes' in data:
                        for box in data['boxes']:
                            if box['status'] == 1:
                                adminerrors.append(box['error'])
                            elif box['status'] == 2:
                                usererrors.append(box['error'])
                            else:
                                adminerrors.append(f"Unhandled error type {box['status']} {box['error']}")
                    else:
                        adminerrors.append(f"No boxes found because of this error: {data['error']}")
                else:
                    adminerrors.append('Unable to download {imgurl}')
        if len(usererrors) > 0:
            usererrors.insert(0, 'Unable to process test. Errors:')
            send_error_message(email, messagelines=usererrors)
        if len(adminerrors) > 0:
            handle_system_error(email, adminerrors)
        if len(adminerrors) == 0 and len(usererrors) == 0:
            print('No adminerrors or usererrors, uploading to database meow.')
            upload_to_database(examinfo, page_answers)
            #TODO: to be updated based on studypoint feedback
            send_error_message(email, 'Thank you, test has been processed.', ['We have received your test.', 'Thank you','','- Your friendly test grading llamas ;)'])
        else:
            print('Tell me whats going on right meow!. How did we get here?')
    except:
        handle_system_error(email, [traceback.format_exc()])

def send_error_message(email, subject='We had trouble grading your recent test.', messagelines=[]):
    
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = 'adminvpt@studypoint.com'
    msg['To'] = 'max@langhorst.com'
    msg.set_content('\n'.join(messagelines))
    context = ssl.create_default_context()
    try:
        s = smtplib.SMTP(host=SMTP_HOST, port=SMTP_PORT)
        s.starttls(context=context) # Secure the connection
        s.login(user=SMTP_USERNAME, password=SMTP_PASSWORD)
        s.send_message(msg)
    except Exception as e:
        print(e)
    finally:
        s.quit()


def examinfohash(examinfo):
    # makes a hash of everything except the imageurls in examinfo so we can identify student submissions
    dict = {k: v for k, v in examinfo.items() if not k == 'Image Urls'}
    dict['Date Submitted'] = date.today
    return hashlib.sha1(json.dumps(dict, sort_keys=True)).hexdigest()

@flaskapp.route('/v1/grader', methods=['POST'])
def handle_grader_message():
    imageurls = []
    print(flask.request.form)

    if flask.request.form['HandshakeKey'] == 'SPPNscores2020':
        print('Success, form is secure')
    else: 
        print(flask.request.form['HandshakeKey'])
        flask.abort(418)

    test = flask.request.form['Field6']
    if test == 'ACT':
        fields = [17]
    if test == 'SAT':
        fields = [8,9,10,11,12]
    for i in fields:
        imageurls.append(flask.request.form[f'Field{i}-url'])
    #for jason
    #https://studypoint.wufoo.com/api/code/28
    examinfo = {
    'First Name': flask.request.form['Field1'],
    'Last Name': flask.request.form['Field2'], 
    'Email': flask.request.form['Field5'],
    'Test': test,
    'Test ID': flask.request.form['Field15'],
    'Image Urls': imageurls
    }
    print(f'examinfo: {examinfo}')
    grade_test.delay(examinfo)
    return flask.Response(status=202)

@flaskapp.route('/', methods=['GET'])
def home():
    return "<h1>Grader API</h1><p.>This site is a API Portal for AutoGrader</p>"
if __name__ == "__main__":
    flaskapp.run(host='0.0.0.0', port=8000)
