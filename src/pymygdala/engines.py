"""

"""

from typing import Union

from pymygdala.agent import Agent
from pymygdala.concepts import Goal, Relation, Belief, Emotion
import time
import math

current_milli_time = lambda: int(round(time.time() * 1000))

import threading
import random

def setInterval(func, sec, args=None):
    def func_wrapper():
        setInterval(func, sec, args)
        if args is not None:
            func()
        else:
            func(args)
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

class Gamygdala:
    """
    This is the main appraisal engine class taking care of interpreting a situation emotionally.
    Typically you create one instance of this class and then register all agents (emotional entities) to it,
    as well as all goals.
    """
    def __init__(self):
        self.agents = []
        self.goals = []
        self.decayFunction = self.exponentialDecay
        self.decayFactor = 0.8
        self.lastMillis = current_milli_time()
        self.millisPassed = 0
        self.debug = False

    def createAgent(self, agentName: str) -> Agent:
        """
        A facilitator method that creates a new Agent and registers it for you

        :param agentName: The agent with agentName is created
        :type agentName: str

        :return: An agent reference to the newly created agent
        :rtype: Agent
        """
        temp=Agent(agentName)
        self.registerAgent(temp)
        return temp

    def createGoalForAgent(self, agentName: str, goalName: str, goalUtility: float, isMaintenanceGoal: bool = False) -> Union[Goal, None]:
        """
        A facilitator method to create a goal for a particular agent, that also registers the goal to the agent and gamygdala.
        This method is thus handy if you want to keep all gamygdala logic internal to Gamygdala.
        However, if you want to do more sophisticated stuff (e.g., goals for multiple agents, keep track of your own list of goals to also remove them, appraise events per agent without the need for gamygdala to keep track of goals, etc...) this method will probably be doing too much.

        :param agentName: The agent's name to which the newly created goal has to be added.
        :type agentName: str

        :param goalName: The goal's name.
        :type goalName: str

        :param goalUtility: The goal's utility.
        :type goalUtility: double

        :param isMaintenanceGoal: Defines if the goal is a maintenance goal or not [optional]. The default is that the goal is an achievement goal, i.e., a goal that once it's likelihood reaches true (1) or false (-1) stays that way.
        :type isMaintenanceGoal: boolean

        :return: - a goal reference to the newly created goal.
        :rtype: Goal or None
        """
        tempAgent = self.getAgentByName(agentName)
        if tempAgent:
            tempGoal = self.getGoalByName(goalName)
            if tempGoal:
                print("Warning: I cannot make a new goal with the same name ", goalName, " as one is registered already. I assume the goal is a common goal and will add the already known goal with that name to the agent ", agentName)
            else:
                tempGoal = Goal(goalName, goalUtility)
                self.registerGoal(tempGoal)
            tempAgent.addGoal(tempGoal)
            if isMaintenanceGoal:
                tempGoal.isMaintenanceGoal = isMaintenanceGoal
            return tempGoal
        else:
            print("Error: agent with name ", agentName ," does not exist, so I cannot add a create a goal for it.")
            return None

    def createRelation(self, sourceName: str, targetName: str, relation: float):
        """
        A facilitator method to create a relation between two agents. Both source and target have to exist and be registered with this Gamygdala instance.
        This method is thus handy if you want to keep all gamygdala logic internal to Gamygdala.

        :param sourceName: The agent who has the relation (the source)
        :type sourceName: str

        :param targetName: The agent who is the target of the relation (the target)
        :type targetName: str

        :param relation: The relation (between -1 and 1).
        :type relation: double
        """
        source=self.getAgentByName(sourceName)
        target=self.getAgentByName(targetName)
        if source and target and relation>=-1 and relation<=1:
            source.updateRelation(targetName, relation)
        else:
            print('Error: cannot relate ', source, '  to ', target ,' with intensity ', relation)

    def appraiseBelief(self, likelihood: float, causalAgentName: str, affectedGoalNames: list[str], goalCongruences: list[float], isIncremental: bool = True):
        """
        A facilitator method to appraise an event. It takes in the same as what the new Belief(...) takes in, creates a belief and appraises it for all agents that are registered.
        This method is thus handy if you want to keep all gamygdala logic internal to Gamygdala.

        :param likelihood: The likelihood of this belief to be true.
        :type likelihood: double

        :param causalAgentName: The agent's name of the causal agent of this belief.
        :type causalAgentName: str

        :param affectedGoalNames: An array of affected goals' names.
        :type affectedGoalNames: list[str]

        :param goalCongruences: An array of the affected goals' congruences (i.e., the extend to which this event is good or bad for a goal [-1,1]).
        :type goalCongruences: list[double]

        :param isIncremental: Incremental evidence enforces gamygdala to see this event as incremental evidence for (or against) the list of goals provided, i.e, it will add or subtract this belief's likelihood*congruence from the goal likelihood instead of using the belief as "state" defining the absolute likelihood.
        :type isIncremental: boolean
        """
        tempBelief=Belief(likelihood, causalAgentName, affectedGoalNames, goalCongruences, isIncremental)
        self.appraise(tempBelief)

    def printAllEmotions(self, useGain: bool = True):
        """
        Facilitator method to print all emotional states to the console.

        :param useGain: Whether you want to print the gained (true) emotional states or non-gained (false).
        :type useGain: bool
        """
        for i in range(len(self.agents)):
            self.agents[i].printEmotionalState(useGain)
            self.agents[i].printRelations(None)

    def setGain(self, gain: float):
        """
        Facilitator to set the gain for the whole set of agents known to gamygdala.
        For more realistic, complex games, you would typically set the gain for each agent type separately, to finetune the intensity of the response.

        :param gain: The gain value [0 and 20].
        :type gain: double
        """
        for i in range(len(self.agents)):
            self.agents[i].setGain(gain)

    def setDecay(self, decayFactor: float, decayFunction: callable):
        """
        Sets the decay factor and function for emotional decay.
        It sets the decay factor and type for emotional decay, so that an emotion will slowly get lower in intensity.
        Whenever decayAll is called, all emotions for all agents are decayed according to the factor and function set here.

        :param decayFactor: The decayfactor used. A factor of 1 means no decay, a factor 
        :type decayFactor: double

        :param decayFunction: The decay function tobe used. choose between linearDecay or exponentialDecay (see the corresponding methods)
        :type decayFunction: callable
        """
        self.decayFunction=decayFunction
        self.decayFactor=decayFactor

    def startDecay(self, timeMS: int):
        """
        This starts the actual gamygdala decay process. It simply calls decayAll() at the specified interval.
        The timeMS only defines the interval at which to decay, not the rate over time, that is defined by the decayFactor and function.
        For more complex games (e.g., games where agents are not active when far away from the player, or games that do not need all agents to decay all the time) you should yourself choose when to decay agents individually.
        To do so you can simply call the agent.decay() method (see the agent class).

        :param timeMS: The "framerate" of the decay in milliseconds. 
        :type timeMS: int
        """
        setInterval(self.decayAll, timeMS, self)
    
    #////////////////////////////////////////////////////////
    #//Below this is more detailed gamygdala stuff to use it more flexibly.
    #////////////////////////////////////////////////////////

    def registerAgent(self, agent: Agent):
        """
        For every entity in your game (usually NPC's, but can be the player character too) you have to first create an Agent object and then register it using this method.
        Registering the agent makes sure that Gamygdala will be able to emotionally interpret incoming Beliefs about the game state for that agent.

        :param agent: The agent to be registered
        :type agent: Agent
        """
        self.agents.append(agent)
        agent.gamygdalaInstance = self

    def getAgentByName(self, agentName: str) -> Union[Agent, None]:
        """
        Simple agent getter by name.

        :param agentName: The name of the agent to be found.
        :type timeMS: int

        :return: None or an agent reference that has the name property equal to the agentName argument
        :rtype: Agent or None
        """
        for i in range(len(self.agents)):
            if self.agents[i].name == agentName:
                return self.agents[i]
        print('Warning: agent ', agentName, ' not found')
        return None

    def registerGoal(self, goal: Goal):
        """
        For every goal that NPC's or player characters can have you have to first create a Goal object and then register it using this method.
        Registering the goals makes sure that Gamygdala will be able to find the correct goal references when a Beliefs about the game state comes in.

        :param goal: The goal to be registered.
        :type goal: Goal
        """
        if self.getGoalByName(goal.name) == None:
            self.goals.append(goal)
        else:
            print("Warning: failed adding a second goal with the same name: ", goal.name)

    def getGoalByName(self, goalName: str) -> Union[Goal, None]:
        """
        Simple goal getter by name.

        :param goalName: The name of the goal to be found.
        :type goalName: str

        :return: None or a goal reference that has the name property equal to the goalName argument
        :rtype: Goal
        """
        for i in range(len(self.goals)):
            if self.goals[i].name == goalName:
                return self.goals[i]
        return None

    def appraise(self, belief: Belief, affectedAgent: Union[Agent, None] = None) -> bool:
        """
        This method is the main emotional interpretation logic entry point. It performs the complete appraisal of a single event (belief) for all agents (affectedAgent=None) or for only one agent (affectedAgent=true)
        if affectedAgent is set, then the complete appraisal logic is executed including the effect on relations (possibly influencing the emotional state of other agents),
        but only if the affected agent (the one owning the goal) == affectedAgent
        this is sometimes needed for efficiency, if you as a game developer know that particular agents can never appraise an event, then you can force Gamygdala to only look at a subset of agents.
        Gamygdala assumes that the affectedAgent is indeed the only goal owner affected, that the belief is well-formed, and will not perform any checks, nor use Gamygdala's list of known goals to find other agents that share this goal (!!!)

        :param belief: The current event, in the form of a Belief object, to be appraised
        :type belief: Belief

        :param affectedAgent: The reference to the agent who needs to appraise the event. If given, this is the appraisal perspective (see explanation above).
        :type affectedAgent: Agent

        :return:
        :rtype: bool
        """
        if affectedAgent is None:
            #check all
            if self.debug:
                print(belief)
            
            if not (len(belief.goalCongruences) == len(belief.affectedGoalNames)):
                print("Error: the congruence list was not of the same length as the affected goal list")
                return False #The congruence list must be of the same length as the affected goals list.
            
            if len(self.goals) == 0:
                print("Warning: no goals registered to Gamygdala, all goals to be considered in appraisal need to be registered.")
                return False #The congruence list must be of the same length as the affected goals list.

            for i in range( len(belief.affectedGoalNames) ):
                #Loop through every goal in the list of affected goals by self event.
                currentGoal=self.getGoalByName(belief.affectedGoalNames[i])
                if not (currentGoal==None):
                    #the goal exists, appraise it
                    utility = currentGoal.utility
                    deltaLikelihood = self._calculateDeltaLikelihood(currentGoal, belief.goalCongruences[i], belief.likelihood, belief.isIncremental)
                    desirability = belief.goalCongruences[i] * utility
                    if self.debug:
                        print('Evaluated goal: ', currentGoal.name, '(', utility, ', ', deltaLikelihood, ')')	

                    #now find the owners, and update their emotional states
                    for j in range(len(self.agents)):
                        if self.agents[j].hasGoal(currentGoal.name):
                            owner=self.agents[j]
                            if self.debug:
                                print('....owned by ', owner.name)
                            self._evaluateInternalEmotion(utility, deltaLikelihood, currentGoal.likelihood, owner)  
                            self._agentActions(owner.name, belief.causalAgentName, owner.name, desirability, utility, deltaLikelihood) 
                            #now check if anyone has a relation to self goal owner, and update the social emotions accordingly.
                            for k in range(len(self.agents)):
                                relation=self.agents[k].getRelation(owner.name)
                                if not (relation==None):
                                    if self.debug:
                                        print(self.agents[k].name, ' has a relationship with ', owner.name)
                                        print(relation)
                                    #The agent has relationship with the goal owner which has nonzero utility, add relational effects to the relations for agent[k]. 
                                    self._evaluateSocialEmotion(utility, desirability, deltaLikelihood, relation, self.agents[k])
                                    #also add remorse and gratification if conditions are met within (i.e., agent[k] did something bad/good for owner)
                                    self._agentActions(owner.name, belief.causalAgentName, self.agents[k].name, desirability, utility, deltaLikelihood)
                                else:
                                    if self.debug:
                                        print(self.agents[k].name, ' has NO relationship with ', owner.name)
        else:
            #check only affectedAgent (which can be much faster) and does not involve console output nor checks
            for i in range(len(belief.affectedGoalNames)):
                #Loop through every goal in the list of affected goals by self event.
                currentGoal=affectedAgent.getGoalByName(belief.affectedGoalNames[i])
                utility = currentGoal.utility
                deltaLikelihood = self._calculateDeltaLikelihood(currentGoal, belief.goalCongruences[i], belief.likelihood, belief.isIncremental)
                desirability = belief.goalCongruences[i] * utility
                #assume affectedAgent is the only owner to be considered in self appraisal round.
                owner=affectedAgent
                self._evaluateInternalEmotion(utility, deltaLikelihood, currentGoal.likelihood, owner)  
                self._agentActions(owner.name, belief.causalAgentName, owner.name, desirability, utility, deltaLikelihood) 
                #now check if anyone has a relation to self goal owner, and update the social emotions accordingly.
                for k in range(len(self.agents)):
                    relation=self.agents[k].getRelation(owner.name)
                    if relation is not None:
                        if self.debug:
                            print(self.agents[k].name, ' has a relationship with ', owner.name)
                            print(relation)
                        #The agent has relationship with the goal owner which has nonzero utility, add relational effects to the relations for agent[k]. 
                        self._evaluateSocialEmotion(utility, desirability, deltaLikelihood, relation, self.agents[k])
                        #also add remorse and gratification if conditions are met within (i.e., agent[k] did something bad/good for owner)
                        self._agentActions(owner.name, belief.causalAgentName, self.agents[k].name, desirability, utility, deltaLikelihood) 
                    else:
                        if self.debug:
                            print(self.agents[k].name, ' has NO relationship with ', owner.name)
        #print the emotions to the console for debugging
        if self.debug:
            self.printAllEmotions(True)

    def decayAll(self):
        """
        This method decays for all registered agents the emotional state and relations. It performs the decay according to the time passed, so longer intervals between consecutive calls result in bigger clunky steps.
        Typically this is called automatically when you use startDecay(), but you can use it yourself if you want to manage the timing.
        This function is keeping track of the millis passed since the last call, and will (try to) keep the decay close to the desired decay factor, regardless the time passed
        So you can call this any time you want (or, e.g., have the game loop call it, or have e.g., Phaser call it in the plugin update, which is default now).
        Further, if you want to tweak the emotional intensity decay of individual agents, you should tweak the decayFactor per agent not the "frame rate" of the decay (as this doesn't change the rate).
        """
        self.millisPassed=current_milli_time()-self.lastMillis
        self.lastMillis=current_milli_time()
        for i in range(len(self.agents)):
            self.agents[i].decay(self)


    #////////////////////////////////////////////////////////
    #//Below this is internal gamygdala stuff not to be used publicly (i.e., never call these methods).
    #////////////////////////////////////////////////////////
    
    def _calculateDeltaLikelihood(self, goal: Goal, congruence: float, likelihood: float, isIncremental: bool) -> float:
        #Defines the change in a goal's likelihood due to the congruence and likelihood of a current event.
        #We cope with two types of beliefs: incremental and absolute beliefs. Incrementals have their likelihood added to the goal, absolute define the current likelihood of the goal
        #And two types of goals: maintenance and achievement. If an achievement goal (the default) is -1 or 1, we can't change it any more (unless externally and explicitly by changing the goal.likelihood).
        oldLikelihood = goal.likelihood 
        newLikelihood = None
        if goal.maintenanceGoal == False and (oldLikelihood >= 1.0 or oldLikelihood <= -1.0):
            return 0.0
        
        if (goal.calculateLikelyhood is not None):
            newLikelihood = goal.calculateLikelyhood()
        else:
            if isIncremental:
                newLikelihood = oldLikelihood + likelihood * congruence
                newLikelihood= max(min(newLikelihood, 1.0), -1.0)
            else:
                newLikelihood = (congruence * likelihood + 1.0) / 2.0
        goal.likelihood = newLikelihood
        if oldLikelihood is not None:
            return newLikelihood - oldLikelihood
        else:
            return newLikelihood

    def _evaluateInternalEmotion(self, utility: float, deltaLikelihood: float, likelihood: float, agent: Agent):
        #This method evaluates the event in terms of internal emotions that do not need relations to exist, such as hope, fear, etc..
        positive = False
        intensity = 0
        emotion = []
        if utility >= 0:
            if deltaLikelihood >= 0:
                positive = True
            else:
                positive = False
        elif utility < 0:
            if deltaLikelihood >= 0:
                positive = False
            else:
                positive = True

        if likelihood > 0 and likelihood < 1:
            if positive:
                emotion.append('hope')   
            else:
                emotion.append('fear')
        elif likelihood == 1:
            if utility >= 0:
                if deltaLikelihood < 0.5:
                    emotion.append('satisfaction')
                emotion.append('joy')
            else:
                if deltaLikelihood <0.5:
                    emotion.append('fear-confirmed')
                emotion.append('distress')
        elif likelihood == 0:
            if utility >= 0:
                if deltaLikelihood > 0.5:
                    emotion.append('disappointment')
                emotion.append('distress')
            else:
                if (deltaLikelihood > 0.5):
                    emotion.append('relief')
                emotion.append('joy')
        intensity = abs(utility * deltaLikelihood)
        if not (intensity == 0):
            for i in range(len(emotion)):
                agent.updateEmotionalState(Emotion(emotion[i], intensity))

    def _agentActions(self, affectedName: str, causalName: str, selfName: str, desirability: float, utility: float, deltaLikelihood: float):
        if causalName is not None and causalName != '':
            #If the causal agent is None or empty, then we we assume the event was not caused by an agent.
            #There are three cases here.
            #The affected agent is SELF and causal agent is other.
            #The affected agent is SELF and causal agent is SELF.
            #The affected agent is OTHER and causal agent is SELF.
            emotion = Emotion("", 0.0)
            relation = None
            if affectedName == selfName and selfName != causalName:
                #Case one 
                if desirability >= 0:
                    emotion.name = 'gratitude'
                else:
                    emotion.name = 'anger'

                emotion.intensity = abs(utility * deltaLikelihood)
                agent = self.getAgentByName(selfName)
                if agent.hasRelationWith(causalName):
                    relation = agent.getRelation(causalName)          
                else:
                    agent.updateRelation(causalName, 0.0)
                    relation = agent.getRelation(causalName) 
                relation.addEmotion(emotion)
                agent.updateEmotionalState(emotion)  #also add relation emotion the emotion to the emotional state
            
            if affectedName == selfName and selfName == causalName:
                #Case two
                pass #GAMYDALA DONT SUPPORT AUTORELATION
            if affectedName != selfName and causalName == selfName:
                #Case three
                relation = None
                if self.getAgentByName(causalName).hasRelationWith(affectedName):
                    relation = self.getAgentByName(causalName).getRelation(affectedName)   
                    if  desirability >= 0:
                        if relation.like >= 0:
                            emotion.name = 'gratification'
                            emotion.intensity = abs(utility * deltaLikelihood * relation.like)
                            relation.addEmotion(emotion)
                            self.getAgentByName(causalName).updateEmotionalState(emotion)  #also add relation emotion the emotion to the emotional state
                    else:
                        if relation.like >= 0:
                            emotion.name = 'remorse'
                            emotion.intensity = abs(utility * deltaLikelihood * relation.like)
                            relation.addEmotion(emotion)
                            self.getAgentByName(causalName).updateEmotionalState(emotion)  #also add relation emotion the emotion to the emotional state
    """
    #A linear decay function that will decrease the emotion intensity of an emotion every tick by a constant defined by the decayFactor in the gamygdala instance.
    #You can set Gamygdala to use this function for all emotion decay by calling setDecay() and passing this function as second parameter. This function is not to be called directly.
    #@method gamygdala.linearDecay
    """
    def linearDecay(self, value: float, deltaTime: Union[float, None] = None) -> float:
        #assumes the decay of the emotional state intensity is linear with a factor equal to decayFactor per second.
        dt = deltaTime
        if dt is None:
            dt = self.millisPassed / 1000
        return value - self.decayFactor * (dt)

    """
    An exponential decay function that will decrease the emotion intensity of an emotion every tick by a factor defined by the decayFactor in the gamygdala instance.
    You can set Gamygdala to use this function for all emotion decay by calling setDecay() and passing this function as second parameter. This function is not to be called directly.
    @method gamygdala.exponentialDecay 
    """
    def exponentialDecay(self, value: float, deltaTime: Union[float, None] = None) -> float:
        dt = deltaTime
        if dt is None:
            dt = self.millisPassed/1000
        return value * math.pow(self.decayFactor, dt)

    def _evaluateSocialEmotion(self, utility: float, desirability: float, deltaLikelihood: float, relation: Relation, agent: Agent):
        #This function is used to evaluate happy-for, pity, gloating or resentment.
        #Emotions that arise when we evaluate events that affect goals of others.
        #The desirability is the desirability from the goal owner's perspective.
        #The agent is the agent getting evaluated (the agent that gets the social emotion added to his emotional state).
        #The relation is a relation object between the agent being evaluated and the goal owner of the affected goal.
        emotion = Emotion(None, None)
        if desirability >= 0:
            if relation.like >= 0:
                emotion.name = 'happy-for'
            else:
                emotion.name = 'resentment'
        else:
            if relation.like >= 0:
                emotion.name = 'pity'
            else:
                emotion.name = 'gloating'
        emotion.intensity = abs(utility * deltaLikelihood * relation.like)
        if emotion.intensity != 0:
            relation.addEmotion(emotion)
            agent.updateEmotionalState(emotion) #also add relation emotion the emotion to the emotional state
