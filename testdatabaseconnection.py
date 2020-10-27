from graderapi import upload_to_database
examinfo = {
    'First Name': 'Max',
    'Last Name': 'Langhorst',
    'Email': 'max@langhorst.com',
    'Test': 'SAT',
    'Test ID': 'Practice Test #1'
    }

page_answers = [{1: 'A', 2: 'B', 3: 12.4}]
upload_to_database(examinfo, page_answers)