import base64
import math

import cv2 as cv
from imutils.perspective import four_point_transform
import numpy as np


def get_threshold(im):
    """
    Performs a Gaussian blur and threshold on an image for image processing.
    Returns the blurred and thresholded image.

    Args:
        im (numpy.ndarray): An ndarray representing an image.

    Returns:
        threshold (numpy.ndarray): An ndarray representing the blurred and
            thresholded image.

    """
    blurred = cv.GaussianBlur(im, (1, 1), 0)
    blurred = cv.bilateralFilter(blurred,5,50,50)
    threshold = cv.adaptiveThreshold(blurred,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv.THRESH_BINARY_INV, 91, 9)
    return threshold

def get_transform(contour, im):
    """
    Returns the portion of an image bounded by a contour.

    Args:
        contour (numpy.ndarray): An ndarray representing a contour.
        im (numpy.ndarray): An ndarray representing an image.

    Returns:
        numpy.ndarray: An ndarray representing the portion of the image bounded
            by the contour.

    """
    peri = cv.arcLength(contour, True)
    epsilon_factor = 0.001
    approx = cv.approxPolyDP(contour, epsilon_factor * peri, True)
    #tries various epsilons to try to identify a rectangle (4 sides)
    while approx.size != 8:
        approx = cv.approxPolyDP(contour, epsilon_factor * peri, True)
        epsilon_factor += 0.001
        if epsilon_factor > 1: break

    if approx.size == 8:
        return four_point_transform(im, approx.reshape(4, 2))
    else:
        #failed to transform... just returns the untransformed image
        return im


def rotate_image(im, angle):
    """
    Rotates an image by a specified angle.

    Args:
        im (numpy.ndarray): An ndarray representing the entire test image.
        angle (int): The angle, in degrees, by which the image should be 
            rotated.

    Returns:
        numpy.ndarray: An ndarray representing the rotated test image.

    """
    w = im.shape[1]
    h = im.shape[0]
    rads = np.deg2rad(angle)

    # Calculate new image width and height.
    nw = abs(np.sin(rads) * h) + abs(np.cos(rads) * w)
    nh = abs(np.cos(rads) * h) + abs(np.sin(rads) * w)

    # Get the rotation matrix.
    rot_mat = cv.getRotationMatrix2D((nw * 0.5, nh * 0.5), angle, 1)

    # Calculate the move from old center to new center combined with the 
    # rotation.
    rot_move = np.dot(rot_mat, np.array([(nw - w) * 0.5, (nh - h) * 0.5, 0]))

    # Update the translation of the transform.
    rot_mat[0,2] += rot_move[0]
    rot_mat[1,2] += rot_move[1]

    return cv.warpAffine(im, rot_mat, (int(math.ceil(nw)), 
        int(math.ceil(nh))), flags=cv.INTER_LANCZOS4)


def encode_image(image):
    """
    Encodes a .png image into a base64 string.

    Args:
        image (numpy.ndarray): An ndarray representing an image.

    Returns:
        str: A base64 string encoding of the image.

    """
    if image is None:
        return None
    else:
        _, binary = cv.imencode('.png', image)
        encoded = base64.b64encode(binary)
        return encoded.decode('utf-8')
