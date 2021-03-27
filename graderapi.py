import hashlib
import json
import os
import shutil
#email sending stuff
import smtplib
import ssl
import jinja2
import tempfile
import traceback
from collections import OrderedDict
from datetime import date
from email.message import EmailMessage

import flask
import magic # for checking filetypes
import pyodbc
import yaml
import requests
from dotenv import load_dotenv
load_dotenv()
from worker import celeryapp
import grader as g

flaskapp = flask.Flask(__name__)
flaskapp.config["DEBUG"] = True

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
#TODO If uploaded wrong page to wrong upload, then we can try it against other configs to see if they match.
#TODO Try multiple config scalings in case the box detection is bad

def format_email_message(email_tag, email_variables):
    """
        Formats the email_messages.yml and returns a string we can email.

        Args:
            email_tag (str): a tag that identifies which email to take
            email_variables (dict): Variables we need to replace (e.g. {{name}} and {{test}})
        Returns:
            Formatted email subject, ready to send ('str')
            Formatted email body, ready to send ('str')
    """
    email_messages_file = 'email_messages.yml'
    with open(email_messages_file) as yaml_file:
        raw_email_config = yaml_file.read().rstrip()
    template = jinja2.Template(raw_email_config)
    prepped_email_config = template.render(email_variables)
    cooked_email_config = yaml.safe_load(prepped_email_config)
    if not email_tag in cooked_email_config:
        email_tag = 'unhandled_image_error'
        message = f'email_tag {email_tag} does not exist in {email_messages_file}'
        print(message)
        send_email(adminemail, 'Admin Error', messagelines=[message], send_email_flag=True)
        
    plated_email_config = [cooked_email_config[email_tag]['subject'],
                           cooked_email_config[email_tag]['body']]
    return plated_email_config

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
    
@celeryapp.task
def grade_test(examinfo, send_email_flag):
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
                        usererrors.append('unsupported_image_format')
                        break
                    print(f'Wrote image into temporary file succesfully. Grading page {page}')
                    grader = g.Grader()
                    jsonData = grader.grade(imgpath, False, False, 1.0, test.lower(), page, imgurl)
                    data = json.loads(jsonData)
                    if data['status'] == 0:
                        for box in data['boxes']:
                            print(box['results']['bubbled'])
                            if not box['name'] in page_answers:
                                page_answers[box['name']] = OrderedDict()
                            page_answers[box['name']].update(box['results']['bubbled'])
                    elif data['status'] == 2:
                        usererrors.append(data['error'])                      
                        break
                    else:
                        adminerrors.append(data['error'])
                else:
                    adminerrors.append('Unable to download {imgurl}')
                    
        if len(adminerrors) == 0 and len(usererrors) == 0:
            if not DB_SERVER_NAME == 'skipdb':
                print('No admin errors or user errors, uploading to database meow.')  
                upload_to_database(examinfo, page_answers)
            subject, body = format_email_message('succesful_submission', {'test': test, 'name': name})
            send_email(email, subject, body, send_email_flag)
        
        else:
            print(f'We got some errors, not adding to database: adminerrors: {adminerrors}, usererrors: {usererrors}')
            if len(usererrors) > 0:
                try:
                    subject, body = format_email_message(usererrors[0], {'test': test, 'name': name})
                except:
                    #this means we got a non-specific user error
                    subject, body = format_email_message('unhandled_image_error', {'test': test, 'name': name})
                send_email(email, subject, body, send_email_flag)

            elif len(adminerrors) > 0:
                subject, body = format_email_message('unhandled_image_error', {'test': test, 'name': name})
                send_email(email, subject, body, send_email_flag)
                send_email(adminemail, 'Grader System Error', adminerrors, send_email_flag)

            else:
                send_email(adminemail, 'Crazy Town Error', f'How did we get here? {[traceback.format_exc()]}', send_email_flag)
    except:
        send_email(adminemail, 'Crazy Town Error', f'How did we get here? {[traceback.format_exc()]}', send_email_flag)

def send_email(email, subject='We had trouble grading your recent test.', messagelines=[], send_email_flag=False):
    if not send_email_flag:
        print(f'Skipping email, but it would be {messagelines}')
        return
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = 'adminvpt@studypoint.com'
    msg['To'] = email
    msg['Bcc'] = 'k.langhorst@studypoint.com', 'max@langhorst.com', 'adminvpt@studypoint.com'
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
    print('here')
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
    send_email = True
    if 'SendEmail' in flask.request.form and flask.request.form['SendEmail'] == 'False':
        print(f"Not sending email")
        send_email = False
    grade_test.delay(examinfo, send_email)
    return flask.Response(status=202)

@flaskapp.route('/', methods=['GET'])
def home():
    return "<h1>Grader API</h1><p.>This site is a API Portal for AutoGrader</p>"
if __name__ == "__main__":
    flaskapp.run(host='0.0.0.0', port=8000)
