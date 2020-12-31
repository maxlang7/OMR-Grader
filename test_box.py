import math

import cv2 as cv
from imutils import contours as cutils
import numpy as np
from collections import OrderedDict
import functools
import utils
import operator

class Error(Exception):
    pass

class BoxNotFoundError(Error):
    def __init__(self, message):
        self.message = message

#TODO test_act_page_1: Failed because test 4 found the locations even though the threshold confused the answers.
#TODO test_act_page_1a: Failed because I'm not really sure.... quetion 72 got nothing when its supposed to be 'B'
#TODO test_act_page-1b: Falied because we couldn't detect the line above test 1.
class TestBox:

    def __init__(self, page, config, verbose_mode, debug_mode, scale, test, threshold_constant):
        """
        Constructor for a new test box.

        Args:
            page (numpy.ndarray): An ndarray representing the test image.
            config (dict): A dictionary containing the config file values for 
                this test box.
            verbose_mode (bool): True to run program in verbose mode, False 
                otherwise.
            debug_mode (bool): True to run the program in debug mode, False 
                otherwise.
            scale (float): Factor to scale image slices by.

        Returns:
            TestBox: A newly created test box.

        """
        # Args.
        self.page = page
        self.config = config
        self.verbose_mode = verbose_mode
        self.debug_mode = debug_mode
        self.scale = scale
        self.test = test
        self.threshold_constant = threshold_constant
        # Configuration values.
        self.name = config['name']
        self.type = config['type']
        self.orientation = config['orientation']
        self.multiple_responses = config['multiple_responses']
        self.num_q_per_super_question = config['num_q_per_super_question']
        self.starting_question_num = config['starting_question_num']
        self.x = config['x']
        self.y = config['y']
        self.rows = config['rows']
        self.columns = config['columns']
        self.groups = config['groups']
        self.bubble_width = config['bubble_width']
        self.bubble_height = config['bubble_height']
        self.x_error = config['x_error']
        self.y_error = config['y_error']
        self.min_bubbles_per_box = config['min_bubbles_per_box']
        self.box_to_grade = config['box_to_grade']
        self.num_questions = config['num_questions']
        # Set number of bubbles per question based on box orientation.
        if self.orientation == 'left-to-right':
            self.bubbles_per_q = self.columns
        elif self.orientation == 'top-to-bottom':
            self.bubbles_per_q = self.rows

        self.init_result_structures()

    def init_result_structures(self):
        # Return values.
        self.bubbled = OrderedDict()
        self.unsure = []
        self.images = []
        self.status = 1
        self.error = ''

    def get_bubble_group(self, bubble):
        """
        Finds and returns the group number that a bubble belongs to.

        Args:
            bubble (numpy.ndarray): An ndarray representing a bubble contour.

        Returns:
            int: The bubble's group number or -1 if the bubble does not belong
                to a group.

        """
        (x, y, _w, _h) = cv.boundingRect(bubble)

        # Add offsets to get coordinates in relation to the whole test image 
        # instead of in relation to the test box.
        x += self.x
        y += self.y

        for (i, group) in enumerate(self.groups):
            if (x >= group['x_min'] - self.x_error and
                x <= group['x_max'] + self.x_error and
                y >= group['y_min'] - self.y_error and
                y <= group['y_max'] + self.y_error):
                return i

        return None
    
    def erase_lines(self, box):
        """
        Erases lines from the passed image returning an image without any lines

        Args:
            (numpy.ndarray): An ndarray representing the image containing lines that need to be erased

        Returns: 
            (numpy.ndarray): An ndarray representing the image without lines
            
        """
        low_threshold = 5
        high_threshold = 200
        edges = cv.Canny(box, low_threshold, high_threshold)
        rho = .8  # distance resolution in pixels of the Hough grid
        theta = np.pi / 600  # angular resolution in radians of the Hough grid
        threshold = 90   # minimum number of votes (intersections in Hough grid cell)
        min_line_length = 10  # minimum number of pixels making up a line
        max_line_gap = 2  # maximum gap in pixels between connectable line segments
        line_image = np.copy(box) * 0  # creating a blank to draw lines on
        line_image = cv.cvtColor(line_image, cv.COLOR_GRAY2BGR)

        #find lines on an image
        lines = cv.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                    min_line_length, max_line_gap)
        if lines is None:
            lines = []
            print("No Lines Detected in Image")
        
        for line in lines:
            for x1,y1,x2,y2 in line:
                cv.line(line_image,(x1,y1),(x2,y2),(255,0,0),2)
        #remove found lines from image
        if self.debug_mode:
            cv.imshow('', edges)
            cv.waitKey()
            box_lines = cv.addWeighted(cv.cvtColor(box, cv.COLOR_GRAY2BGR), 0.8, line_image, 1, 0)
            #lines_no_edges = cv.subtract(cv.cvtColor(line_image, cv.COLOR_BGR2GRAY), box)
            cv.imshow('', box_lines)
            cv.waitKey()
            _, thresholded_lines = cv.threshold(cv.cvtColor(line_image, cv.COLOR_BGR2GRAY), thresh=10, maxval=255, type=cv.THRESH_BINARY) 
            box[thresholded_lines==255] = 0
            #box = cv.bilateralFilter(box,3,50,50)
            cv.imshow('', box)
            cv.waitKey()
        return box

    def is_bubble(self, contour):
        """
        Checks if a contour is of sufficient width and height, is somewhat
        circular, and is within the correct coordinates, with margins for error,
        to be counted as a bubble.

        Args:
            contour (numpy.ndarray): An ndarray representing the contour being 
                checked.

        Returns:
            bool: True if contour is counted as a bubble, False otherwise.

        """
        (x, y, w, h) = cv.boundingRect(contour)
        aspect_ratio = w / float(h)
        min_aspect_ratio = self.bubble_width/self.bubble_height * 0.8
        max_aspect_ratio = self.bubble_width/self.bubble_height * 1.3



        # Add offsets to get coordinates in relation to the whole test image 
        # instead of in relation to the test box.
        x += self.x
        y += self.y

        # Ignore contour if not of sufficient width or height, or not circular.
        if (w < self.bubble_width * 0.8 or 
            h < self.bubble_height * 0.8 or
            w > self.bubble_width * 1.2 or 
            h > self.bubble_height * 1.2 or
            aspect_ratio < min_aspect_ratio or
            aspect_ratio > max_aspect_ratio):
            # if self.debug_mode:
            #     if aspect_ratio > min_aspect_ratio and aspect_ratio < max_aspect_ratio and w > 15:
            #         print(f"not considered a bubble because width is {w:.2f} not between, {(self.bubble_width * 0.8):.2f}, {(self.bubble_width * 2.0):.2f}, or height is {h:.2f} not between, {(self.bubble_height * 0.8):.2f}, {(self.bubble_height * 2.0):.2f}, or aspect ratio is {aspect_ratio:.2f} not between {min_aspect_ratio}, {max_aspect_ratio}")
            return False

        return True

    def contours_overlap(self, contour1, contour2):
        if contour1 is None:
            return False
        (x, y, w, h) = cv.boundingRect(contour1)
        if len(contour2) == 2:
            (x1, y1, w1, h1) = [contour2[0], contour2[1], self.bubble_width*0.5, self.bubble_height*0.5]
        else:
            (x1, y1, w1, h1) = cv.boundingRect(contour2)
        # it is easier to calculate the non-overlapping cases because there are less of them.
        return not (x > x1 + w1 or x1 > x + w) and \
               not (y > y1 + h1 or y1 > y + h) 


    def compress_overlapping_bubbles(self, bubbles):
        """
        Finds Bubbles that are overlapping and uses the biggest one.

        Args:
            bubbles (list): A list of bubble contours.
        
        Returns:
            biggest_bubble: The biggest bubble contour.
        """ 
        if len(bubbles) == 1:
            return bubbles[0]
        biggest_area = cv.contourArea(bubbles[0])
        biggest_bubble = bubbles[0]
        biggest_i = 0
        for i, contour in enumerate(bubbles):
            contour_area = cv.contourArea(contour)
            if contour_area >= biggest_area:
                biggest_area = contour_area
                biggest_bubble = contour
                biggest_i = i  
        return biggest_bubble, biggest_i

    def get_expected_bubble_locations(self, box_extremes, group_extremes):
        """
        Uses the extreme points to "draw a grid" to figure out where there should be bubbles
        box_extremes is a list of two things: [xs], [ys]
        group_extremes is a list of box_extremes (one per group)
        """
        locations = []
        sorted_xs = sorted(box_extremes[0])
        sorted_ys = sorted(box_extremes[1])
        top_row_bubble_count = int((len(self.groups) * self.columns)/2)
        top_row_y = np.median(sorted_ys[:top_row_bubble_count])
        bot_row_y = np.median(sorted_ys[-top_row_bubble_count])
        step_size_y = (bot_row_y - top_row_y)/(self.rows -1)
        
        for _ in range(len(self.groups)):
            locations.append([])
        for group_num, group in enumerate(locations):
            sorted_xs = sorted(group_extremes[group_num][0])
            sorted_ys = sorted(group_extremes[group_num][1])
            col_bubble_count = max(int(self.rows/2),2)
            left_col_x = np.median(sorted_xs[1:col_bubble_count])
            right_col_x = np.median(sorted_xs[-col_bubble_count:-1])
            step_size_x = (right_col_x-left_col_x)/(self.columns -1)

            for row in range(self.rows):
                y = top_row_y +(step_size_y * row)
                for column in range(self.columns):
                    x = left_col_x+(step_size_x * column)
                    group.append([x, y])
        return locations

    def get_overlapping_bubbles(self, bubbles, location):
        """
        Loops through all the bubbles and returns any that overlap with location.
        """
        bubble_indices = []        
        for i, group in enumerate(bubbles):
            for j, bubble in enumerate(group):
                if self.contours_overlap(bubble, location):
                    bubble_index = [i, j]
                    bubble_indices.append(bubble_index)
        return bubble_indices

    def all_contours_overlap(self, contour_list):
        for i, contour in enumerate(contour_list):
            for contour_2 in contour_list[i+1:]:
                if not self.contours_overlap(contour, contour_2):
                    return False
        return True

        
    def bubble_cleanup(self, bubbles, box_extremes, group_extremes, box):
        """
        Creates a "grid" of where the bubbles should be located based on the coordinates 
        of bubbles we already found. If there isn't a bubble where there is supposed to 
        be one on the grid, then we call rescue_expected_bubbles on that question.
        Lastly, it gets rid of overlapping bubbles.
        """
        expected_bubble_locations = self.get_expected_bubble_locations(box_extremes, group_extremes)
        if self.debug_mode:
            colorbox = cv.cvtColor(box, cv.COLOR_GRAY2BGR)
            for group in expected_bubble_locations:
                for point in group:
                    cv.circle(colorbox, (int(point[0]), int(point[1])), radius=5, color=(0,0,255), thickness=-1)
            cv.imshow('', colorbox)
            cv.waitKey()
        clean_bubbles = []
        for _ in range(len(self.groups)):
            clean_bubbles.append([])
        model_bubble = bubbles[0][0]
        for group_num, group in enumerate(expected_bubble_locations):
            for i, location in enumerate(group):
                if self.orientation == 'top-to-bottom':
                    offset = group_num * self.columns
                if self.orientation == 'left-to-right':
                    offset = group_num * self.rows
                qnum = int(i/self.bubbles_per_q) + offset
                if qnum >= self.num_questions:
                    break

                bubble_to_append = None
                index_to_append = 0
                overlapping_indices = self.get_overlapping_bubbles(bubbles, location)
                overlapping_bubbles = [bubbles[oi[0]][oi[1]] for oi in overlapping_indices]
                if len(overlapping_bubbles) == 0 and len(clean_bubbles[group_num]) < self.num_questions:
                    bubble_to_append = self.rescue_expected_bubbles(model_bubble, location)
                elif len(overlapping_bubbles) == 1:
                    bubble_to_append = overlapping_bubbles[0]
                elif len(overlapping_bubbles) > 1 and self.all_contours_overlap(overlapping_bubbles):
                    bubble_to_append, index_to_append = self.compress_overlapping_bubbles(overlapping_bubbles)
                else:
                    print(f"All the bubbles in this location ({location}) didn't overlap each other. Not putting a bubble for this location.")
                
                if bubble_to_append is not None:
                    clean_bubbles[group_num].append(bubble_to_append)
                    bubbles[group_num][index_to_append] = None                 
        return clean_bubbles

    def get_bubbles(self, box):
        """
        Finds and return bubbles within the test box.

        Args:
            box (numpy.ndarray): An ndarray representing a test box.

        Returns:
            bubbles (list): A list of lists, where each list is a group of 
                bubble contours.

        """
        # Find bubbles in box.
        contours, _ = cv.findContours(box, cv.RETR_TREE, 
            cv.CHAIN_APPROX_SIMPLE)
    
        # Init empty list for each group of bubbles.
        allbubbles = []
        nonbubbles = []
        group_extremes = []
        bubbles = []
        for _ in range(len(self.groups)):
            bubbles.append([])
            group_extremes.append([[], []])
    
        box_extremes = [[], []]
        # Check if contour is bubble; if it is, add to its appropriate group.
        for contour in contours:
            if self.is_bubble(contour):
                group_num = self.get_bubble_group(contour)
                if group_num is not None: 
                    bubbles[group_num].append(contour)
                    allbubbles.append(contour)                
                    contour_y = np.mean([p[0][1] for p in contour])
                    contour_x = np.mean([p[0][0] for p in contour])
                    box_extremes[0].append(contour_x)
                    box_extremes[1].append(contour_y)
                    group_extremes[group_num][0].append(contour_x)
                    group_extremes[group_num][1].append(contour_y)
            else:
                nonbubbles.append(contour)



        clean_bubbles = self.bubble_cleanup(bubbles, box_extremes, group_extremes, box)

        if self.debug_mode:
            colorbox = cv.cvtColor(box, cv.COLOR_GRAY2BGR)
            # for contour in sorted(contours, key = lambda a: cv.boundingRect(a)[1]):
            #     area = cv.contourArea(contour)
            #     if area < 20:
            #         continue
            #     colorbox_copy = colorbox
            #     cv.drawContours(colorbox_copy, [contour], -1, (0,0,255), 3)
            #     cv.imshow('', colorbox_copy)
            #     cv.waitKey() 
            #show the detected bubbles in yellow.
            for group in clean_bubbles:
                cv.drawContours(colorbox, group, -1, (0,255,255), 5)
            cv.imshow('', colorbox)
            cv.waitKey()
            #show all bubbles in purple
            cv.drawContours(colorbox, allbubbles, -1, (255,0,140), 3)
            cv.imshow('', colorbox)
            cv.waitKey()
            #show the detected contours in green.

        return clean_bubbles, nonbubbles

    def mask_edges(self, im):
        """
        Draws a black contour around the very outside of our box so that we don't pick up a very outer contour.
        """
        im_height, im_width = im.shape
        areas_to_erase = [np.array(([0, 0], [im_width, 0], [im_width, im_height], [0, im_height]))]
        cv.drawContours(im, areas_to_erase, -1, 0, 10)
        return im

    def box_contains_bubbles(self, box, threshold):
        (x, y, w, h) = cv.boundingRect(box)
        bubbles = []
        # Some boxes are too small and can't be 4-point-transformed so they aren't gonna be the one we want anyway.
        
        if w < 100:
            return False
        im = threshold[y:y+h, x:x+w]
        im = cv.resize(im, None, fx=self.scale, fy=self.scale)
        
        #print("box", x, y, w, h)
        im = utils.get_transform(box, threshold)
        im = self.mask_edges(im)
        # if self.debug_mode:
        #     cv.imshow('', im)
        #     cv.waitKey()
        contours, _ = cv.findContours(im, cv.RETR_EXTERNAL, 
            cv.CHAIN_APPROX_SIMPLE)
        
        #colorim = cv.cvtColor(im, cv.COLOR_GRAY2BGR)
        for contour in contours:
            # if self.debug_mode:
            #     #show the detected bubbles in blue.
            #     cv.drawContours(colorim, contour, -1, (255,0,0), 3)
            if self.is_bubble(contour):
                bubbles.append(contour)
        # if self.debug_mode:
        #     print(len(contours))
        #     cv.imshow('', colorim)
        #     cv.waitKey()
        if len(bubbles) < self.min_bubbles_per_box:
            return False
        else:
            return True

    def is_box(self, contour, page):
        """
        Checks if x and y coordinates of a contour match the x and y coordinates
        of this test box, with margins for error.

        Args:
            contour (numpy.ndarray): An ndarray representing the contour being 
                checked.

        Returns:
            bool: True for success, False otherwise.

        """
        (_, _, w, h) = cv.boundingRect(contour)
        page_height, page_width = page.shape
        #eliminating possible boxes based on area so we get the right box to grade.
        if (w*h >= .1 * page_height * page_width and 
            w > .5 * page_width and
            w*h <= .95 * page_height * page_width and
            self.box_contains_bubbles(contour, page)):
            #if self.debug_mode:
                #print(f'Width: {w} Height:{h} Aspect Ratio:{w/h}')
            return True
        else:
            return False


    def similar_box_found(self, contour, potential_boxes):
        for box in potential_boxes:
            if self.contours_overlap(box, contour):
                return True



    def get_box(self, box_num):
        """
        Finds and returns the contour for this test answer box.

        Returns:
            numpy.ndarray: An ndarray representing the answer box in
                the test image.

        """
        # Blur and threshold the page, then find boxes within the page.
        thresh_page = utils.get_threshold(self.page, self.threshold_constant)
        inverted_page = cv.bitwise_not(self.page)
        contours, _ = cv.findContours(thresh_page, cv.RETR_TREE, 
            cv.CHAIN_APPROX_SIMPLE)
        potential_boxes = []
        # Iterate through contours until the correct box is found.
        for contour in contours:
            if self.is_box(contour, thresh_page):
                if not self.similar_box_found(contour, potential_boxes):
                    potential_boxes.append(contour)
        #sorting the potential boxes by y position
        potential_boxes = sorted(potential_boxes, key=lambda b:cv.boundingRect(b)[1])
            
        if len(potential_boxes) == 0:
            raise BoxNotFoundError('No boxes found')
        elif len(potential_boxes) < self.box_to_grade:
            raise BoxNotFoundError('Not enough boxes found on the page')
        else:
            if self.debug_mode:
                colorbox = cv.cvtColor(thresh_page, cv.COLOR_GRAY2BGR)
                cv.drawContours(colorbox, potential_boxes[box_num], -1, (255,0,255), 3)
                cv.imshow('', colorbox)
                cv.waitKey()                        
            return utils.get_transform(potential_boxes[box_num], thresh_page), \
                   utils.get_transform(potential_boxes[box_num], inverted_page)
        
    def init_questions(self):
        """
        Initialize and return a list of empty lists based on the number of
        questions in a group.

        Returns:
            questions (list): A list of empty lists.

        """
        questions = []

        if self.orientation == 'left-to-right':
            num_questions = self.rows
        elif self.orientation == 'top-to-bottom':
            num_questions = self.columns

        for _ in range(num_questions):
            questions.append([])

        return questions

    def get_question_diff(self, config):
        """
        Finds and returns the distance between each question.

        Args:
            config (dict): A dict containing the config values for this bubble
                group.

        Returns:
            float: The distance between questions in this bubble group.

        """
        if self.orientation == 'left-to-right':
            if self.rows == 1:
                return 0
            else:
                return (config['y_max'] - config['y_min']) / (self.rows - 1)
        elif self.orientation == 'top-to-bottom':
            if self.columns == 1:
                return 0
            else:
                return (config['x_max'] - config['x_min']) / (self.columns - 1)

    def get_question_offset(self, config):
        """
        Returns the starting point for this group of bubbles.

        Args:
            config (dict): A dict containing the config values for this bubble
                group.

            Returns:
                float: The starting point for this group of bubbles.

        """
        if self.orientation == 'left-to-right':
            return config['y_min'] - self.y
        elif self.orientation == 'top-to-bottom':
            return config['x_min'] - self.x

    def get_question_num(self, bubble, diff, offset):
        """
        Finds and returns the question number of a bubble based on its 
        coordinates.

        Args:
            bubble (numpy.ndarray): An ndarray representing a bubble contour.
            diff (float): The distance between questions in this bubble group.
            offset (float): The starting point for this group of bubbles.

        Returns:
            int: The question number of this bubble.

        """
        if diff == 0:
            return 0

        (x, y, _, _) = cv.boundingRect(bubble)

        if self.debug_mode:
            print(f"qnum {round((y - offset) / diff)}= bubble y: {y} - offset {offset} / diff: {diff}")


        if self.orientation == 'left-to-right':
            return round((y - offset) / diff)
        elif self.orientation == 'top-to-bottom':
            return round((x - offset) / diff)     

    def group_by_question(self, bubbles, config):
        """
        Groups a list of bubbles by question.

        Args:
            bubbles (list): A list of bubble contours.

        Returns:
            questions (list): A list of lists, where each list contains the 
                bubble contours for a question.

        """
        questions = self.init_questions()
        diff = self.get_question_diff(config)
        offset = self.get_question_offset(config)
    
        for bubble in bubbles:
            question_num = self.get_question_num(bubble, diff, offset)
            questions[question_num].append(bubble)

        return questions

    def get_image_coords(self, question_num, group_num, group_config):
        """
        Finds and returns the coordinates of a question in the test image.

        Args:
            question_num (int): The question number.
            group_num (int): The question's group number.
            config (dict): A dict containing the config values for this bubble
                group.

        Returns:
            x_min (float): Minimum x coordinate.
            x_max (float): Maximum x coordinate.
            y_min (float): Minimum y coordinate.
            y_max (float): Maximum y coordinate.

        """
        diff = self.get_question_diff(group_config)
        offset = self.get_question_offset(group_config)

        if self.orientation == 'left-to-right':
            zerobased_question_num = question_num - (group_num * self.rows) - self.starting_question_num
            x_min = max(group_config['x_min'] - self.x - self.x_error, 0)
            x_max = group_config['x_max'] - self.x + self.x_error
            y_min = max((diff * zerobased_question_num) + offset - (self.y_error / 2), 0)
            y_max = y_min + self.bubble_height + self.y_error
        elif self. orientation == 'top-to-bottom':
            zerobased_question_num = question_num - (group_num * self.columns) - self.starting_question_num
            x_min = max((diff * zerobased_question_num) + offset - (self.x_error / 2), 0)
            x_max = x_min + self.bubble_width + self.x_error
            y_min = max(group_config['y_min'] - self.y - self.y_error, 0)
            y_max = group_config['y_max'] - self.y + self.y_error

        return x_min, x_max, y_min, y_max

    def get_image_slice(self, question_num, group_num, box):
        """
        Crops and returns an image slice for the unsure question.

        Args:
            question_num (int): The question number.
            group_num (int): The question's group number.
            box (numpy.ndarray): An ndarray representing the test box image.

        Returns:
            numpy.ndarray: An ndarray representing the specified question in the
                test image.

        """
        # Get coordinages of image slice.
        config = self.groups[group_num]
        (x_min, x_max, y_min, y_max) = self.get_image_coords(question_num, 
            group_num, config)
        
        if self.debug_mode:
            print(f"image slice coordinates q{question_num} : {round(x_min,1)}-{round(x_max,1)}, {round(y_min,1)}-{round(y_max,1)} ")
        
        # Crop image and scale.
        im = box[int(y_min): int(y_max), int(x_min): int(x_max)]
        im = cv.resize(im, None, fx=self.scale, fy=self.scale)

        return im

    def add_image_slice(self, question_num, group_num, box):
        """
        Adds the image slice for the question to the list of images.

        Args:
            question_num (int): The question number.
            group_num (int): The question's group number.
            box (numpy.ndarray): An ndarray representing the test box image.

        """
        im = self.get_image_slice(question_num, group_num, box)
        encoded_im = utils.encode_image(im)

        # Display image to screen if program runnning in debug mode.
        if self.debug_mode:
            cv.imshow('', im)
            cv.waitKey()

        self.images.append(encoded_im)

    def handle_unsure_question(self, question_num, group_num, box):
        """
        Adds the image slice for the question to the list of images. Adds the
        question to the list of unsure questions.

        Args:
            question_num (int): The question number.
            group_num (int): The question's group number.
            box (numpy.ndarray): An ndarray representing the test box image.

        """
        self.add_image_slice(question_num, group_num, box)
        self.unsure.append(question_num)

    def get_bubble_intensity(self, bubble, box):
        """
        Calculates the percentage of darkened pixels in the bubble contour.

        Args:
            bubble (numpy.ndarray): An ndarray representing the bubble.
            box (numpy.ndarray): An ndarray representing the test box image.

        Returns:
            float: The percentage of darkened pixels in the bubble contour.

        """
        # Sum up all of the pixel values (0 to 255) inside a bubble 
        
        zero_box = np.zeros_like(box)
        cv.ellipse(zero_box, bubble, 255, -1)
        #Could be useful to visualize this function|
        #                                          V
                                                #if self.debug_mode:
                                                    #cv.imshow('', zero_box)
                                                    #cv.waitKey()
        pts = np.where(zero_box == 255)
        return box[pts[0], pts[1]]

    def format_answer(self, bubbled, question_num):
        """
        Formats the answer for this question (string of letters or numbers).

        Args:
            bubbled (str): A string representing the graded answer.
            question_num (int): An zero-based integer representing the question number (used when type is twolineletter) 
        Returns:
            str: A formatted string representing the graded answer, or '-' for
                an unmarked answer.

        """
        if bubbled == '':
            return '-'
        elif bubbled == '?':
            return '?'
        elif self.type == 'number':
            return bubbled
        elif self.type == 'letter':
            return ''.join([chr(int(c) + 65) for c in bubbled])
        elif self.type == 'twolineletter':
            letter_offset = 0
            #if it is in an even number, then we have to offset the original letter because act's letters altrenate ABCD and FGHJ. 
            #There is also no 'I', which makes it even more complicated
            if (question_num - 1)% 2 == 1:
                return_string = ''
                for c in bubbled:
                    if int(c) >= 3:
                        letter_offset = 6
                    else: 
                        letter_offset = 5
                    return_string += chr(int(c) + 65 + letter_offset)
                return return_string
            else:        
                return ''.join([chr(int(c) + 65) for c in bubbled])

                
    def find_contour_by_position(self, contours, expected_x, expected_y, bubble_width, bubble_height):
        #box = self.get_box()
        for contour in contours:
            x, y, w, h = cv.boundingRect(contour)
            if ((w > bubble_width/2 and w < bubble_width) \
               or (h > bubble_height/2 and h < bubble_height*2)) \
               and w*h > bubble_height*bubble_width/3:
                if abs(x - expected_x) < bubble_width and abs(y - expected_y) < bubble_height/2:
                    # if self.debug_mode:
                    #     #show the detected bubbles in yellow.
                    #     colorbox = cv.cvtColor(box, cv.COLOR_GRAY2BGR)
                    #     cv.drawContours(colorbox, contour, -1, (255,0,0), 3)
                    #     cv.imshow('', colorbox)
                    #     cv.waitKey()
                    #     print(f'rescuing: {x, y, w, h}')
                    return contour 
                


    # This function is for when a bubble gets colored outside the lines and its aspect ratio isn't close enough to 1. 
    # We see if it is in the position that we think a bubble will be and if it is we add it to the list of bubbles. 
    def rescue_expected_bubbles(self, good_bubble, location):
        tx, ty, w, h = cv.boundingRect(good_bubble)
        tx, ty = [tx+w/2, ty+h/2]
        expected_x, expected_y = location
        y_add = expected_y - ty
        x_add = expected_x - tx
        copycat_contour = []
        for point in good_bubble:
            copycat_contour.append([[point[0][0]+x_add, point[0][1]+y_add]])
        npcopycat_contour = np.array(copycat_contour, dtype=np.int32)
        if self.debug_mode:
            x, y, w, h = cv.boundingRect(npcopycat_contour)
            print(f'adding missing contour: x:{x} y:{y} w:{w} h:{h}')
        return npcopycat_contour

    def grade_question(self, question, question_num, group_num, box):
        """
        Grades a question and adds the result to the 'bubbled' list.

        Args:
            question (list): A list of bubble contours for the question being
                graded.
            question_num (int): The question number.
            group_num (int): The question's group number.
            box (numpy.ndarray): An ndarray representing the test box image.

        """
        unsure = False
        # If question is missing bubbles, mark as unsure.
        if len(question) != self.bubbles_per_q:
            unsure = True
            self.handle_unsure_question(question_num, group_num, box)

        bubble_vals=[]
        for bubble in question:
            bubble_intensity = sum(self.get_bubble_intensity(bubble, box))
            bubble_vals.append(bubble_intensity)

        # Add image slice if program running in verbose mode and image slice not
        # already added.
        if self.verbose_mode and unsure == False:
            self.add_image_slice(question_num, group_num, box)
        return bubble_vals

    def create_super_question(self, num_q_per_super_question, bubbled):
        """
        For open answer questions, we combine for columns into one super question. 
        Ex. Nothing, 3, /,4 = 0.75
        Args:
            num_q_per_super_question (int): Config file entry for how many columns we should compress into a super question
            bubbled (dict): A dict ordered by question number containing answers.
        """
        super_questions =  OrderedDict()
        super_bubbled = OrderedDict()

        for question_number, answer in bubbled.items():
            zero_based_question_num = question_number - self.starting_question_num
            super_question_num = int(zero_based_question_num/num_q_per_super_question)
            if not super_question_num in super_questions:
                super_questions[super_question_num] = []
            super_questions[super_question_num].append(answer)
        
        for key in super_questions.keys():
            bbld = ''
            bbld1, bbld2, bbld3, bbld4 = super_questions[key]

            def xlate(ans,has_slash=False):
                bbld = ''
                if ans == '-':
                    bbld += ''
                elif ans == '0' and has_slash:
                    bbld += '/'
                elif (has_slash and ans == '1') or   ((not has_slash) and ans == '0'):
                    bbld += '.'
                else:
                    bbld += str(int(ans) - 2)

                return bbld

            bbld += xlate(bbld1,has_slash=False)
            bbld += xlate(bbld2,has_slash=True)
            bbld += xlate(bbld3,has_slash=True)
            bbld += xlate(bbld4,has_slash=False)
            try:
                answer = round(float(eval(bbld)), 3)
            except:
                answer = '-'
            super_bubbled[key + self.starting_question_num] = answer
        return super_bubbled         
    
    def shrink_bubbles(self, clean_question, box):
        """
        shrinks down the bubbles so that we don't get the outer printed ring.
        """
        shrunken_bubbles = []
        for bubble in clean_question:
            scale = 0.6
            centerbubble = cv.fitEllipse(bubble)
            scaledbubble = (centerbubble[0],(centerbubble[1][0]*scale, centerbubble[1][1]*scale),centerbubble[2])
            shrunken_bubbles.append(scaledbubble)

        if self.debug_mode:
            #show the detected bubbles in green.
            colorbox = cv.cvtColor(box, cv.COLOR_GRAY2BGR)
            for shrunken_bubble in shrunken_bubbles:
                cv.ellipse(colorbox, shrunken_bubble, (0,255,0), -1)
            cv.imshow('', colorbox)
            cv.waitKey()
            
        return shrunken_bubbles


    def get_bubble_vals(self, bubbles, nonbubbles, box, graybox):
        """
        Populates a dict with the pixel intensities of each bubble

        Args:
            bubbles (list): A list of lists, where each list is a group of 
                bubble contours.
            nonbubbles (list): A list of the contours that weren't determined to be bubbles.
            box (numpy.ndarray): An ndarray representing the test box.

        """
        bubble_vals = {}
        for (i, group) in enumerate(bubbles):
            # Split a group of bubbles by question.
            qgroup = self.group_by_question(group, self.groups[i])
            # if your qgroup only contains one thing, it is probably not a group, so we should filter it out
            if len(qgroup) <= 1:
                continue
            # Sort bubbles in each question based on box orientation then grade.
            for (j, question) in enumerate(qgroup, self.starting_question_num):
                # Make sure that we have enough bubbles in each question.
                question_num = j + (i * len(qgroup))

                #creates a new lambda function that finds the x coordinate of a contour
                if self.orientation == "top-to-bottom":
                    # if its top to bottom we are using y as the thing to sort by
                    sorter = lambda cntr: cv.boundingRect(cntr)[1]
                elif self.orientation == "left-to-right":
                    # if its top to bottom we are using x as the thing to sort by
                    sorter = lambda cntr: cv.boundingRect(cntr)[0]
                question_sorted = sorted(question, key = sorter)
                if len(question_sorted) < self.bubbles_per_q and self.orientation == "left-to-right" and question_num <= self.num_questions : #and len(clean_question) > 0:
                    raise Exception(f'We were unable to find the expected number of bubbles ({len(question_sorted)} != {self.bubbles_per_q}) for question {question_num}.')
                shrunken_question = self.shrink_bubbles(question_sorted, box)
                if len(shrunken_question) > 0:
                    bubble_vals[question_num] = self.grade_question(shrunken_question, question_num, i, graybox)
        return bubble_vals

    def get_filled_bubble_vals(self, bubble_vals, unfilled_median):
        """
        gets a list of all the certainly filled bubble values
        """
        filled_bubble_vals = []
        expected_filled = len(bubble_vals.keys())
        corrected_bubbles = [b - unfilled_median for b in bubble_vals.values()]
        corrected_top_bubbles = sorted(functools.reduce(operator.iconcat, corrected_bubbles, []))[-1*expected_filled:]
        
        i=0
        #keep dropping the lowest bubble until bottom-top < 50%
        while (corrected_top_bubbles[-1] - corrected_top_bubbles[i])/corrected_top_bubbles[-1] > 0.5:
            i+=1
        if i < expected_filled - 5: 
            filled_bubble_vals = corrected_top_bubbles[i:]
        else: #not enough filled, need to use distance from the unfilled instead
            for question in corrected_bubbles:
                stddev = max(np.std(sorted(question)[0:-1]),100)
                if max(question) > np.median(question)+(stddev*5):
                    filled_bubble_vals.append(max(question))
        return filled_bubble_vals

    def get_qvar(self, question_vals):
        """
        Try to identify a value for a question that distinguishes whether or not one value stands out
        """
        question_vals = sorted(question_vals)
        total = 0
        top_dif = question_vals[-1] - question_vals[-2]
        prev_val = question_vals[0]
        for val in question_vals[1:-1]:
            total += val-prev_val
            prev_val = val
        return top_dif/(total/(len(question_vals)-2))
             

    def grade_bubbles(self, bubble_vals, bubbled):
        # Goes through all bubbles and decides whether they're closer to the 
        # median filled or the median unfilled and updates bubbled accordingly
        num_questions = len(bubble_vals.keys())
        bottom_val_index = int((num_questions*self.bubbles_per_q)*0.3)
        unfilled_bubble_vals = sorted(functools.reduce(operator.iconcat, bubble_vals.values(), []))[0:bottom_val_index]   
        unfilled_median = np.median(unfilled_bubble_vals)
        filled_bubble_vals = self.get_filled_bubble_vals(bubble_vals, unfilled_median)
        filled_median = np.median(filled_bubble_vals)
        qvars = [self.get_qvar(v - unfilled_median) for v in bubble_vals.values()]
        if len(filled_bubble_vals) > 0.4 * num_questions:
            variance_threshold = np.median(qvars) * 0.2
        else: # not enough filled questions, offset from lowest 
            variance_threshold = np.median(sorted(qvars)[0:int(num_questions/2)])* 10
        if self.test == 'act':
            multiplier = 0.55 #ACT has printed letter inside bubbles, so we want to require a higher threshold for bubbled
        elif self.test == 'sat':
            multiplier = 0.5
        filled_threshold = filled_median * multiplier
        for qnum, v in bubble_vals.items():
            corrected_vals = [val - unfilled_median for val in v]
            bubbled[qnum] = ''
            qvar = self.get_qvar(corrected_vals)
            darkest_bubble_val = 0
            darkest_index = None
            
            for bubble_num, val in enumerate(corrected_vals):
                if val > filled_threshold and qvar > variance_threshold:
                    bubbled[qnum] += self.format_answer(str(bubble_num), qnum)
                if val > darkest_bubble_val:
                    darkest_bubble_val = val
                    darkest_index = bubble_num

            #can we rescue bubbles based on a combination of values?        
            if bubbled[qnum] == '' and \
               (( min((qvar / variance_threshold), 1.2)) + \
               (darkest_bubble_val / (filled_threshold*.95)) > 1.65):
                    
                bubbled[qnum] = self.format_answer(str(darkest_index), qnum)
            if bubbled[qnum] == '':
                bubbled[qnum] = self.format_answer('', qnum)
            
        if self.multiple_responses == False:
            for qnum, question in bubbled.items(): 
                 
                if len(question) > 1:
                    # ** Will break if order of percents does not match order that bubbles are in **
                    # see if blank questions are supposed to be blank
                     darkest_index = np.argmax(bubble_vals[qnum])
                     bubbled[qnum] = self.format_answer(str(darkest_index), qnum)
        return bubbled

    def grade(self, page_number, box_num):
        """
        Finds and grades a test box within a test image.

        Returns:
            data (dict): A dictionary containing info about the graded test box.

        """
        # Initialize dictionary to be returned.
        data = {
            'status': 0,
            'error': ''
        }
        # Find box, find bubbles in box, then grade bubbles.
        try:
            gradable_box, gradable_im = self.get_box(box_num)
        except BoxNotFoundError:
            data['status'] = 2
            data['error'] = f'page: {page_number}\n Could not find the boxes inside the page.\n' + \
            'We need this border to straighten and scale the image before grading.\n' + \
            'Please refer to the guidelines document and resubmit.'
            return data
        for (treatment) in enumerate(['', 'erase_lines']):
            self.init_result_structures()
            if treatment == 'erase_lines':
                gradable_box = self.erase_lines(gradable_box)

            for constant in np.linspace(0, 30, 75):
                if constant > 0:
                    gradable_box = utils.get_threshold(cv.bitwise_not(gradable_im), constant)
                bubbles, nonbubbles = self.get_bubbles(gradable_box)
                
                expected_bubble_num = self.bubbles_per_q*self.num_questions
                num_bubbles = sum([len(g) for g in bubbles])
                print(f"Found {num_bubbles} with threshold constant {constant}")
                if num_bubbles == expected_bubble_num:
                    break

            try:
                bubble_vals = self.get_bubble_vals(bubbles, nonbubbles, gradable_box, gradable_im)
            except Exception as err:
                print(err)
                data['status'] = 1
                data['error'] = err
                return data
            self.bubbled = self.grade_bubbles(bubble_vals, self.bubbled)
            if len(self.bubbled) == self.num_questions:
                self.status = 0
                self.error = ''
                break
            else:
                self.error = f"expected {self.num_questions} got {len(self.bubbled)}"
                self.status =  1
        if self.num_q_per_super_question > 1:
            self.bubbled = self.create_super_question(self.num_q_per_super_question, self.bubbled)
        # Add results of grading to return value.
        data['bubbled'] = self.bubbled
        data['unsure'] = self.unsure
        data['images'] = self.images
        data['status'] = self.status
        data['error'] = self.error

        return data

