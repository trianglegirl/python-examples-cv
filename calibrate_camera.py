#####################################################################

# Example : perform intrinsic calibration of a  connected camera

# Author : Toby Breckon, toby.breckon@durham.ac.uk

# Copyright (c) 2018 Department of Computer Science,
#                    Durham University, UK
# License : LGPL - http://www.gnu.org/licenses/lgpl.html

# Acknowledgements:

# http://opencv-python-tutroals.readthedocs.org/en/latest/ \
# py_tutorials/py_calib3d/py_table_of_contents_calib3d/py_table_of_contents_calib3d.html

# http://docs.ros.org/electric/api/cob_camera_calibration/html/calibrator_8py_source.html

#####################################################################

import cv2
import sys
import numpy as np

#####################################################################

keep_processing = True;
camera_to_use = 0; # 0 if you have no built in webcam, 1 otherwise

#####################################################################

#  define video capture object

cam = cv2.VideoCapture();

# define display window names

windowName = "Camera Input"; # window name
windowNameU = "Undistored (calibrated) Camera"; # window name

#####################################################################

# perform intrinsic calibration (removal of image distortion in each image)

do_calibration = False;
termination_criteria_subpix = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# set up a set of real-world "object points" for the chessboard pattern

patternX = 6;
patternY = 9;
square_size_in_mm = 40;

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)

objp = np.zeros((patternX*patternY,3), np.float32)
objp[:,:2] = np.mgrid[0:patternX,0:patternY].T.reshape(-1,2)
objp = objp * square_size_in_mm;

# create arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

#####################################################################

# count number of chessboard detection (across both images)
chessboard_pattern_detections = 0;

print()
print("--> hold up chessboard")
print("press c : to continue to calibration")

#####################################################################

# open connected camera

if cam.open(camera_to_use):

    while (not(do_calibration)):

        # grab frames from camera (to ensure best time sync.)

        cam.grab();
        ret, frame = cam.retrieve();

        # convert to grayscale

        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY);

        # Find the chess board corners in the image
        # (change flags to perhaps improve detection ?)

        ret, corners = cv2.findChessboardCorners(gray, (patternX,patternY),None, cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_FAST_CHECK | cv2.CALIB_CB_NORMALIZE_IMAGE);

        # If found, add object points, image points (after refining them)

        if (ret == True):

            chessboard_pattern_detections += 1;

            # add object points to global list

            objpoints.append(objp);

            # refine corner locations to sub-pixel accuracy and then

            corners_sp = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),termination_criteria_subpix);
            imgpoints.append(corners_sp);

            # Draw and display the corners

            drawboard = cv2.drawChessboardCorners(frame, (patternX,patternY), corners_sp,ret);

            text = 'detected: ' + str(chessboard_pattern_detections);
            cv2.putText(drawboard, text, (10,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2, 8);

            cv2.imshow(windowName,drawboard);
        else:
            text = 'detected: ' + str(chessboard_pattern_detections);
            cv2.putText(frame, text, (10,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2, 8);

            cv2.imshow(windowName,frame);

        # start the event loop

        key = cv2.waitKey(100) & 0xFF; # wait 500ms between frames
        if (key == ord('c')):
            do_calibration = True;

else:
    print("Cannot open connected camera.")

#####################################################################

# perform calibration on both cameras - uses [Zhang, 2000]

print("START - intrinsic calibration ...");

ret, mtx, dist, rvecs, tvecs= cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None);

print("FINISHED - intrinsic calibration");

print("Intrinsic Distortion Co-effients - from intrinsic calibration:");
print(dist);

#####################################################################

# perform undistortion (i.e. calibration) of the images

keep_processing = True;

print();
print("-> performing undistortion");
print("press x : to exit")

while (keep_processing):

    # grab frames from camera (to ensure best time sync.)

    cam.grab();
    ret, frame = cam.retrieve();

    undistorted = cv2.undistort(frame, mtx, dist, None, None)

    # display both images

    cv2.imshow(windowName,frame);
    cv2.imshow(windowNameU,undistorted);

    # start the event loop - essential

    key = cv2.waitKey(40) & 0xFF; # wait 40ms (i.e. 1000ms / 25 fps = 40 ms)

    if (key == ord('x')):
        keep_processing = False;

#####################################################################

# close all windows and cams.

cv2.destroyAllWindows()

#####################################################################
