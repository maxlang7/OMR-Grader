import os
import sys
import argparse
import json
import re
import cv2 as cv
from imutils.perspective import four_point_transform
import numpy as np
import config_parser
from collections import deque
from test_box import TestBox
import utils


class Grader:
    def __init__(self):
        self.config = None


    def get_contour_width(self, contour):
        """
        Finds and returns the width of a contour
        """
        _, _, w, _ = cv.boundingRect(contour)
        return w
    
    def sort_contours_by_width(self, contours):
        """
        Sorts the list of contours given by their width using the get_contour_width function
        """
        return sorted(contours, key=lambda x: self.get_contour_width(x), reverse=True)
    
    def get_first_and_last_points(self, contour, xy):
        """
        Gets the first and last points of the contour it is passed 
        ("xy" decides whether it sorts by x or y)
        """
        min_x = [np.inf, 0]
        max_x = [-1, 0]
        min_y = [0, np.inf]
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
        Finds and returns the outside box that contains the entire test. 
        We will use this to scale the given image.

        Args:
            im (numpy.ndarray): An ndarray representing the entire test image.
            test (string): A string saying what type of test we are trying to grade (sat, act, etc)
            debug_mode (boolean): Whether or not we should show images or print in print statements
            threshold_constant (float): What threshold his to be used in the get_threshold function call. 
            P.S. We are looping through many different ones
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
            line_contours = self.get_line_contours(contours[:20], imgray, 6, 6)
            
            
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
            raise Exception(f'We currently only support sat and act (lowercase) not {test}')

        
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

    def merge_lines(self, contour_properties, imgray):
        """
        Goes through all the contour_properties and checks for lines that have similar slope
        and are ending and starting at about the same place. 
        """
        clean_contour_properties = []
        page_height, page_width = imgray.shape
        y_threshold = 0.007*page_height
        x_threshold = 0.1*page_width
        for i, cp in enumerate(contour_properties):
            merged = False
            if 'ignored' in cp:
                continue
            for cp2 in contour_properties[i+1:]:
                # We will merge contours only if:
                # the slopes of cp and cp2 are similar
                # the first y positions are similar
                # they have about the same starting and ending x's
                if np.abs(cp['slope'] - cp2['slope']) < 0.01 and \
                   np.abs(cp['first_point'][1] - cp2['first_point'][1]) < y_threshold and \
                   np.abs(cp['first_point'][0] - cp2['first_point'][0]) < x_threshold and \
                   np.abs(cp['last_point'][0] - cp2['last_point'][0]) < x_threshold:
                        clean_contour_properties.append(cp)
                        cp2['ignored'] = True
                        merged = True
                        break
            # If cp didn't get a merge partner then its still a potential line contour. 
            # If it did find one, we already broke out and will never get here
            # If it is a partner of a line that was already merged, we already got rid of it above
            if not merged:
                clean_contour_properties.append(cp)
        return clean_contour_properties

    def get_line_contour_y(self, line_contour):
        """
        Gets the y position of a line contour by finding the median y of all the points.
        """
        return np.median([p[0][1] for p in line_contour])
        
    def act_draw_boxes(self, image, threshold_constant):
        """
        Converts top and bottom lines into boxes and draws them onto the page.
        """
        threshold = utils.get_threshold(image, threshold_constant)
        # cv.imshow('', threshold)
        # cv.waitKey()
        contours, _ = cv.findContours(threshold, cv.RETR_EXTERNAL, 
            cv.CHAIN_APPROX_SIMPLE)
        contours = self.sort_contours_by_width(contours)
        line_contours = sorted(self.get_line_contours(contours[:20], image, 5, 6), key=lambda y: self.get_line_contour_y(y), reverse=False)
        
        # colorim = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
        # cv.drawContours(colorim,line_contours, -1, (133,255,255), 3)
        # cv.imshow('', colorim)
        # cv.waitKey()
        # we add one because we don't grade the first box
        num_expected_boxes = len(self.config['boxes'])  
        h, w = image.shape
        min_box_height = (h/num_expected_boxes+1)/2
        prev_contour = line_contours[0]
        boxes_to_draw = deque()

        areas_to_erase = []
        x = 1
        for c in line_contours:
            # calculating height by finding difference beween y values.
            current_box_height = self.get_line_contour_y(c) - self.get_line_contour_y(prev_contour)
            erase_height = int(current_box_height*0.05)
            if current_box_height > min_box_height:
                ty = self.get_line_contour_y(prev_contour)
                by = self.get_line_contour_y(c)
                boxes_to_draw.append(np.array(([x,ty+5],[w-1,ty+5],[w-1,by-5], [x,by-5]), dtype=np.int32))
                areas_to_erase.append(np.array(([x,ty-erase_height],[w-1,ty-erase_height],[w-1,ty+erase_height], [x,ty+erase_height]), dtype=np.int32))
            prev_contour = c
        # Make sure that theres a box at the top of the page
        top_box_y_pos = boxes_to_draw[0][0][1]
        bottom_y_pos = boxes_to_draw[-1][-1][1]
        image_height = image.shape[0]
        if top_box_y_pos <= image_height*0.01:
            boxes_to_draw.popleft()
        if bottom_y_pos < image_height*0.99:
            x, ty, by = (0, bottom_y_pos, image_height)
            boxes_to_draw.append(np.array(([0,ty+5],[w,ty+5],[w,by-5], [0,by-5]), dtype=np.int32)) 
        if len(boxes_to_draw) < num_expected_boxes:
            return None
        #need to erase at the very end of the page too
        areas_to_erase.append(np.array(([x,by-erase_height],[w,by-erase_height],[w,by+erase_height], [x,by+erase_height]), dtype=np.int32))
        cv.drawContours(image, areas_to_erase, -1, 255, -1) 
        #the first box contains student info, no answers
        cv.drawContours(image, boxes_to_draw, -1, 0, 1)
        return image

    def get_contour_properties(self, contour):
        """
        Gets the first point, last point, slope, intercept, width, height, and 
        the np.array of the contour pased
        """
        x, y, w, h = cv.boundingRect(contour)
        xs = [p[0][0] for p in contour]
        ys = [p[0][1] for p in contour]
        m,b = np.polyfit(xs,ys,1)
        sorted_contour = sorted(contour, key=lambda p: p[0][0], reverse = False)
        first_point = sorted_contour[0][0]
        last_point = sorted_contour[-1][0]
        if y - first_point[1] < h/2:
            slope = (h/w)*-1
        # we didn't find one in the upper left, so first_point is lower left
        else:
            slope = h/w
        
        return {
                'first_point': first_point, 
                'last_point': last_point,
                'slope': m,
                'intercept': b,
                'width': w,
                'height': h,
                'contour': contour
               }

    def get_line_contours(self, contours, imgray, min_cnum, max_cnum):
        """
        Goes through the list of contours and decides whether they are lines. 

        Args:
            contours (list): A list of contours in the form of np.array()
            imgray (numpy.ndarray): A numpy.ndarray representing the whole test image
            min_cnum (int): The minimum number of contours to return
            max_cnum (int): The maximum number of contours to return 
        Returns:
            line_contours (list): A list of line contours
        """
        line_contours = []
        if len(contours) < min_cnum:
            raise Exception('We could not find the detailed features in your image. Please send an image that has a high enough resolution')
        contour_properties = []
        # We are looping through the contours that are sorted by y position. 
        # keeps only those that are about right length
        for contour in contours:
            contour_properties.append(self.get_contour_properties(contour))
        for properties in contour_properties:
            deviations = []
            slope = properties['slope']
            first_point = properties['first_point']
            for point in properties['contour']:
                point_x = point[0][0]
                point_y = point[0][1]
                pred_y = slope * point_x + properties['intercept']
                deviations.append(np.abs(point_y-pred_y))
            
            average_deviation = np.average(deviations)
            median_deviation = np.median(deviations)
            #print(average_deviation)
            properties['average_deviation'] = average_deviation
            properties['median_deviation'] = median_deviation
            properties['deviations'] = deviations
            properties['height'] = median_deviation*2
                
        # colorim = cv.cvtColor(imgray, cv.COLOR_GRAY2BGR)
        # cv.drawContours(colorim,[cp['contour'] for cp in contour_properties], -1, (133,255,255), 3)
        # cv.imshow('', colorim)
        # cv.waitKey()


        # We have to do some filtering first so that we don't do merge_lines on every single contour
        plausable_line_properties = []
        for cp in contour_properties:
            # this might be able to change because of the new np.fit
            if cp['average_deviation'] < 50:
                plausable_line_properties.append(cp)

        line_widths = []
        plausable_line_properties = self.merge_lines(plausable_line_properties, imgray)
        longest_line_properties = sorted(plausable_line_properties, key=lambda cp: cp['width'], reverse = True)[:6]
        min_line_length = np.median([cp['width'] for cp in longest_line_properties])*0.85
        max_line_length = np.median([cp['width'] for cp in longest_line_properties])*1.5
        median_height = np.median([cp['height'] for cp in longest_line_properties])
        # Now that we've finished merging, we are free to check heights and deviations
        for cp in plausable_line_properties:
            c = cp['contour']
            w = cp['width']
            if cp['height'] < median_height*4 and \
               w >= min_line_length and w <= max_line_length:
                line_contours.append(c)
                line_widths.append(w)
                
        if len(line_contours) < min_cnum or len(line_contours) > max_cnum:
            #find contours with similar slopes and merge them
            raise Exception(f"We couldn't find the right amount lines between the test sections to indentify where the bubbles are. We found these widths {line_widths}")

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
        """
        Uses the config parser file to unpack the config file into self.config
        """
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
        Initializes the data structure we use to return answers and errors/statuses.
        """
        data = {
            'status' : 0,
            'error' : '',
            'boxes' : []
        }
        return data

    def grade(self, image_name, verbose_mode, debug_mode, scale, test, page_number):
        """
        Grades a test image and outputs the result to stdout as a JSON object.
        It goes through many different thresholds to make sure that we get the page

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
        im_w, im_h, _ = im.shape
        if im_w < 1000 or im_h < 1000:
            data['status'] = 2
            data['error'] = f'Your image is not high enough resolution for us to identify bubbles. Please send an image that contains at least 1000 x 1000 pixels.'
            return self.format_error(data)

        # Find largest box within image.
        threshold_constant = 0
        if test == 'act':
            threshold_list = [15, 25, 35, 50, 75]
        elif test == 'sat':
            threshold_list = [25, 35, 50]
        else:
            data['status'] = 2
            data['error'] = f'Unsupported Test Type: {test}.'
            return self.format_error(data)
        page = None
        for threshold_constant in threshold_list:
            data = self.initialize_return_data()
            try:
                config_error = self.initialize_config(test, page_number)
                if config_error is not None:
                    data['status'] = 1
                    data['error'] = config_error
                    return self.format_error(data)
                else:
                    config = self.config
                page = self.find_page(im, test, debug_mode, threshold_constant)
            except Exception as e:
                print(f"Unable to find page: {str(e)} at threshold {threshold_constant}.")
                continue
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

