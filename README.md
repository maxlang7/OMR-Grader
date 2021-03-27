# SAT-ACT Grader
Grader for bubble sheet multiple choice tests using Optical Mark Recognition, Python, and OpenCV. Images should be 300 dpi for maximum accuracy.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisities
```
conda env create -f environment.yml
```

### Deployment
To deploy you can  use 
```
bash deploy.sh
```
Which does the ansible and also activates the conda enviornment.
## Running
There are three ways to run it. 
To run a specific page or box: python dreadnoughtgrader.py --page --imagepath --box --test
To run a program that listens for a WuFoo form with images: python graderapi.py
To run the test suite: Use your test runner of choice in the sat or act test files.

## Possible Improvements
The first thing that could be improved is fixing invalid answers on the SAT super questions. They normally return a no-answer if the answer is invalid, something like "1/". We thought that maybe you could choose the darkest bubble in the next question to make sure the answer has the best chance of being what the student intended.

The different letters on the act have different unfilled thresholds. G is the most, then E, and so on. Encorporating this would only mean making 8 different unfilled_thresholds instead of 1.

.Heic file format. This one is pretty simple, we just have to add a file converter that converts .heic to .jpg or .png.

If the order was mixed up in the Wufoo, we could try  all configs against all pages to find the config with the best bubble detection.

We could scale the config multiple times in case our box detection is a bit off.

## Testing
To test the program, you can use both the sat_test and act_test.py files which will test the results of individual images.

To test graderapi, which normally runs on a server, you can use test_api.sh and then post to it with the post_wufoo_csv.py. 
```
python post_wufoo_csv.py -f pol.csv --url http://localhost:7777/v1/grader
```


## Acknowledgements
* Adrian Rosebrock's tutorial "Bubble sheet multiple choice scanner and test grader using OMR, Python, OpenCV"
* John Fremlin's tutorial "Rotating an image with OpenCV and Python"
* Bthicks's OMR-Grader GitHub Repository (https://github.com/bthicks/OMR-Grader)
