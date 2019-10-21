#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
from kobuki_msgs.msg import BumperEvent

PI = 3.1415926535897

collision = False

def processBump(data):
    print ("hit object")
    global collision
    if (data.state == BumperEvent.PRESSED):
        collision = True

def publisher():
    pub = rospy.Publisher('mobile_base/commands/velocity', Twist)
    sub = rospy.Subscriber('mobile_base/events/bumper', BumperEvent, processBump)
    rospy.init_node('Walker', anonymous=True)
    rate = rospy.Rate(10) #10hz
    while not rospy.is_shutdown():
        desired_velocity = Twist()
        desired_velocity.linear.x = 0.2 # Forward with 0.2 m/sec.
        for i in range (50):
            if(collision == True):
                print('Reversing and stopping')
                desired_velocity.angular.z = 0
                desired_velocity.linear.x = -0.2
                for i in range(20):
                    pub.publish(desired_velocity)
                break;
            pub.publish(desired_velocity)
            rate.sleep()
        if(collision == True):
            break;
        desired_velocity.linear.x = 0
        desired_velocity.angular.z = PI / 2
        for i in range (10):
            pub.publish(desired_velocity)
            rate.sleep()

if __name__ == "__main__":
	try:
		publisher()
	except rospy.ROSInterruptException:
		pass
