from typing import Union
from pymygdala.concepts import Emotion, Goal, Belief, Relation

class Agent:
	"""
	self is the emotion agent class taking care of emotion management for one entity 

	:param name: The name of the agent to be created. self name is used as ref throughout the appraisal engine.
	:type name: str
	"""
	def __init__(self, name='agent'):
		self.name = name
		self.goals = []
		self.currentRelations: list[Relation] = []
		self.internalState = []
		self.gamygdalaInstance = None
		self.mapPAD = {}
		self.gain = 1
		self.mapPAD['distress']=[-0.61,0.28,-0.36]
		self.mapPAD['fear']=[-0.64,0.6,-0.43]
		self.mapPAD['hope']=[0.51,0.23,0.14]
		self.mapPAD['joy']=[0.76,.48,0.35]
		self.mapPAD['satisfaction']=[0.87,0.2,0.62]
		self.mapPAD['fear-confirmed']=[-0.61,0.06,-0.32]#defeated
		self.mapPAD['disappointment']=[-0.61,-0.15,-0.29]
		self.mapPAD['relief']=[0.29,-0.19,-0.28]
		self.mapPAD['happy-for']=[0.64,0.35,0.25]
		self.mapPAD['resentment']=[-0.35,0.35,0.29]
		self.mapPAD['pity']=[-0.52,0.02,-0.21]#regretful
		self.mapPAD['gloating']=[-0.45,0.48,0.42]#cruel
		self.mapPAD['gratitude']=[0.64,0.16,-0.21]#grateful
		self.mapPAD['anger']=[-0.51,0.59,0.25]
		self.mapPAD['gratification']=[0.69,0.57,0.63]#triumphant
		self.mapPAD['remorse']=[-0.57,0.28,-0.34]#guilty
	
	def addGoal(self, goal: Goal):
		self.goals.append(goal)
	
	def removeGoal(self, goalName: str) -> bool:
		for i in range(len(self.goals)):
			if self.goals[i].name == goalName:
				self.goals.pop(i)
				return True
		return False
	
	def hasGoal(self, goalName: str) -> bool:
		for i in range(len(self.goals)):
			if self.goals[i].name == goalName:
				return True
		return False
	
	def getGoalByName(self, goalName: str) -> Union[Goal, None]:
		for i in range(len(self.goals)):
			if self.goals[i].name == goalName:
				return self.goals[i]
		return None
	
	def setGain(self, gain: int):
		assert gain > 0 and gain  <= 20, 'Error: gain factor for appraisal integration must be between 0 and 20'
		self.gain = gain
	
	def appraise(self, belief: Belief):
		self.gamygdalaInstance.appraise(belief, self)

	def updateEmotionalState(self, emotion: Emotion):
		for i in range(len(self.internalState)):
			if self.internalState[i].name == emotion.name:
				#Appraisals simply add to the old value of the emotion
				#So repeated appraisals without decay will result in the sum of the appraisals over time
				#To decay the emotional state, call .decay(decayFunction), or simply use the facilitating function in Gamygdala setDecay(timeMS).
				self.internalState[i].intensity += emotion.intensity
				return
		#copy on keep, we need to maintain a list of current emotions for the state, not a list references to the appraisal engine
		self.internalState.append(Emotion(emotion.name, emotion.intensity))

	def getEmotionalState(self, useGain: bool) -> list[Emotion]:
		"""
		This function returns either the state as is (gain=false) or a state based on gained limiter (limited between 0 and 1), of which the gain can be set by using setGain(gain).
		A high gain factor works well when appraisals are small and rare, and you want to see the effect of these appraisals
		A low gain factor (close to 0 but in any case below 1) works well for high frequency and/or large appraisals, so that the effect of these is dampened.

		:param useGain: Whether to use the gain function or not.
		:type useGain: bool

		:return: An array of emotions.
		:rtype: list[Emotion]
		"""
		if useGain:
			gainState=[]
			for i in range(len(self.internalState)):
				gainEmo=(self.gain*self.internalState[i].intensity)/(self.gain*self.internalState[i].intensity+1)
				gainState.append(Emotion(self.internalState[i].name, gainEmo))
			return gainState
		else:
			return self.internalState

	def getPADState(self, useGain: bool) -> list[int]:
		"""
		This function returns a summation-based Pleasure Arousal Dominance mapping of the emotional state as is (gain=false), or a PAD mapping based on a gained limiter (limited between 0 and 1), of which the gain can be set by using setGain(gain).
		It sums over all emotions the equivalent PAD values of each emotion (i.e., [P,A,D]=SUM(Emotion_i([P,A,D])))), which is then gained or not.
		A high gain factor works well when appraisals are small and rare, and you want to see the effect of these appraisals.
		A low gain factor (close to 0 but in any case below 1) works well for high frequency and/or large appraisals, so that the effect of these is dampened.

		:param useGain: Whether to use the gain function or not.
		:type useGain: bool

		:return: An array of doubles with Pleasure at index 0, Arousal at index [1] and Dominance at index [2].
		:rtype: list[float]
		"""
		PAD=[0, 0, 0]
		for i in range(len(self.internalState)):
			PAD[0] += self.internalState[i].intensity*self.mapPAD[self.internalState[i].name][0]
			PAD[1] += self.internalState[i].intensity*self.mapPAD[self.internalState[i].name][1]
			PAD[2] += self.internalState[i].intensity*self.mapPAD[self.internalState[i].name][2]
		if useGain:
			PAD[0] = self.gain*PAD[0]/(self.gain*PAD[0]+1) if PAD[0]>=0 else -self.gain*PAD[0]/(self.gain*PAD[0]-1)
			PAD[1] = self.gain*PAD[1]/(self.gain*PAD[1]+1) if PAD[1]>=0 else -self.gain*PAD[1]/(self.gain*PAD[1]-1)
			PAD[2] = self.gain*PAD[2]/(self.gain*PAD[2]+1) if PAD[2]>=0 else -self.gain*PAD[2]/(self.gain*PAD[2]-1)
			return PAD
		else:
			return PAD

	def printEmotionalState(self, useGain: bool): 
		"""
		This function prints to the console either the state as is (gain=false) or a state based on gained limiter (limited between 0 and 1), of which the gain can be set by using setGain(gain).
		A high gain factor works well when appraisals are small and rare, and you want to see the effect of these appraisals
		A low gain factor (close to 0 but in any case below 1) works well for high frequency and/or large appraisals, so that the effect of these is dampened.

		:param useGain: Whether to use the gain function or not.
		:type useGain: bool
		"""
		output = self.name + ' feels '
		emotionalState=self.getEmotionalState(useGain)
		k = 0
		for i in range(len(emotionalState)):
			k += 1
			output+=emotionalState[i].name+" : "+str(emotionalState[i].intensity)+", "
		if k>0:
			print(output)

	def updateRelation(self, agentName: str, like: float):
		"""
		Sets the relation this agent has with the agent defined by agentName. If the relation does not exist, it will be created, otherwise it will be updated.

		:param agentName: The agent who is the target of the relation.
		:type agentName: str

		:param like: The relation (between -1 and 1).
		:type like: float
		"""
		if not self.hasRelationWith(agentName):
			#This relation does not exist, just add it.
			self.currentRelations.append(Relation(agentName,like))   
		else:
			#The relation already exists, update it.
			for i in range(len(self.currentRelations)):
				if self.currentRelations[i].agentName == agentName:
					self.currentRelations[i].like = like

	def hasRelationWith(self, agentName: str) -> bool:
		"""
		Checks if this agent has a relation with the agent defined by agentName.

		:param agentName: The agent who is the target of the relation.
		:type agentName: str

		:return: True if the relation exists, otherwise false.
		:rtype: bool
		"""
		return self.getRelation(agentName) is not None

	def getRelation(self, agentName: str) -> Union[Relation, None]:
		"""
		Returns the relation object this agent has with the agent defined by agentName.

		:param agentName: The agent who is the target of the relation.
		:type agentName: str

		:return: The given relation or None
		:rtype: Relation or None
		"""
		for i in range(len(self.currentRelations)):
			if self.currentRelations[i].agentName == agentName:
				return self.currentRelations[i]    
		return None


	def printAllRelations(self):
		for r in self.currentRelations:
			print(r)

	def printRelations(self, agentName: str):
		"""
		Returns the relation object this agent has with the agent defined by agentName.

		:param agentName: The agent who is the target of the relation will only be printed, or when omitted all relations are printed.
		:type agentName: str
		"""
		output = self.name + ' has the following sentiments:\n   '
		found=False
		for i in range(len(self.currentRelations)):
			if agentName is not None or self.currentRelations[i].agentName == agentName:
				for j in range(len(self.currentRelations[i].emotionList)):
					output += self.currentRelations[i].emotionList[j].name + '(' + self.currentRelations[i].emotionList[j].intensity+') ' 
					found = True
			output += ' for ' + self.currentRelations[i].agentName
			if i < len(self.currentRelations)-1:
				output+=', and\n   '
		if found:
			print(output)

	def decay(self, decayFunction: callable, deltaTime=None):
		"""
		This method decays the emotional state and relations according to the decay factor and function defined in gamygdala. 
		Typically this is called automatically when you use startDecay() in Gamygdala, but you can use it yourself if you want to manage the timing.
		This function is keeping track of the millis passed since the last call, and will (try to) keep the decay close to the desired decay factor, regardless the time passed
		So you can call this any time you want (or, e.g., have the game loop call it, or have e.g., Phaser call it in the plugin update, which is default now).
		Further, if you want to tweak the emotional intensity decay of individual agents, you should tweak the decayFactor per agent not the "frame rate" of the decay (as this doesn't change the rate).

		:param decayFunction: A reference to the decayFunction property to be used.
		:type decayFunction: Callable
		"""
		for i in range(len(self.internalState)):
			newIntensity = decayFunction(self.internalState[i].intensity, deltaTime)
			if newIntensity < 0:
				self.internalState.pop(i)
			else:
				self.internalState[i].intensity = newIntensity
		for i in range(len(self.currentRelations)):
			self.currentRelations[i].decay(decayFunction)
