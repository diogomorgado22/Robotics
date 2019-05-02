#!/usr/bin/env python


import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Quaternion
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import tf
from tf.transformations import euler_from_quaternion, quaternion_from_euler
import math
import random
import numpy as np


class pioneer(object):

	def __init__(self):

		rospy.init_node('ListenerTalker',anonymous=False)
		rospy.Subscriber('/RosAria/pose',Odometry,self.odom_callback,queue_size=1)
		#rospy.Subscriber("/scan", LaserScan, self.laser_callback,queue_size=1)
		# setup publisher to later on move the pioneer base
		self.pub_move = rospy.Publisher('/RosAria/cmd_vel', Twist, queue_size=1)
		self.positionx=0.0
		self.positiony=0.0
		self.yaw=0.0
		self.vmax=0.3
		self.v=0
		self.flag1=0
		self.flag2=1
		self.flag3=1
		self.xref=0
		self.yref=0
		self.teta=0

	def odom_callback(self, data):

		quaternion =(data.pose.pose.orientation.x, data.pose.pose.orientation.y, data.pose.pose.orientation.z, data.pose.pose.orientation.w)
		euler = euler_from_quaternion(quaternion)
		#roll = euler[0]
		#pitch = euler[1]
		self.yaw =euler[2]
		self.positionx=data.pose.pose.position.x
		self.positiony=data.pose.pose.position.y

	#def laser_callback(self, msg):
	#def correct(self):
	#	dx=self.posx_ref-self.positionx
	#	dy=self.posy_ref-self.positiony
	#	d=math.sqrt(dx^2+dy^2)
	#	woff=0.00645771823
	#	self.x=self.positionx-(self.positiony*math.sin(woff*d))
	#	self.y=self.positiony+(self.positionx*math.sin(woff*d))
	#	self.teta=self.yaw+woff
	def setcontrol(self):
		xdif=self.xref-self.positionx
		print('xdif =',xdif)
		ydif=self.yref-self.positiony
		print('ydif =',ydif)
		e=math.sqrt(xdif**2+ydif**2)
		print('e = ', e)
		phi=math.atan2(ydif,xdif)
		print('phi = ', phi)
		alfa=phi-self.yaw
		print('alfa = ', alfa)
		self.v=self.vmax
		print('v =',self.v)

		self.w= self.vmax*(((1+self.k2)*(math.tanh(self.k1*e)/e)*math.sin(alfa))+ (self.k3*math.tanh(alfa)))
		print('w =',self.w)
	
	def move_forward(self):

		twist_msg = Twist()
      
		twist_msg.linear.x = self.v
		twist_msg.linear.y = 0.0
		twist_msg.linear.z = 0.0
       
		twist_msg.angular.x = 0.0
		twist_msg.angular.y = 0.0
		twist_msg.angular.z = self.w

        # publish Twist message to move the robot
		self.pub_move.publish(twist_msg)
	
	def move_left(self):

		twist_msg = Twist()
      
		twist_msg.linear.x = 0.0
		twist_msg.linear.y = 0.0
		twist_msg.linear.z = 0.0
       
		twist_msg.angular.x = 0.0
		twist_msg.angular.y = 0.0
		twist_msg.angular.z = self.w
        # publish Twist message to move the robot
		self.pub_move.publish(twist_msg)

	def move_right(self):

		twist_msg = Twist()
      
		twist_msg.linear.x = 0.0
		twist_msg.linear.y = 0.0
		twist_msg.linear.z = 0.0
       
		twist_msg.angular.x = 0.0
		twist_msg.angular.y = 0.0
		twist_msg.angular.z = -self.w

        # publish Twist message to move the robot
		self.pub_move.publish(twist_msg)

	def trajectx(self):
		
		if self.positionx<self.xref:
			self.setcontrol()
			self.move_forward()
		else:
			while self.yaw<self.teta:
				self.w=0.2
				self.move_left()
			self.flag1=1
			self.flag2=0

	def trajecty(self):
		
		if self.positiony<self.yref:
			self.setcontrol()
			self.move_forward()
		else:
			while self.yaw>self.teta:
				self.w=0.2
				self.move_right()
			self.flag2=1
			self.flag3=0

	def second_traject(self):

		if self.positiony<3.8:
			self.w=0
			self.move_forward()
		else:
			while self.yaw>0.2:
				self.w=-0.2
				self.move_right()
			self.flag2=1
			self.flag3=0

	def third_traject(self):
		
		if self.positionx<18:
			self.w=0
			self.move_forward()
		else:
			self.flag3=1


	def move(self):
		while not rospy.is_shutdown():
	        # base needs this msg to be published constantly for the robot to keep moving so we publish in a loop

	        # while the distance from the robot to the walls is bigger than the defined threshold keep moving forward
			if self.flag1==0:
				self.xref=4.2
				self.yref=0
				self.teta=1.43
				self.k1=0.5
				self.k2=0
				self.k3=0
				self.trajectx()
							
			if self.flag2==0:
				self.xref=4.4
				self.yref=3.7
				self.teta=0.2
				self.k1=0.5
				self.k2=0
				self.k3=0
				self.trajecty()
			

	        # sleep for a small amount of time
			rospy.sleep(0.1)

def main():

	# create object of the class pioneer
	obj = pioneer()
    # call move method of class pioneer
	obj.move()


