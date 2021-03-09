import csv
import sys
import os
import urllib.parse
import click
from numpy.lib.function_base import extract
import requests
import urllib.request
@click.command()
@click.option('-f', required=True)
@click.option('--mode', required=True, default='post')
@click.option('--url', default='http://ec2-54-174-87-221.compute-1.amazonaws.com:8000/v1/grader', required=True)
def import_csv_file(f, mode, url):
    with open(f, newline='') as csvfile:
        reader = csv.reader(csvfile)
        #[print(str(i)+':'+value) for i, value in enumerate(line.keys())]
        for line in reader:
            if line[0] == 'Entry Id':
                continue
            dict = {'HandshakeKey': 'SPPNscores2020',
            'Field6': line[26],
            'Field17-url': extract_parens(line[30]),
            'Field49-url': extract_parens(line[31]),
            'Field8-url': extract_parens(line[32]),
            'Field9-url': extract_parens(line[33]),
            'Field10-url': extract_parens(line[34]),
            'Field11-url': extract_parens(line[35]),
            'Field12-url': extract_parens(line[36]),
            'Field15': line[27], #SAT version
            'Field44': line[28], #ACT version
            'Field45': line[29],
            'Field23': line[8],
            'Field24': line[9],
            'Field5': line[10]
            }
            if mode == 'post':
                print(dict)
                resp = requests.post(url, dict)
                print(resp)
            elif mode == 'download':
                for i in range(29, 36):
                    imagelink = extract_parens(line[i])
                    if imagelink == '':
                        continue
                    path = urllib.parse.urlparse(imagelink).path
                    extension = os.path.splitext(path)[1]
                    filename = f'/Users/maxanna/Documents/AutoGrader/OMR-Grader/test/images/image{line[9]}{i}.{extension}'
                    urllib.request.urlretrieve(imagelink, filename)


           
            
def extract_parens(input):
    if len(input) == 0:
        return input
    return input.split('(')[1].split(')')[0]

if __name__ == '__main__':
    import_csv_file()
