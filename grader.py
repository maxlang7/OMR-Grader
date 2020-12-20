import os
import sys
import argparse
import json
import re
import cv2 as cv
from imutils.perspective import four_point_transform
import numpy as np
import config_parser
from test_box import TestBox
import utils


class Grader:
    def __init__(self):
        self.config = None


    def get_contour_width(self, contour):
        _, _, w, _ = cv.boundingRect(contour)
        return w
    
    def sort_contours_by_width(self, contours):
        return sorted(contours, key=lambda x: self.get_contour_width(x), reverse=True)
    
    def get_first_and_last_points(self, contour, xy):
        #Gets the first and last points of the contour it is passed (element decides whether it sorts by x or y)
        min_x = [3000000000, 0]
        max_x = [-1, 0]
        min_y = [0, 3000000000]
        max_y = [0, -1]
        
        for point in contour:
            px = point[0][0]
            py = point[0][1]
            if py < min_y[1]:
                min_y = [px, py]
            if px < min_x[0]:
                min_x = [px, py]
            if py > max_y[1]:
                max_y = [px, py]
            if px > max_x[0]:
                max_x = [px, py]
        if xy == 'x':
            return min_x[0], min_x[1], max_x[0], max_x[1]
        if xy == 'y':
            return min_y[0], min_y[1], max_y[0], max_y[1]

    def find_page(self, im, test, debug_mode, threshold_constant):
        """
        Finds and returns the outside box that contains the entire test. Will use this to scale the given image.

        Args:
            im (numpy.ndarray): An ndarray representing the entire test image.
            test (string): A string saying what type of test we are trying to grade (sat, act, etc)

        Returns:
            numpy.ndarray: An ndarray representing the test box in the image.

        """
        # Convert image to grayscale then blur to better detect contours.
        page = None
        imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
        threshold = utils.get_threshold(imgray, threshold_constant)
        if debug_mode:
            cv.imshow('', threshold)
            cv.waitKey()    
        contours, _ = cv.findContours(threshold, cv.RETR_EXTERNAL, 
            cv.CHAIN_APPROX_SIMPLE)
        if test == 'sat':
            contours = sorted(contours, key=cv.contourArea, reverse=True)
            # Approximate the contour.
            for contour in contours:
                if cv.contourArea(contour) < 0.5*imgray.size:
                    continue
                peri = cv.arcLength(contour, True)
                approx = cv.approxPolyDP(contour, 0.02 * peri, True)

                # Verify that contour has four corners.
                if len(approx) == 4:
                    page = approx
                    break
        elif test == 'act':
            contours = self.sort_contours_by_width(contours)
            """
            We are trying to make a top and bottom line into a box that we can four point transform
            We are finding the min length of the first six lines (that is the minimum we could get)
            and find the one with the largest y position (closest to the bottom) 
            that is at least 80% of the first 6 minimum line we calculated before
            """
            
            line_contours = self.get_line_contours(contours[:20])\
            
            
            b1x, b1y, b2x, b2y = self.get_first_and_last_points(line_contours[0], 'x')
            t1x, t1y, t2x, t2y = self.get_first_and_last_points(line_contours[-1], 'x')
            """
            EX:
            t1            t2
            .______________.
            |              |
            |              |
            .______________.
            b1             b2
            """
            page = np.array(([t1x,t1y],[b1x,b1y], [b2x,b2y], [t2x,t2y]), dtype=np.int32)


            if debug_mode:
                colorim = cv.cvtColor(imgray, cv.COLOR_GRAY2BGR)
                cv.drawContours(colorim,line_contours, -1, (133,255,255), 3)
                print([self.get_contour_width(c) for c in line_contours])
                cv.imshow('', colorim)
                cv.waitKey()
            cv.drawContours(imgray,line_contours, -1, 0, 3)

        else:
            #TODO when we add more tests, extend these errors and if block
            raise f'We currently only support sat and act (lowercase) not {test}'

        
        if page is None:
            return None

        # Apply perspective transform to get top down view of page.
        transformed_image = four_point_transform(imgray, page.reshape(4, 2))
        if debug_mode:
            cv.imshow('', transformed_image)
            cv.waitKey()
        if test == 'act':
            transformed_image = self.act_draw_boxes(transformed_image, threshold_constant)
        return transformed_image

    def get_line_contour_y(self, line_contour):
        """
        Gets the y position of a line contour by finding the median y of all the points.
        """
        return np.median([p[0][1] for p in line_contour])
        
    def act_draw_boxes(self, image, threshold_constant):
        """
        Converts top and bottom lines into boxes and draws them onto the page

        """
        threshold = utils.get_threshold(image, threshold_constant)
        # cv.imshow('', threshold)
        # cv.waitKey()
        contours, _ = cv.findContours(threshold, cv.RETR_EXTERNAL, 
            cv.CHAIN_APPROX_SIMPLE)
        contours = self.sort_contours_by_width(contours)
        line_contours = sorted(self.get_line_contours(contours[:20]), key=lambda y: self.get_line_contour_y(y), reverse=False)

            
        ty = self.get_line_contour_y(line_contours[0])
        by = self.get_line_contour_y(line_contours[-1])
        page_y_dif = by - ty 
        min_box_height = page_y_dif/(len(self.config['boxes'])+1)/2
        prev_contour = line_contours[0]
        boxes_to_draw = []
        areas_to_erase = []
        x = 0
        w = image.shape[0]
        for c in line_contours:
            # calculating height by finding difference beween y values.
            current_box_height = self.get_line_contour_y(c) - self.get_line_contour_y(prev_contour)
            if current_box_height > min_box_height:
                ty = self.get_line_contour_y(prev_contour)
                by = self.get_line_contour_y(c)
                boxes_to_draw.append(np.array(([x,ty],[x+w,ty],[x+w,by-5], [x,by-5]), dtype=np.int32))
                areas_to_erase.append(np.array(([x,ty-8],[x+w,ty-8],[x+w,ty+8], [x,ty+8]), dtype=np.int32))
            prev_contour = c
        
        cv.drawContours(image, areas_to_erase, -1, 255, 40)   
        cv.drawContours(image, boxes_to_draw[1:], -1, 0, 2)
        return image


    def get_line_contours(self, contours):
        #sorts contours by y position
        line_contours = []
        if len(contours) < 6:
            raise Exception('We could not find the detailed features in your image. Please send an image that has a high enough resolution')
        min_line_length = self.get_contour_width(contours[5])*0.8
        max_line_length = self.get_contour_width(contours[5])*1.5
        # We are looping through the contours that are sorted by y position. 
        # keeps only those that are about right length
        for c in sorted(contours, key=lambda y: self.get_contour_width(y), reverse=False): #the contours sorted by y postion on page
            w = self.get_contour_width(c)
            if w >= min_line_length and w <= max_line_length:
                line_contours.append(c)
        return sorted(line_contours, key=lambda a: self.get_line_contour_y(a), reverse = False)



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
    
    def format_error(self, data):
        return json.dumps(data)

    def initialize_config(self, test, page_number):
        
        #Identify configuration file  
        config_fname = (os.path.dirname(os.path.abspath(__file__)) 
        + f'/config/{test}_page{page_number}.json')


        # Read config file into dictionary and scale values. Check for duplicate
        # keys with object pairs hook.
        try:
            with open(config_fname) as file:
                config = json.load(file, 
                    object_pairs_hook=config_parser.duplicate_key_check)
        except FileNotFoundError:
            return f'Configuration file {config_fname} not found'

        # Parse config file.
        parser = config_parser.Parser(config, config_fname)
        self.config =  config
        status, error = parser.parse()
        if status == 1:
            return error 

        return None

    def initialize_return_data(self):
        """
        Initializes the data structure we use to return answers and errors/statuses
        """
        data = {
            'status' : 0,
            'error' : ''
        }
        return data

    def grade(self, image_name, verbose_mode, debug_mode, scale, test, page_number):
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
        """
        # Initialize dictionary to be returned.
        data = self.initialize_return_data()

        # Cast str to float for scale.
        if scale is None:
            scale = 1.0
        else:
            try:
                scale = float(scale)
            except ValueError:
                data['status'] = 1
                data['error'] = f'Scale {scale} must be castable to type float'
                return self.format_error(data)

        # Verify that scale is positive.
        if scale <= 0:
            data['status'] = 1
            data['error'] = f'Scale {scale} must be positive'
            return self.format_error(data)

        # Load image. 
        im = cv.imread(image_name)
        if im is None:
            data['status'] = 1
            data['error'] = f'Image {image_name} not found'
            return self.format_error(data)

        config_error = self.initialize_config(test, page_number)
        if config_error is not None:
            data['status'] = 1
            data['error'] = config_error
            return self.format_error(data)
        else:
            config = self.config

        # Find largest box within image.
        threshold_constant = 0
        if test == 'act':
            threshold_list = [25, 50, 75]
        if test == 'sat':
            threshold_list = [25, 35, 50]
        for threshold_constant in threshold_list:
            data = self.initialize_return_data()
            try:
                page = self.find_page(im, test, debug_mode, threshold_constant)
            except Exception as e:
                data['status'] = 2
                data['error'] = str(e)
                return self.format_error(data)
            if page is not None:
                # Scale config values based on page size.
                self.scale_config(config, page.shape[1], page.shape[0])
                # Rotate page until upright.
                page = self.upright_image(page, config)
                if page is None:
                    data['status'] = 1
                    data['error'] = f'Could not upright page in {image_name}'
                    return self.format_error(data)

                # Grade each test box and add result to data.
                data['boxes'] = []
                for box_num, box_config in enumerate(config['boxes']):  
                    #For debugging purposes: if box_num != 3: continue
                    box_config['x_error'] = config['x_error']
                    box_config['y_error'] = config['y_error']
                    box_config['bubble_width'] = config['bubble_width']
                    box_config['bubble_height'] = config['bubble_height']
                    box_config['min_bubbles_per_box'] = config['min_bubbles_per_box']
                    box_config['box_to_grade'] = config['box_to_grade']

                    box = TestBox(page, box_config, verbose_mode, debug_mode, scale, test, threshold_constant) #make cleaner with new lines
                    results = box.grade(page_number, box_num)
                    if box.status == 0:
                        data['boxes'].append({'name': box.name, 'results': results, 'status': box.status, 'error': box.error})
                    else:
                        break
                successful_boxes = 0
                for box in data['boxes']:
                    if box['status'] == 0:
                        successful_boxes+=1
                if successful_boxes == len(config['boxes']):
                    break
    

        if page is None:    
            data['status'] = 2
            data['error'] = f'We were unable to find the outer features of the test. Please refer to the guidelines and resubmit your test.'
            return self.format_error(data) 
        
        if len(config['boxes']) != len(data['boxes']):
            data['status'] = 1
            data['error'] = f'We found a page but were unable to find any boxes in {image_name} with threshold constant:{threshold_constant}'
            return self.format_error(data)

        for box in data['boxes']:
            if box['status'] != 0:
                data['status'] = 1
                data['error'] = "One of the boxes in this page failed. For more details, look in the boxes['status'] and boxes['error']"
                break

        return json.dumps(data)

