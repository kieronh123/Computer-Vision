#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
PI = 3.1415926535897

def publisher():
	pub = rospy.Publisher('mobile_base/commands/velocity', Twist)
	rospy.init_node('Walker', anonymous=True)
	rate = rospy.Rate(10) #10hz
	while not rospy.is_shutdown():
		desired_velocity = Twist()
		desired_velocity.linear.x = 0.2 # Forward with 0.2 m/sec.
		for i in range (10):
			pub.publish(desired_velocity)
			rate.sleep()
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
