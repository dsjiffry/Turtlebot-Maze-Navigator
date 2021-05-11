#!/usr/bin/env python

import rospy
import sys
import time
from numpy import inf
from std_msgs.msg import String
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from tf.msg import tfMessage

currentDirection = directiontoTurn = "forward"
subscription = turnSubscription = pub = move_cmd = None
numberOfSlits = right = left = 0
mainWall = "right"
isTurning = False


def lidarCallback(data):
    global currentDirection, mainWall, subscription, numberOfSlits, right, left
    subscription.unregister()

    forward = data.ranges[0]
    left = data.ranges[89]
#    leftBack = data.ranges[109]
    leftBack = data.ranges[102]
    backward = data.ranges[179]
    rightForward = data.ranges[279]
  #  rightForward = data.ranges[289]
 #   rightBack = data.ranges[249]
    rightBack = data.ranges[265]
    right = data.ranges[269]

    rospy.loginfo('Forward: %f', forward)
    rospy.loginfo('Left: %f', left)
    rospy.loginfo('Left Back: %f', leftBack)
    rospy.loginfo('Backward: %f', backward)
    rospy.loginfo('Right Forward: %f', rightForward)
    rospy.loginfo('Right: %f', right)
    rospy.loginfo('Right Back: %f', rightBack)
    rospy.loginfo('-----------------------------------',)

    moveRobot("stop")

    if left  == inf and right == inf and forward == inf:
        if numberOfSlits == 1:
            executeFirstPath()
        elif numberOfSlits == 2:
            executeSecondPath()
        elif numberOfSlits == 3:
            executeThirdPath()
        sys.exit(0)


    if mainWall == "right":
        if rightBack > 0.6 and currentDirection != "right":
            if rightForward < 0.5:
                numberOfSlits = numberOfSlits + 1
                moveRobot("forward")
                subscription = rospy.Subscriber(
                    'scan', LaserScan, lidarCallback)
                return
            turn("right")
            moveRobot("forward")
            currentDirection = "right"

        elif forward > 0.2:
            moveRobot("forward")

        elif forward <= 0.2:
            if currentDirection == "right":
                turn("forward")
                currentDirection = "forward"
            else:
                turn("backward")
                mainWall = "left"

    else:
        if leftBack > 0.6 and currentDirection != "left":
            turn("left")
            moveRobot("forward")
            currentDirection = "left"

        elif forward > 0.2:
            moveRobot("forward")

        elif forward <= 0.2:
            if currentDirection == "left":
                turn("backward")
                currentDirection = "backward"
                moveRobot("forward")
                time.sleep(0.1)
            else:
                turn("forward")
                mainWall = "right"

    subscription = rospy.Subscriber('scan', LaserScan, lidarCallback)


def turnCallback(data):
    global isTurning, directiontoTurn, turnSubscription
    reading = data.transforms[0].transform.rotation.w

    if directiontoTurn == "forward":
        if reading >= 0.99999:
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
    global pub, move_cmd, right, left
    if command == "forward":
        move_cmd.linear.x = 0.22
        move_cmd.angular.z = 0.0
    elif command == "stop":
        move_cmd.linear.x = 0.0
        move_cmd.angular.z = 0.0
    elif command == "right":
        move_cmd.linear.x = 0.0
        move_cmd.angular.z = -0.1
    elif command == "left" or command == "backward":
        move_cmd.linear.x = 0.0
        move_cmd.angular.z = 0.1
    pub.publish(move_cmd)
    time.sleep(0.01)

def executeFirstPath():
    global pub, move_cmd
    moveRobot("stop")    
    moveRobot("forward")
    time.sleep(9.0909)
    moveRobot("stop")
    move_cmd.linear.x = 0.22
    move_cmd.angular.z = 0.21
    pub.publish(move_cmd)
    time.sleep(15)
    moveRobot("stop")

def executeThirdPath():
    global pub, move_cmd
    moveRobot("stop")    
    moveRobot("forward")
    time.sleep(9.0909)
    moveRobot("stop")
    move_cmd.linear.x = 0.22
    move_cmd.angular.z = -0.21
    pub.publish(move_cmd)
    time.sleep(15)
    moveRobot("stop")

def executeSecondPath():
    global pub, move_cmd
    moveRobot("stop")    
    moveRobot("forward")
    time.sleep(13.6363)
    moveRobot("stop")
    move_cmd.linear.x = 0.22
    move_cmd.angular.z = 0.21
    pub.publish(move_cmd)
    time.sleep(7.5)
    move_cmd.linear.x = 0.22
    move_cmd.angular.z = -0.21
    pub.publish(move_cmd)
    time.sleep(7.5)
    moveRobot("stop")

def listener():

    rospy.init_node('maze_solver', anonymous=True)

    global subscription, move_cmd, pub
    move_cmd = Twist()
    pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)
    subscription = rospy.Subscriber('scan', LaserScan, lidarCallback)

    # spin() keeps python from exiting
    rospy.spin()


if __name__ == '__main__':
    listener()
