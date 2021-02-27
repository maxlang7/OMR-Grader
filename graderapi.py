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
import magic # for checking filetypes
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

def handle_system_error(adminerrors):
    send_error_message(adminemail, 'Grader System Error', adminerrors)
    
@celeryapp.task
def grade_test(examinfo):
    try:
        usererrors = []
        adminerrors = []
        imgurls = examinfo['Image Urls']
        test = examinfo['Test']
        email = examinfo['Email']
        name = f'{examinfo["First Name"]} {examinfo["Last Name"]}'
        page_answers = OrderedDict()
        print(f'trying to grade from: {email} {test}')
        for i, imgurl in enumerate(imgurls):
            page = i + 1
            with tempfile.TemporaryDirectory() as tmpdirname:
                imgpath = f'{tmpdirname}/tmpimg'
                with open(imgpath, 'wb') as imgfile:
                    download_success = download_image(imgurl, imgfile)
                if download_success:
                    filetype = magic.from_file(imgpath, mime=True)
                    if not (filetype == "image/png" or filetype == "image/jpeg"):
                        send_error_message(email, 'Error in your Practice Test Submission',
                        [f'Our grading system is unable to score the {test} practice test submitted for {name}.',
                            '',
                            'In order for our system to grade your test, you need to make sure that the image(s) you submitted comply with these guidelines: https://bit.ly/3aiavdW .',
                            '',
                            'It appears that the image(s) you submitted are not the file type that our system can handle.',
                            'Please resubmit your test *as either a .jpg or .png file. Our system is unable to grade .pdf or .heic image formats.*',
                            '',
                            'You can submit corrected images of your test here: https://studypoint.wufoo.com/forms/virtual-practice-test-answer-sheet-upload.',
                            '*Please resubmit all pages.',
                            '',
                            'Thank you!',
                            'StudyPoint'])
                        usererrors.append('invalid_file_format')
                        break
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
                    elif data['status'] == 1:
                        adminerrors.append(f'Problem: {data["error"]}')
                        break
                    elif data['status'] == 2:
                        usererrors.append(data['error'])
                        if data['error'] == 'page_not_found':
                            send_error_message(email, 'Error in your Practice Test Submission', 
                            [f'Our grading system is unable to score the {test} practice test submitted for {name}.',
                            '',
                            'In order for our system to grade your test, you need to make sure that the image(s) you submitted comply with these guidelines: https://bit.ly/3aiavdW .',
                            '',
                            'It appears that the image(s) you submitted do not include the entire page.',
                            'Please resubmit your test ensuring that the *entire outside edge of each page is visible* in each image.',
                            '',
                            'You can submit corrected images of your test here: https://studypoint.wufoo.com/forms/virtual-practice-test-answer-sheet-upload.',
                            '*Please resubmit all pages.',
                            '',
                            'Thank you!',
                            'StudyPoint'])
                        elif data['error'] == 'low_res_image':
                            send_error_message(email, 'Error in your Practice Test Submission', 
                            [f'Our grading system is unable to score the {test} practice test submitted for {name}.',
                            '',
                            'In order for our system to grade your test, you need to make sure that the image(s) you submitted comply with these guidelines: https://bit.ly/3aiavdW .',
                            '',
                            'It appears that the image(s) you submitted are not of high enough resolution for our system.',
                            'Please resubmit your test ensuring that *the image size is at least 1000 x 1000 pixels per page*.',
                            '',
                            'You can submit corrected images of your test here: https://studypoint.wufoo.com/forms/virtual-practice-test-answer-sheet-upload.',
                            '*Please resubmit all pages.',
                            '',
                            'Thank you!',
                            'StudyPoint'])
                        elif data['error'] == 'unsupported_test_type':
                            send_error_message(email, 'Error in your Practice Test Submission', 
                            [f'Our grading system is unable to score the practice test submitted for {name}.',
                            '',
                            'You have selected a test type of PSAT, however our grading system is only able to grade ACT or SAT tests at this time.',
                            '',
                            'Please resubmit your test with the correct test type selected here: https://studypoint.wufoo.com/forms/virtual-practice-test-answer-sheet-upload.',
                            '*Please resubmit all pages.',
                            '',
                            'Thank you!',
                            'StudyPoint'])
                        else: 
                            adminerrors.append('There is some sort of unhandled user error')
                        break
                    elif data['status'] == 3:
                        send_error_message(email, 'Error in your Practice Test Submission', 
                        [f'Our grading system is unable to score the {test} practice test submitted for {name}.',
                        '',
                        'In order for our system to grade your test, you need to make sure that the image(s) you submitted comply with these guidelines: https://bit.ly/3aiavdW .',
                        '',
                        'You can submit corrected images of your test here: https://studypoint.wufoo.com/forms/virtual-practice-test-answer-sheet-upload.',
                        '*Please resubmit all pages.',
                        '',
                        'Thank you!',
                        'StudyPoint'])
                        adminerrors.append(data['error'])
                        handle_system_error(adminerrors)
                        break
                    else:
                        adminerrors.append('unhandled data["status"]') 
                        break
                    
                else:
                    adminerrors.append('Unable to download {imgurl}')
        if len(adminerrors) > 0:
            handle_system_error(adminerrors)
        if len(adminerrors) == 0 and len(usererrors) == 0:
            print('No admin errors or user errors, uploading to database meow.')
            upload_to_database(examinfo, page_answers)
            #TODO: to be updated based on studypoint feedback
            send_error_message(email, 'Thank you, test has been processed.', 
            [f'Thank you for submitting the {test} practice test for {name}.', 
            '',
            'Your test has been scored successfully!',
            '',
            'You can expect a member of our team to reach out to share your scores within 2-3 business days.',
            '',
            'Thank you!',
            'StudyPoint'])
        else:
            print(f'We got some errors, not adding to database: adminerrors: {adminerrors}, usererrors: {usererrors}')
    except:
        handle_system_error([traceback.format_exc()])

def send_error_message(email, subject='We had trouble grading your recent test.', messagelines=[]):
    
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = 'adminvpt@studypoint.com'
    msg['To'] = email
    msg['Cc'] = 'k.langhorst@studypoint.com', 'max@langhorst.com', 'adminvpt@studypoint.com'
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
        imfields = [17]
        verfield = 'Field44'
    elif test == 'SAT':
        imfields = [8,9,10,11,12]
        verfield = 'Field15'
    elif test == 'PSAT':
        imfields = [49]
        verfield = 'Field45'
    else:
        print(f'unhandled test type: {test}')
        flask.abort(406)

    for i in imfields:
        imageurls.append(flask.request.form[f'Field{i}-url'])
    #for anyone updating --> field names documented here:
    #https://studypoint.wufoo.com/api/code/28
    
    examinfo = {
    'First Name': flask.request.form['Field23'],
    'Last Name': flask.request.form['Field24'], 
    'Email': flask.request.form['Field5'],
    'Test': test,
    'Test ID': flask.request.form[verfield],
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
