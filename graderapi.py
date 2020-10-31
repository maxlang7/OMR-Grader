import hashlib
import json
import os
import shutil
#email sending stuff
import smtplib
import ssl
import tempfile
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
DB_SERVER_NAME=os.getenv('DB_SERVER_NAME')
DB_USER=os.getenv('DB_USER')
DB_PASSWORD=os.getenv('DB_PASSWORD')
DB_NAME=os.getenv('DB_NAME')
SMTP_HOST=os.getenv('SMTP_HOST')
SMTP_USERNAME=os.getenv('SMTP_USERNAME')
SMTP_PASSWORD=os.getenv('SMTP_PASSWORD')
SMTP_PORT=os.getenv('SMTP_PORT')

#TODO .Heic

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

    for pagecounter, page in enumerate(page_answers):
        for qnum, answer in page.items():
            cursor.execute("insert into Grader_Submissions_Answers "\
                        "(Submission_ID, Test_Section, Test_Question_Number, Test_Question_Answer)" \
                        " values (?,?,?,?)", submission_id, pagecounter+1, qnum, answer)
    conn.commit()

#pages don't all start with 1, so we need to handle that situation

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
    page_answers = []
    print(f'trying to grade from: {email} {test} ')
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
                    #TODO imgpath?? did we download ok?
                    jsonData = grader.grade(imgpath, False, False, 1.0, test.lower(), box, page)
                    data = json.loads(jsonData)
                    print(data['answer']['bubbled'])
                    if data['status'] == 0:
                        page_answers.append(data['answer']['bubbled'])
                    else:
                        errors.append(data['error'])
                else:
                    errors.append('Unable to download {imgurl}')
    if len(errors) > 0:
        send_error_message(email, errors)
    else:
        upload_to_database(examinfo, page_answers)

def send_error_message(email, errors):
    
    msg = EmailMessage()
    msg['Subject'] = 'We had trouble grading your recent test.'
    msg['From'] = 'adminvpt@studypoint.com'
    msg['To'] = email
    msg.set_content('Unable to process test. Errors:' + '\n'.join(errors))
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
    #TODO: determine and parse POSTed message
    imageurls = []
    print(flask.request.form)

    if flask.request.form['HandshakeKey'] == 'SPPNscores2020':
        print('Success, form is secure')
    else: 
        print(flask.request.form['HandshakeKey'])
        raise InvalidUsage("Invalid submission", status_code=418)
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
    print(f'examinfo: {examinfo}'
    grade_test.delay(examinfo)
    return flask.Response(status=202)

@flaskapp.route('/', methods=['GET'])
def home():
    return "<h1>Grader API</h1><p.>This site is a API Portal for AutoGrader</p>"
if __name__ == "__main__":
    flaskapp.run(host='0.0.0.0', port=8000)
