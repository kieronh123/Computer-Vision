#!/usr/bin/env python
from __future__ import division
import cv2
import numpy as np
import rospy
import sys

from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

global sensitivity
sensitivity = 0


class colourIdentifier():
    def __init__(self):
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber("camera/rgb/image_raw", Image, self.callback)

    def callback(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
            hsv_green_lower = np.array([60 - sensitivity,100,100])
            hsv_green_upper = np.array([60 + sensitivity,255,255])
            hsv_red_lower = np.array([0,50,50])
            hsv_red_upper = np.array([10,255,255])
            hsv_blue_lower = np.array([110,50,50])
            hsv_blue_upper = np.array([130,255,255])
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

            image_mask = cv2.inRange(hsv,hsv_green_lower,hsv_green_upper)
            image_mask2 = cv2.inRange(hsv,hsv_red_lower,hsv_red_upper)
            image_mask3 = cv2.inRange(hsv,hsv_blue_lower,hsv_blue_upper)
            temp_mask = cv2.bitwise_or(image_mask,image_mask2)
            maskCombined = cv2.bitwise_or(image_mask3,temp_mask)
            image_res = cv2.bitwise_and(cv_image,cv_image, mask= maskCombined)
        except CvBridgeError as e:
            print(e)

        cv2.namedWindow('Camera_Feed')
        cv2.imshow("Camera_Feed", cv_image)
        cv2.imshow('image_mask',maskCombined)
        cv2.imshow('res',image_res)
        cv2.waitKey(3)


def main(args):
    cI = colourIdentifier()
    rospy.init_node("colourIdentifier", anonymous=True)
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main(sys.argv)
