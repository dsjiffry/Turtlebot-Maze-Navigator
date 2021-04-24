#!/usr/bin/env python

import rospy
import time
from std_msgs.msg import String
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from tf.msg import tfMessage

currentDirection = directiontoTurn = "forward"
subscription = turnSubscription = pub = move_cmd = None
mainWall = "right"
isTurning = False

def lidarCallback(data):
	global currentDirection, mainWall,subscription
	subscription.unregister()
		
	forward = data.ranges[0]
	left = data.ranges[109]
	backward = data.ranges[179]
	right = data.ranges[249]

	rospy.loginfo('Forward: %f', forward)
	rospy.loginfo('Left: %f', left)
	rospy.loginfo('Backward: %f', backward)
	rospy.loginfo('Right: %f', right)
	rospy.loginfo('-----------------------------------',)

	moveRobot("stop")

	if mainWall == "right":
		if right > 0.6 and currentDirection != "right": 
			turn("right")
			moveRobot("forward")
			currentDirection = "right"

		elif forward > 0.3:
			moveRobot("forward")
			
		elif forward <= 0.3:
			if currentDirection == "right":
				turn("forward")
				currentDirection = "forward"
			else:
				turn("backward")
				mainWall = "left"
	
	else:
		if left > 0.6 and currentDirection != "left": 
			turn("left")
			moveRobot("forward")
			currentDirection = "left"

		elif forward > 0.3:
			moveRobot("forward")
			
		elif forward <= 0.3:
			if currentDirection == "left":
				turn("backward")
				currentDirection = "backward"
			else:
				turn("forward")
				mainWall = "right"


	subscription = rospy.Subscriber('scan', LaserScan, lidarCallback)



def turnCallback(data):
	global isTurning, directiontoTurn, turnSubscription
	reading = data.transforms[0].transform.rotation.w

	if directiontoTurn == "forward":
		if reading >= 0.9990:
			moveRobot("stop")
			isTurning = False
			turnSubscription.unregister()

	elif directiontoTurn == "right" or directiontoTurn == "left":
		if reading >= 0.7040 and reading <= 0.7060:
			moveRobot("stop")
			isTurning = False
			turnSubscription.unregister()

	elif directiontoTurn == "backward":
		if reading >= -0.0010 and reading <= 0.0010:
			moveRobot("stop")
			isTurning = False
			turnSubscription.unregister()


def turn(direction):
	global isTurning, directiontoTurn, turnSubscription, currentDirection
	isTurning = True
	directiontoTurn = direction

	turnSubscription = rospy.Subscriber('tf', tfMessage, turnCallback)
	if direction == "forward":
		if currentDirection == "right":
			moveRobot("left")
		else:
			moveRobot("right")
	elif direction == "backward":
		if currentDirection == "left":
			moveRobot("right")
		else:
			moveRobot("left")	
	else:
		moveRobot(direction)

	while isTurning:
		time.sleep(0.1)
	


	

	




def moveRobot(command):
	global pub, move_cmd
	if command == "forward":
		move_cmd.linear.x = 0.22
		move_cmd.angular.z = 0.0
	elif command == "stop":
		move_cmd.linear.x = 0.0
		move_cmd.angular.z = 0.0
	elif command == "right":
		move_cmd.linear.x = 0.0
		move_cmd.angular.z = -0.10
	elif command == "left" or command == "backward":
		move_cmd.linear.x = 0.0
		move_cmd.angular.z = 0.10
	pub.publish(move_cmd)
	time.sleep(0.01)

def listener():

	rospy.init_node('maze_solver', anonymous=True)

	global subscription, move_cmd, pub
	move_cmd = Twist()
	pub = rospy.Publisher('cmd_vel',Twist,queue_size=1)
	subscription = rospy.Subscriber('scan', LaserScan, lidarCallback)

	# spin() keeps python from exiting 
	rospy.spin()

if __name__ == '__main__':
	listener()



