import math

import cv2 as cv
from imutils import contours as cutils
import numpy as np

import utils

class Error(Exception):
    pass

class BoxNotFoundError(Error):
    def __init__(self, message):
        self.message = message

class TestBox:

    def __init__(self, page, config, verbose_mode, debug_mode, scale):
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

        # Configuration values.
        self.name = config['name']
        self.type = config['type']
        self.orientation = config['orientation']
        self.multiple_responses = config['multiple_responses']
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
        self.bubbled = []
        self.unsure = []
        self.images = []
        self.status = 0
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
        (x, y, w, h) = cv.boundingRect(bubble)

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

        return -1
    
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
        min_aspect_ratio = 0.8
        max_aspect_ratio = 1.3



        # Add offsets to get coordinates in relation to the whole test image 
        # instead of in relation to the test box.
        x += self.x
        y += self.y

        # Ignore contour if not of sufficient width or height, or not circular.
        if (w < self.bubble_width * 0.8 or 
            h < self.bubble_height * 0.8 or
            w > self.bubble_width * 2 or 
            h > self.bubble_height * 2 or
            aspect_ratio < min_aspect_ratio or
            aspect_ratio > max_aspect_ratio):
            if self.debug_mode:
                if aspect_ratio > min_aspect_ratio and aspect_ratio < max_aspect_ratio and w > 15:
                    print(f"not considered a bubble because width is {w:.2f} not between, {(self.bubble_width * 0.8):.2f}, {(self.bubble_width * 2.0):.2f}, or height is {h:.2f} not between, {(self.bubble_height * 0.8):.2f}, {(self.bubble_height * 2.0):.2f}, or aspect ratio is {aspect_ratio:.2f} not between {min_aspect_ratio}, {max_aspect_ratio}")
            return False

        return True
    def compress_overlapping_bubbles(self, bubbles, box):
        """
        Finds Bubbles that are overlapping and uses the bigger one.

        Args:
            bubbles (list): A list of bubble contours.
        
        Returns:
            clean_bubbles (list): A list of bubble contours.
        """ 
        clean_bubbles = []
        first_bubble = bubbles[0]
        for contour in bubbles:
            (x, _y, w, h) = cv.boundingRect(contour)
            (x1, _y1, w1, h1) = cv.boundingRect(first_bubble)
            # it is easier to calculate the non-overlapping cases because there are less of them.
            if not (x > x1 + w1 or x1 > x + w):
                """if self.debug_mode:
                    colorbox = cv.cvtColor(box, cv.COLOR_GRAY2BGR)
                    cv.drawContours(colorbox, contour, -1, (0,255,255), 3)
                    cv.imshow('', colorbox)
                    cv.waitKey()"""
                if w * h >= w1 * h1:
                    clean_bubbles.append(contour)
                    first_bubble = contour
            else:
                clean_bubbles.append(contour)
                first_bubble = contour
                """if self.debug_mode:
                    colorbox = cv.cvtColor(box, cv.COLOR_GRAY2BGR)
                    cv.drawContours(colorbox, contour, -1, (0,255,0), 3)
                    cv.imshow('', colorbox)
                    cv.waitKey()        """
        
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
        bubbles = []
        for _ in range(len(self.groups)):
            bubbles.append([])

        # Check if contour is bubble; if it is, add to its appropriate group.
        for contour in contours:
            if self.is_bubble(contour):
               # what is the contour hierachy (skip contours at innermost level)
                group_num = self.get_bubble_group(contour)
                bubbles[group_num].append(contour)
                allbubbles.append(contour)
                #print(cv.boundingRect(contour)[2])
            else:
                nonbubbles.append(contour)
 
        if self.debug_mode:
            #show the detected bubbles in yellow.
            colorbox = cv.cvtColor(box, cv.COLOR_GRAY2BGR)
            cv.drawContours(colorbox, allbubbles, -1, (0,255,255), 3)
            cv.imshow('', colorbox)
            cv.waitKey()



        return bubbles, nonbubbles

    def box_contains_bubbles(self, box, threshold,):
        (x, y, w, h) = cv.boundingRect(box)
        bubbles = []
        # Some boxes are too small and can't be 4-point-transformed so they aren't gonna be the one we want anyway.
        
        if w < 100:
            return False
        im = threshold[y:y+h, x:x+w]
        im = cv.resize(im, None, fx=self.scale, fy=self.scale)
        if self.debug_mode:
            cv.imshow('', im)
            cv.waitKey()
        #print("box", x, y, w, h)
        im = utils.get_transform(box, threshold)
        contours, _ = cv.findContours(im, cv.RETR_EXTERNAL, 
            cv.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if self.is_bubble(contour):
                 bubbles.append(contour)

        if len(bubbles) < self.min_bubbles_per_box:
            return False
        else:
            return True

    def is_box(self, contour, threshold):
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
        threshh, threshw = threshold.shape
        if (w*h >= .1 * threshh * threshw and #eliminating possible boxes based on area so we get the right box to grade.
            self.box_contains_bubbles(contour, threshold)):
            return True
        else:
            return False

    def get_box(self):
        """
        Finds and returns the contour for this test answer box.

        Returns:
            numpy.ndarray: An ndarray representing the answer box in
                the test image.

        """
        # Blur and threshold the page, then find boxes within the page.
        threshold = utils.get_threshold(self.page)
        contours, _ = cv.findContours(threshold, cv.RETR_TREE, 
            cv.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv.contourArea, reverse=True)
        potential_boxes = []
        # Iterate through contours until the correct box is found.
        #try to handle case 1a, where there is one big outer box and smaller ones inside of it and one of the smaller ones actually contains the bubbles.
        for contour in contours:
            if self.is_box(contour, threshold):
                potential_boxes.append(contour)
        print(len(potential_boxes)) 

        # If is_box doesn't find a box of the right size, accept the page as the box. 
        if len(potential_boxes) == 0:
            raise BoxNotFoundError('No box found on the page')
        else:                
            return utils.get_transform(potential_boxes[self.box_to_grade - 1], threshold)
        
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
            question_num = question_num - (group_num * self.rows) - 1
            x_min = max(group_config['x_min'] - self.x - self.x_error, 0)
            x_max = group_config['x_max'] - self.x + self.x_error
            y_min = max((diff * question_num) + offset - (self.y_error / 2), 0)
            y_max = y_min + self.bubble_height + self.y_error
        elif self. orientation == 'top-to-bottom':
            question_num = question_num - (group_num * self.columns) - 1
            x_min = max((diff * question_num) + offset - (self.x_error / 2), 0)
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
            print(f"image slice coordinates are{x_min}-{x_max}, {y_min}-{y_max} ")
        
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

    def get_percent_marked(self, bubble, box):
        """
        Calculates the percentage of darkened pixels in the bubble contour.

        Args:
            bubble (numpy.ndarray): An ndarray representing the bubble.
            box (numpy.ndarray): An ndarray representing the test box image.

        Returns:
            float: The percentage of darkened pixels in the bubble contour.

        """
        # Applies a mask to the entire test box image to only look at one
        # bubble, then counts the number of nonzero pixels in the bubble.
        mask = np.zeros(box.shape, dtype='uint8')
        cv.drawContours(mask, [bubble], -1, 255, -1)
        mask = cv.bitwise_and(box, box, mask=mask)
        total = cv.countNonZero(mask)
        (x, y, w, h) = cv.boundingRect(bubble)
        area = math.pi * ((max(w, h) / 2) ** 2)

        return total / area

    def format_answer(self, bubbled):
        """
        Formats the answer for this question (string of letters or numbers).

        Args:
            bubbled (str): A string representing the graded answer.

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

    # This function is for when a bubble gets colored outside the lines and its aspect ratio isn't close enough to 1. 
    # We see if it is in the position that we think a bubble will be and if it is we add it to the list of bubbles. 
    def rescue_expected_bubbles(self, qgroup, question_bubbles, contours):
        # use the good bubbles in each question to compute the expected Y
        y_values = []
        for contour in question_bubbles:
            x, y, _, _ = cv.boundingRect(contour)
            y_values.append(y)
           
        expected_y = np.median(y_values)
        # use the good bubbles from the whole group to compute the expected X
        for i in range(len(question_bubbles)): 
            x_values = []
            for row in qgroup:
                if i < len(row):
                    x, y, _, _ = cv.boundingRect(row[i])
                    x_values.append(x)
            expected_x = np.median(x_values)
            if self.debug_mode:
                print(f'expected_x:{expected_x} expected_y:{expected_y}')
        # look through all the contours to try to find one around the right position
        return question_bubbles
       
    

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
        bubbled = ''
        unsure = False

        # If question is missing bubbles, mark as unsure.

        if self.debug_mode:
            colorbox = cv.cvtColor(box, cv.COLOR_GRAY2BGR)
            cv.drawContours(colorbox, question, -1, (0,255,0), 3)
            cv.imshow('', colorbox)
            cv.waitKey()
        if len(question) != self.bubbles_per_q:
            unsure = True
            self.handle_unsure_question(question_num, group_num, box)
            self.bubbled.append('?')
            return

        bubble_pcts=[]
        for (i, bubble) in enumerate(question):
                percent_marked = self.get_percent_marked(bubble, box)
                bubble_pcts.append(percent_marked)
                # If >75% bubbled, count as marked.   
                if percent_marked > 0.75:
                    bubbled += str(i)
                # Count as unsure.
                elif percent_marked > 0.65:
                    unsure = True
                    self.handle_unsure_question(question_num, group_num, box)
                    #bubbled = '?'
                    #break
        if self.multiple_responses == False:
            # find the darkest bubble in a question
            darkest_index = np.argmax(bubble_pcts)
            if bubble_pcts[darkest_index] > .7:
                bubbled = str(darkest_index)

        # Add image slice if program running in verbose mode and image slice not
        # already added.
        if self.verbose_mode and unsure == False:
            self.add_image_slice(question_num, group_num, box)

        self.bubbled.append(self.format_answer(bubbled))

    def grade_bubbles(self, bubbles, nonbubbles, box):
        """
        Grades a list of bubbles from the test box.

        Args:
            bubbles (list): A list of lists, where each list is a group of 
                bubble contours.
            nonbubbles (list): A list of the contours that weren't determined to be bubbles.
            box (numpy.ndarray): An ndarray representing the test box.

        """
        for (i, group) in enumerate(bubbles):
            # Split a group of bubbles by question.
            qgroup = self.group_by_question(group, self.groups[i])
            # if your qgroup only contains one thing, it is probably not a group, so we should filter it out
            if len(qgroup) <= 1:
                continue
            # Sort bubbles in each question based on box orientation then grade.
            for (j, question) in enumerate(qgroup, 1):
                # Make sure that we have enough bubbles in each question.
                question_num = j + (i * len(qgroup))
                #creates a new lambda function that finds the x coordinate of a contour
                cntr_x = lambda cntr: cv.boundingRect(cntr)[0]
                question_sorted = sorted(question, key = cntr_x)
                # box is passed so we can draw the contours during debugging
                clean_questions = self.compress_overlapping_bubbles(question_sorted, box)
                clean_questions = self.rescue_expected_bubbles(qgroup, clean_questions, nonbubbles)
                self.grade_question(clean_questions, question_num, i, box)

    def grade(self):
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
        gradable_box = self.get_box()
        for (treatment) in enumerate(['','erase_lines']):
            self.init_result_structures()
            if treatment == 'erase_lines':
                gradable_box = self.erase_lines(gradable_box)

            bubbles, nonbubbles = self.get_bubbles(gradable_box)
            self.grade_bubbles(bubbles, nonbubbles, gradable_box)
            if len(self.bubbled) == self.num_questions:
                break

        # Add results of grading to return value.
        data['bubbled'] = self.bubbled
        data['unsure'] = self.unsure
        data['images'] = self.images
        data['status'] = self.status
        data['error'] = self.error

        return data

