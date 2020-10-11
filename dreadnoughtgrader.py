import click
import grader as g
import json

#database connnection information


@click.command()
@click.option('--test', type=click.Choice(['SAT', 'ACT']), default='SAT', help='test to grade', required=True)
@click.option('--page', type=int, help='page to grade (1, 2, 3 etc.)', required=True)
@click.option('--box', type=int, help='box to grade (top box = 1)', required=True)
@click.option('--imgpath', help='path to image to grade', required=True)
def dreadnought(test, page, box, imgpath):
    click.echo(f'Grading {imgpath} ({test} page {page} box {box})...')
    """ 
    """
    grader = g.Grader()
    jsonData = grader.grade(imgpath, False, False, 1.0, test.lower(), box, page)
    data = json.loads(jsonData)
    print(data['answer']['bubbled'])

if __name__ == '__main__':
    dreadnought()
