#Simulation for distributed algorithms
__author__ = 'M. Tosun & C. U. Ileri'

import simpy
import random
import networkx as nx


class MsgManager(object):
	def __init__(self,env,nodes):
		self.env = env
		self.action1 = env.process(self.timeRun())
		self.action1 = env.process(self.mailboxRun())
		self.nodes = nodes
		self.messages = {}
		self.delayTime = 1
		self.mailbox = simpy.Container(env, capacity=1000, init=0)
		self.totalMessageSent = 0

	def timeRun(self):
		while True:
			yield self.env.timeout(1)  # Go to the next time step or wait for a message
			msgToBeSent = []

			# Find messages to be sent NOW
			if self.env.now in self.messages:
				msgToBeSent = self.messages[self.env.now]

			for msg in msgToBeSent:                
				if msg['receiver'] == 255:
					keys = list(self.nodes[msg['sender']].neighbors.keys())
					random.shuffle(keys)
					for n in keys:
						self.forward_message(n,msg)                      
				else:
					self.forward_message(msg['receiver'],msg)

            # Delete SENT messages
			if self.env.now in self.messages:
				del(self.messages[self.env.now])
                
	
	def mailboxRun(self):
		while True:
			yield self.mailbox.get(1)
			msgToBeSent = []
			# Find messages to be sent NOW
			if self.env.now in self.messages:
				msgToBeSent = self.messages[self.env.now]

			for msg in msgToBeSent:                
				if msg['receiver'] == 255:
					for n in self.nodes[msg['sender']].neighbors.keys():
						self.forward_message(n,msg)                      
				else:
					self.forward_message(msg['receiver'],msg)

            # Delete SENT messages
			if self.env.now in self.messages:
				del(self.messages[self.env.now])

	def addToMessageQueue(self,msg):
		if msg['type'] == 'TIMER':
			timestamp = self.env.now + msg['time']
			msg['type'] = 'TIMEOUT'
		else:
			self.totalMessageSent += 1
			if msg['type'] == 'ROUND':
				timestamp = self.env.now
			else:
				timestamp = self.env.now + self.delayTime

		if timestamp not in self.messages:
			self.messages[timestamp] = []
            
		self.messages[timestamp].append(msg)
		self.mailbox.put(1) 

	def forward_message(self, n, msg):
		self.nodes[n].messages.append(msg)
		self.nodes[n].mailbox.put(1)   

class Node(object):
	def __init__(self,id,env,msgManager):
		self.env = env
		self.id = id
		self.msgManager = msgManager
		self.mailbox = simpy.Container(env, capacity=1000, init=0)
		self.messages = []
		self.neighbors = {}
		self.action = env.process(self.run())

	def run(self):
		print('running')



	def sendMessageTo(self,to,msgdict):
		msgdict['sender'] = self.id
		msgdict['receiver'] = to
		self.msgManager.addToMessageQueue(msgdict)

	def sendMessage(self,msgdict):
		self.sendMessageTo(255,msgdict)

	def receiveMessage(self):
		return self.messages.pop(0)

	def addNeighbor(self,id,neighborDict):
		self.neighbors[id] = neighborDict

	def setTimer(self,name,time):
		self.sendMessageTo(self.id,{'type':'TIMER','name':name,'time':time})



class System(object):
	def __init__(self,NodeObject=Node,nodeCount=None,nxGraph=None,roundInterval=None):
		self.env = simpy.Environment()
		self.nodes = {}
		self.NodeObject = NodeObject
		self.msgManager = MsgManager(self.env,self.nodes)

		if roundInterval != None:
			self.roundInterval = roundInterval
			self.round = 0
			self.action = self.env.process(self.syncRound())

		if nxGraph == None:
			self.nodeCount = nodeCount
			for i in range(nodeCount):
				self.addNode(i)
		else:
			self.nxGraph = nxGraph
			for i in self.nxGraph.nodes():
				self.addNode(i)
			for (id1,id2) in self.nxGraph.edges():
				self.addEdge(id1,id2)
				self.addEdge(id2,id1)

		self.msgManager.nodes = self.nodes

	def addNode(self,id):
		n = self.NodeObject(id,self.env,self.msgManager)
		self.nodes[id]=n
		
	def addEdge(self,id1,id2):
		self.nodes[id1].addNeighbor(id2,{})

	def syncRound(self):
		while True:
			self.round += 1
			keys = list(self.nodes.keys())
			random.shuffle(keys)
			for i in keys:
				self.msgManager.addToMessageQueue({'type': 'ROUND', 'round': self.round,'receiver': i,'sender':-1})
			yield self.env.timeout(self.roundInterval) 
	


