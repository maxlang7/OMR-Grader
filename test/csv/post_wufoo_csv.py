import csv
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
        reader = csv.DictReader(csvfile)
        #[print(str(i)+':'+value) for i, value in enumerate(line.keys())]
        for line in reader:
            dict_values = list(line.values())
            dict = {'HandshakeKey': 'SPPNscores2020',
            'Field6': line['For which exam are you submitting answers?'],
            'Field17-url': extract_parens(dict_values[29]),
            'Field49-url': extract_parens(dict_values[30]),
            'Field8-url': extract_parens(dict_values[31]),
            'Field9-url': extract_parens(dict_values[32]),
            'Field10-url': extract_parens(dict_values[33]),
            'Field11-url': extract_parens(dict_values[34]),
            'Field12-url': extract_parens(dict_values[35]),
            'Field15': dict_values[26],
            'Field44': dict_values[27],
            'Field45': dict_values[28],
            'Field23': dict_values[8],
            'Field24': dict_values[9],
            'Field5': dict_values[10]
            }
            if mode == 'post':
                requests.post(url, dict)
            elif mode == 'download':
                for i in range(29, 36):
                    imagelink = extract_parens(dict_values[i])
                    if imagelink == '':
                        continue
                    path = urllib.parse.urlparse(imagelink).path
                    extension = os.path.splitext(path)[1]
                    filename = f'/Users/maxanna/Documents/AutoGrader/OMR-Grader/test/images/image{dict_values[9]}{i}.{extension}'
                    urllib.request.urlretrieve(imagelink, filename)


           
            
def extract_parens(input):
    if len(input) == 0:
        return input
    return input.split('(')[1].split(')')[0]

if __name__ == '__main__':
    import_csv_file()
