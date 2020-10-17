# OMR Grader
Grader for bubble sheet multiple choice tests using Optical Mark Recognition, Python, and OpenCV. Images should be 300 dpi for maximum accuracy.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisities
```
conda env create -f environment.yml
```

### Deployment
We are using ansible to manage the configuration of our Aws server. To deploy awsgrader using ansible:
```
ansible-playbook -i hosts setup_grader_server.yml 
```

## Running
There are two types. 
To run a specific page or box: python dreadnoughtgrader.py --page --imagepath --box --test
To run a program that listens for a WuFoo form with images: python graderapi.py


## Acknowledgements
* Adrian Rosebrock's tutorial "Bubble sheet multiple choice scanner and test grader using OMR, Python, OpenCV"
* John Fremlin's tutorial "Rotating an image with OpenCV and Python"
* Bthicks's OMR-Grader GitHub Repository (https://github.com/bthicks/OMR-Grader)
