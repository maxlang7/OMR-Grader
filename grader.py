import os
import sys
import argparse
import json
import re

import cv2 as cv
from imutils.perspective import four_point_transform
import pyzbar.pyzbar as pyzbar

import config_parser
from test_box import TestBox
import utils


class Grader:

    def find_page(self, im):
        """
        Finds and returns the outside box that contains the entire test. Will use this to scale the given image.

        Args:
            im (numpy.ndarray): An ndarray representing the entire test image.

        Returns:
            numpy.ndarray: An ndarray representing the test box in the image.

        """
        # Convert image to grayscale then blur to better detect contours.
        imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
        threshold = utils.get_threshold(imgray)

        # Find contour for entire page. 
        contours, _ = cv.findContours(threshold, cv.RETR_EXTERNAL, 
            cv.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv.contourArea, reverse=True)

        if len(contours) > 0:
            # Approximate the contour.
            for contour in contours:
                peri = cv.arcLength(contour, True)
                approx = cv.approxPolyDP(contour, 0.02 * peri, True)

                # Verify that contour has four corners.
                if len(approx) == 4:
                    page = approx
                    break
        else:
            return None

        # Apply perspective transform to get top down view of page.
        return four_point_transform(imgray, page.reshape(4, 2))

    def image_is_upright(self, page, config):
        """
      This function is a placeholder if you ever need to make sure an image is upright. In most cases it is pretty much useless.



        Args:
            page (numpy.ndarray): An ndarray representing the test image.
            config (dict): A dictionary containing the config file values.

        Returns:
            bool: True if image is upright, False otherwise.
        

        """
        return True

    def upright_image(self, page, config):
        """
        Rotates an image by 90 degree increments until it is upright.

        Args:
            page (numpy.ndarray): An ndarray representing the test image.
            config (dict): A dictionary containing the config file values.

        Returns:
            page (numpy.ndarray): An ndarray representing the upright test 
                image.

        """
        if self.image_is_upright(page, config):
            return page
        else:
            for _ in range(3):
                page = utils.rotate_image(page, 90)
                if self.image_is_upright(page, config):
                    return page
        return None

    def scale_config_r(self, config, x_scale, y_scale, re_x, re_y):
        """
        Recursively scales lists within lists of values in the config dictionary 
        based on the width and height of the image being graded.  

        Args:
            config (dict): An unscaled coordinate mapping read from the 
                configuration file.
            x_scale (int): Factor to scale x coordinates by.
            y_scale (int): Factor to scale y coordinates by.
            re_x (pattern): Regex pattern to match x coordinate key names.
            re_y (pattern): Regex pattern to match y coordinate key names.

        Returns:
            config (dict): A scaled coordinate mapping read from the 
                configuration file. 

        """
        for key, val in config.items():
            if isinstance(val, list):
                for config in val:
                    self.scale_config_r(config, x_scale, y_scale, re_x, re_y)
            if re_x.search(key) or key == 'bubble_width':
                config[key] = val * x_scale
            elif re_y.search(key) or key == 'bubble_height':
                config[key] = val * y_scale

    def scale_config(self, config, width, height):
        """
        Scales the values in the config dictionary based on the width and height
        of the image being graded.

        Args:
            config (dict): An unscaled coordinate mapping read from the 
                configuration file.
            width (int): Width of the actual test image.
            height (int): Height of the actual test image.

        """
        x_scale = width / config['page_width']
        y_scale = height / config['page_height']

        # Regex to match strings like x, qr_x, and x_min.
        re_x = re.compile('(_|^)x(_|$)')
        re_y = re.compile('(_|^)y(_|$)')
        
        self.scale_config_r(config, x_scale, y_scale, re_x, re_y)

    def grade(self, image_name, verbose_mode, debug_mode, scale, test, page_number, box_number = 1):
        """
        Grades a test image and outputs the result to stdout as a JSON object.

        Args:
            image_name (str): Filepath to the test image to be graded.
            verbose_mode (bool): True to run program in verbose mode, False 
                otherwise.
            debug_mode (bool): True to run program in debug mode, False 
                otherwise.
            scale (str): Factor to scale image slices by.
            test (str): Name of test
            page_number (int): Page number of test
            box_number (int): Optional; which box to grade on the test (ordered largest to smallest)

        """
        # Initialize dictionary to be returned.
        data = {
            'status' : 0,
            'error' : ''
        }

        # Cast str to float for scale.
        if scale is None:
            scale = 1.0
        else:
            try:
                scale = float(scale)
            except ValueError:
                data['status'] = 1
                data['error'] = f'Scale {scale} must be of type float'
                return json.dump(data, sys.stdout)

        # Verify that scale is positive.
        if scale <= 0:
            data['status'] = 1
            data['error'] = f'Scale {scale} must be positive'
            return json.dump(data, sys.stdout)

        #TODO: convert other image types to .png
        # Verify that the filepath leads to a .png
        if not (image_name.endswith('.png')):
            data['status'] = 1
            data['error'] = f'File {image_name} must be of type .png'
            return json.dump(data, sys.stdout)

        # Load image. 
        im = cv.imread(image_name)
        if im is None:
            data['status'] = 1
            data['error'] = f'Image {image_name} not found'
            return json.dump(data, sys.stdout)

        # Find largest box within image.
        page = self.find_page(im)
        if page is None:
            data['status'] = 1
            data['error'] = f'Page not found in {image_name}'
            return json.dump(data, sys.stdout) 
        if debug_mode:
            cv.imshow('', page)
            cv.waitKey()

        #Identify configuration file  
        if box_number == 1:
            config_fname = (os.path.dirname(os.path.abspath(__file__)) 
            + f'/config/{test}_page{page_number}.json')
        else:
            config_fname = (os.path.dirname(os.path.abspath(__file__)) 
            + f'/config/{test}_page{page_number}_box{box_number}.json')


        # Read config file into dictionary and scale values. Check for duplicate
        # keys with object pairs hook.
        try:
            with open(config_fname) as file:
                config = json.load(file, 
                    object_pairs_hook=config_parser.duplicate_key_check)
        except FileNotFoundError:
            data['status'] = 1
            data['error'] = f'Configuration file {config_fname} not found'
            return json.dump(data, sys.stdout)

        # Parse config file.
        parser = config_parser.Parser(config, config_fname)
        status, error = parser.parse()
        if status == 1:
            data['status'] = 1
            data['error'] = error
            return json.dump(data, sys.stdout)

        # Scale config values based on page size.
        self.scale_config(config, page.shape[1], page.shape[0])  

        # Rotate page until upright.
        page = self.upright_image(page, config)
        if page is None:
            data['status'] = 1
            data['error'] = f'Could not upright page in {image_name}'
            return json.dump(data, sys.stdout)

        # Grade each test box and add result to data.
        for box_config in config['boxes']:
            box_config['x_error'] = config['x_error']
            box_config['y_error'] = config['y_error']
            box_config['bubble_width'] = config['bubble_width']
            box_config['bubble_height'] = config['bubble_height']
            box_config['min_bubbles_per_box'] = config['min_bubbles_per_box']
            box_config['box_to_grade'] = config['box_to_grade']

            box = TestBox(page, box_config, verbose_mode, debug_mode, scale)
            data[box.name] = box.grade()

        # Output result as a JSON object to stdout.
       # json.dump(data, sys.stdout)
        #print()

         # For debugging.
        return json.dumps(data)


def main():
    """
    Parses command line arguments and grades the specified test.

    """
    # Parse the arguments.
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--image', required=True, 
        help='path to the input image')
    ap.add_argument('-v', action='store_true', required=False, 
        help='enable verbose mode')
    ap.add_argument('-d', action='store_true', required=False, 
        help='enable debug mode')
    ap.add_argument('-s', '--scale', required=False, help='scale image slices')
    args = vars(ap.parse_args())

    # Grade test.
    grader = Grader()
    return grader.grade(args['image'], args['v'], args['d'], args['scale'])


if __name__ == '__main__':
    main()
