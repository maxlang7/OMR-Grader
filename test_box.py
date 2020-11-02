import math

import cv2 as cv
from imutils import contours as cutils
import numpy as np
from collections import OrderedDict

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


    def contours_overlap(self, contour1, contour2):
        (x, y, w, h) = cv.boundingRect(contour1)
        (x1, y1, w1, h1) = cv.boundingRect(contour2)
        # it is easier to calculate the non-overlapping cases because there are less of them.
        return not (x > x1 + w1 or x1 > x + w) and \
               not (y > y1 + h1 or y1 > y + h) 


    def compress_overlapping_bubbles(self, bubbles, box):
        """
        Finds Bubbles that are overlapping and uses the bigger one.

        Args:
            bubbles (list): A list of bubble contours.
        
        Returns:
            clean_bubbles (list): A list of bubble contours.
        """ 
        clean_bubbles = []
        if len(bubbles) == 0:
            return bubbles
        first_bubble = bubbles[0]
        for contour in bubbles:
            if self.contours_overlap(contour, first_bubble):
                (_x, _y, w, h) = cv.boundingRect(contour)
                (_x1, _y1, w1, h1) = cv.boundingRect(first_bubble)
                """if self.debug_mode:j
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
                if group_num is not None: 
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
            self.box_contains_bubbles(contour, page)):
            if self.debug_mode:
                print(f'{w}:{h} {w/h}')
            return True
        else:
            return False


    def similar_box_found(self, contour, potential_boxes):
        for box in potential_boxes:
            if self.contours_overlap(box, contour):
                return True



    def get_box(self):
        """
        Finds and returns the contour for this test answer box.

        Returns:
            numpy.ndarray: An ndarray representing the answer box in
                the test image.

        """
        # Blur and threshold the page, then find boxes within the page.
        thresh_page = utils.get_threshold(self.page)
        contours, _ = cv.findContours(thresh_page, cv.RETR_TREE, 
            cv.CHAIN_APPROX_SIMPLE)
        potential_boxes = []
        # Iterate through contours until the correct box is found.
        #try to handle case 1a, where there is one big outer box and smaller ones inside of it and one of the smaller ones actually contains the bubbles.
        for contour in contours:
            if self.is_box(contour, thresh_page):
                if not self.similar_box_found(contour, potential_boxes):
                    potential_boxes.append(contour) 
        if len(potential_boxes) == 0:
            return None
        #sorting potential boxes by y position
        boundingBoxes = [cv.boundingRect(box) for box in potential_boxes]
        (potential_boxes, boundingBoxes) = zip(*sorted(zip(potential_boxes, boundingBoxes), key=lambda b:b[1][1]))

        # If is_box doesn't find a box of the right size, accept the page as the box. 
        if len(potential_boxes) == 0:
            raise BoxNotFoundError('No box found on the page')
        elif len(potential_boxes) < self.box_to_grade:
            raise BoxNotFoundError('Not enough boxes found on the page')
        else:                
            return utils.get_transform(potential_boxes[self.box_to_grade - 1], thresh_page)
        
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
        # We were using the max of the contour w and h before and any bubbles colored outside 
        # the lines didn't have the right total area because their radiuses were too big.
        _, _, w, h = cv.boundingRect(bubble)
        area = math.pi * ((np.average([h, w])/2) ** 2)

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
    def find_contour_by_position(self, contours, expected_x, expected_y, bubble_width, bubble_height):
        box = self.get_box()
        for contour in contours:
            x, y, w, h = cv.boundingRect(contour)
            if ((w > bubble_width/2 and w < bubble_width*2) \
               or (h > bubble_height/2 and h < bubble_height*2)) \
               and w*h > bubble_height*bubble_width/3:
                if abs(x - expected_x) < bubble_width*2 and abs(y - expected_y) < bubble_height/2:
                    if self.debug_mode:
                        #show the detected bubbles in yellow.
                        colorbox = cv.cvtColor(box, cv.COLOR_GRAY2BGR)
                        cv.drawContours(colorbox, contour, -1, (255,0,0), 3)
                        cv.imshow('', colorbox)
                        cv.waitKey()
                        print(f'rescuing: {x, y, w, h}')
                    return contour 
                


    # This function is for when a bubble gets colored outside the lines and its aspect ratio isn't close enough to 1. 
    # We see if it is in the position that we think a bubble will be and if it is we add it to the list of bubbles. 
    def rescue_expected_bubbles(self, qgroup, question_bubbles, nonbubblecontours):
        # use the good bubbles in each question to compute the expected Y
        y_values = []
        supplemented_bubbles = []
        expected_xs = []
        for contour in question_bubbles:
            x, y, _, _ = cv.boundingRect(contour)
            y_values.append(y)
           
        expected_y = np.median(y_values)
        # use the good bubbles from the whole group to compute the expected X
        for i in range(self.bubbles_per_q): 
            x_values = []
            for row in qgroup:
                row_xs = []
                for contour in row:
                    x, y, _, _ = cv.boundingRect(contour)
                    row_xs.append(x)
                row_xs.sort()
                if i < len(row):
                    x_values.append(row_xs[i])
            expected_xs.append(np.median(x_values))
        expected_xs.sort()
        if self.debug_mode:
            print(f'expected_xs:{expected_xs} expected_y:{expected_y}')
        # look through all the contours to try to find one around the right position
        for i, expected_x in enumerate(expected_xs):
            foundbubble = False    
            for contour in question_bubbles:
                x, y, w, h = cv.boundingRect(contour)
                if np.absolute(expected_x - x) < self.bubble_width/2:
                    supplemented_bubbles.append(contour)
                    foundbubble = True
                    if self.debug_mode:
                        print(f'rescuing bubble: x:{x} y:{y} w:{w} h:{h}')
                    break
            #went through all contours and didn't find one that was around expected x so we try to look at see if it wasn't picked up as a bubble.
            if foundbubble == False:
                contour_to_rescue = self.find_contour_by_position(nonbubblecontours, expected_x, expected_y, self.bubble_width, self.bubble_height)
                if contour_to_rescue is not None:
                    x, y, w, h = cv.boundingRect(contour_to_rescue)
                    if self.debug_mode:
                        print(f'rescuing contour: x:{x} y:{y} w:{w} h:{h}')
                    supplemented_bubbles.append(contour_to_rescue)
        return supplemented_bubbles

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
        if len(question) != self.bubbles_per_q:
            unsure = True
            self.handle_unsure_question(question_num, group_num, box)


        bubble_pcts=[]
        for (i, bubble) in enumerate(question):
            percent_marked = self.get_percent_marked(bubble, box)
            bubble_pcts.append(percent_marked)
            sure = False
            if percent_marked > 0.4:
                bubbled += str(i)
                sure = True
            elif percent_marked > 0.2 and unsure == False:
                unsure = True
                self.handle_unsure_question(question_num, group_num, box)
                #bubbled = '?'
                #break
            with open('meow.txt', 'a') as file:
                file.write(f'{sure},{round(percent_marked,3)}\n') 
        if self.multiple_responses == False:
            # find the darkest bubble in a question
            if len(bubble_pcts) > 0:
                darkest_index = np.argmax(bubble_pcts)
                if bubble_pcts[darkest_index] > 0.66:
                    bubbled = str(darkest_index)
        

        # Add image slice if program running in verbose mode and image slice not
        # already added.
        if self.verbose_mode and unsure == False:
            self.add_image_slice(question_num, group_num, box)
        self.bubbled[question_num] = self.format_answer(bubbled)
    
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
                elif has_slash:
                    bbld += str(int(ans) - 2)
                else:
                    bbld += str(int(ans) - 1)

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
            scale = .6
            M = cv.moments(bubble)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            centerbubble = bubble - [cx, cy]
            scaledbubble = centerbubble * scale
            scaledbubble = (scaledbubble + [cx, cy]).astype(np.int32)
            shrunken_bubbles.append(scaledbubble)

        if self.debug_mode:
            #show the detected bubbles in green.
            colorbox = cv.cvtColor(box, cv.COLOR_GRAY2BGR)
            cv.drawContours(colorbox, shrunken_bubbles, -1, (0,255,0), 2)
            cv.imshow('', colorbox)
            cv.waitKey()
            
        return shrunken_bubbles


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
                # box is passed so we can draw the contours during debugging
                clean_question = self.compress_overlapping_bubbles(question_sorted, box)
                if len(clean_question) < self.bubbles_per_q and self.orientation == "left-to-right" : #and len(clean_question) > 0:
                    clean_question = self.rescue_expected_bubbles(qgroup, clean_question, nonbubbles)
                clean_question = self.shrink_bubbles(clean_question, box)
                if len(clean_question) > 0:
                    self.grade_question(clean_question, question_num, i, box)

    def grade(self, page_number):
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
        if gradable_box is None:
            data['status'] = 2
            data['error'] = f'We were unable to find any boxes on page {page_number}.'
            return data
        for (treatment) in enumerate(['','erase_lines']):
            self.init_result_structures()
            if treatment == 'erase_lines':
                gradable_box = self.erase_lines(gradable_box)

            bubbles, nonbubbles = self.get_bubbles(gradable_box)
            self.grade_bubbles(bubbles, nonbubbles, gradable_box)
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

