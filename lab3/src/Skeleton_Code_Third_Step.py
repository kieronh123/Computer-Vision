#!/usr/bin/env python

from __future__ import division
import cv2
import numpy as np
import rospy
import sys

from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from std_msgs.msg import String

class colourIdentifier():

    def __init__(self):
        # Initialise a publisher to publish messages to the robot base
        self.message_pub = rospy.Publisher('messages', String, queue_size = 10)
        # We covered which topic receives messages that move the robot in the 2nd Lab Session


        # Initialise any flags that signal a colour has been detected in view
        self.green_detected = False
        self.blue_detected = False
        # Initialise some standard movement messages such as a simple move forward and a message with all zeroes (stop)

        # Remember to initialise a CvBridge() and set up a subscriber to the image topic you wish to use
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber("camera/rgb/image_raw", Image, self.callback)
        # We covered which topic to subscribe to should you wish to receive image data


    def callback(self, data):
        # Convert the received image into a opencv image
        # But remember that you should always wrap a call to this conversion method in an exception handler
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
            # Set the upper and lower bounds for the two colours you wish to identify

        except CvBridgeError as e:
            print(e)
        # Find the contours that appear within the certain colours mask using the cv2.findContours() method
        # For <mode> use cv2.RETR_LIST for <method> use cv2.CHAIN_APPROX_SIMPLE
        hsv_green_lower = np.array([60,100,100])
        hsv_green_upper = np.array([60,255,255])
        hsv_blue_lower = np.array([110,50,50])
        hsv_blue_upper = np.array([130,255,255])
        # Convert the rgb image into a hsv image
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        # Filter out everything but particular colours using the cv2.inRange() method
        image_mask_green = cv2.inRange(hsv,hsv_green_lower,hsv_green_upper)
        image_mask_blue = cv2.inRange(hsv,hsv_blue_lower,hsv_blue_upper)
        # To combine the masks you should use the cv2.bitwise_or() method
        # You can only bitwise_or two image at once, so multiple calls are necessary for more than two colours
        maskCombined = cv2.bitwise_or(image_mask_green,image_mask_blue)
        # Apply the mask to the original image using the cv2.bitwise_and() method
        # As mentioned on the worksheet the best way to do this is to bitwise and an image with itself and pass the mask to the mask parameter
        # As opposed to performing a bitwise_and on the mask and the image.
        image_res = cv2.bitwise_and(cv_image,cv_image, mask= maskCombined)


        contours_green, hierarchy = cv2.findContours(image_mask_green.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours_blue, hierarchy = cv2.findContours(image_mask_blue.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        #cv2.namedWindow('Camera_Feed')
#        cv2.imshow("Camera_Feed", cv_image)
#        cv2.imshow('image_mask',image_mask_green)
#        cv2.imshow('res',image_res)
        #cv2.waitKey(3)

        # Loop over the contours
        # There are a few different methods for identifying which contour is the biggest
        # Loop throguht the list and keep track of whioch contour is biggest or
        # Use the max() method to find the largest contour

        if len(contours_green) > 0:
            cgreen = max(contours_green, key = cv2.contourArea)
            M = cv2.moments(cgreen)

            # M = cv2.moments(c)
            # cx, cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
            cxgreen, cygreen = int(M['m10']/M['m00']), int(M['m01']/M['m00'])

            #Check if the area of the shape you want is big enough to be considered
            # If it is then change the flag for that colour to be True(1)
            if cv2.contourArea(cgreen) > 1000:

                self.green_detected = True
                # draw a circle on the contour you're identifying as a blue object as well
                #COLOUR_BLUE = np.array([0,0,255])
                COLOUR_GREEN = np.array([0,255,0])
                #COLOUR_RED = np.array([255,0,0])
                #cv2.circle(cv_image,(cx,cy), 50, COLOUR_BLUE, 1)
                cv2.circle(cv_image,(cxgreen,cygreen), 25, COLOUR_GREEN, 1)
                #cv2.circle(cv_image,(cx,cy), 50, COLOUR_RED, 1)
                # cv2.circle(<image>,(<center x>,<center y>),<radius>,<colour (rgb tuple)>,<thickness (defaults to 1)>)
                # Then alter the values of any flags
        else:
            self.green_detected = False

        if len(contours_blue) > 0:
            cblue = max(contours_blue, key = cv2.contourArea)
            M = cv2.moments(cblue)
            # M = cv2.moments(c)
            # cx, cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
            cxblue, cyblue = int(M['m10']/M['m00']), int(M['m01']/M['m00'])




            #Check if the area of the shape you want is big enough to be considered
            # If it is then change the flag for that colour to be True(1)
            if cv2.contourArea(cblue) > 1000:
                self.message_pub.publish('blue detected')
                self.blue_detected = True
                # draw a circle on the contour you're identifying as a blue object as well
                #COLOUR_BLUE = np.array([0,0,255])
                COLOUR_GREEN = np.array([0,255,0])
                #COLOUR_RED = np.array([255,0,0])
                #cv2.circle(cv_image,(cx,cy), 50, COLOUR_BLUE, 1)
                cv2.circle(cv_image,(cxblue,cyblue), 25, COLOUR_GREEN, 1)
                #cv2.circle(cv_image,(cx,cy), 50, COLOUR_RED, 1)
                # cv2.circle(<image>,(<center x>,<center y>),<radius>,<colour (rgb tuple)>,<thickness (defaults to 1)>)
                # Then alter the values of any flags
        else:
            self.blue_detected = False

        if self.green_detected==True:
                self.message_pub.publish('green detected')
        if self.blue_detected==True:
                self.message_pub.publish('blue detected')



            #Show the resultant images you have created. You can show all of them or just the end result if you wish to.
        cv2.namedWindow('Camera_Feed')
        cv2.imshow("Camera_Feed", cv_image)
        cv2.imshow('image_mask',maskCombined)
        cv2.imshow('res',image_res)
        cv2.waitKey(3)

def main(args):
    rospy.init_node("colourIdentifier", anonymous=True)
    cI = colourIdentifier()

    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main(sys.argv)
