from typing import Union

class Emotion:
    """
    This class is mainly a data structure to store an emotion with its intensity.
    """
    def __init__(self, name: str = "joy", intensity: float = 0.0):
        self.name = name
        self.intensity = intensity
    
    def __str__(self):
        return "Emotion: name(" + self.name + "), intensity(" + str(self.intensity) + ")."

class Goal:
    """
    This class is mainly a data structure to store a goal with it's utility and likelihood of being achieved. 
    This is used as basis for interpreting Beliefs

    :param name: The name of the goal.
    :type name: str

    :param utility: The "amount" of pleasure or displeasure the agent experiences upon achieving this goal. Must be a float between [-1.0, 1.0]
    :type utility: float

    :param isMaintenanceGoal: Determines if this is a maintenance or achievement goal. When an achievement goal is reached (or not), this is definite (e.g., to a the promotion or not). A maintenance goal can become true/false indefinetly (e.g., to be well-fed).
    :type isMaintenanceGoal: bool
    """
    def __init__(self, name: str = "main", utility: float = 1.0, isMaintenanceGoal: bool = False):

        self.name = name
        self.utility = utility
        self.likelihood = 0.5
        self.calculateLikelyhood = None
        self.maintenanceGoal = isMaintenanceGoal
    
    def __str__(self):
        return "Goal: name(" + self.name + "), utility(" + str(self.utility) + "), likelihood(" + str(self.likelihood) + ")." 

class Belief:
    """
    This class is a data structure to store one Belief for an agent. 
    A belief is created and fed into a Gamygdala instance (method Gamygdala.appraise()) for evaluation.

    :param likelihood: The name of the goal.
    :type likelihood: float
    
    :param causalAgentName: The name of the agent that caused this event.
    :type causalAgentName: str
    
    :param affectedGoalNames: A list of strings representing the names of goals effected by this belief.
    :type affectedGoalNames: list[str] or None
    
    :param goalCongruences: A list of float representing how congruent this belief is for each goal in affectedGoalNames.
    :type goalCongruences: list[str] or None
    
    :param isIncremental: Is this an incremental or maintenance goal.
    :type isIncremental: bool

    """
    def __init__(self, likelihood: float = 0.0, causalAgentName: str = '', affectedGoalNames: Union[list[str], None] = None, goalCongruences: Union[list[int], None] = None, isIncremental: bool = False):
        self.likelihood = likelihood
        self.causalAgentName = causalAgentName
        if affectedGoalNames is None:
            self.affectedGoalNames = []
        else:
            self.affectedGoalNames = affectedGoalNames
        if goalCongruences is None:
            self.goalCongruences = []
        else:
            self.goalCongruences = goalCongruences
        
        self.isIncremental = isIncremental
    
    def __str__(self):
        return "Belief: Causal Agent (" + self.causalAgentName + "), Likelihood (" + str(self.likelihood) + "), AffectedGoald(" + str(self.affectedGoalNames) + ") Goal Congruences(" + str(self.goalCongruences) + ")."

class Relation:
    """
    This is the class that represents a relation one agent has with other agents. 
    It's main role is to store and manage the emotions felt for a target agent (e.g angry at, or pity for). 
    Each agent maintains a list of relations, one relation for each target agent.
    """
    def __init__(self, targetName: str, like: float = 1.0):
        self.agentName = targetName
        self.like = like
        self.emotionList = []

    def addEmotion(self, emotion: Emotion):
        added = False
        for  i in range( len(self.emotionList) ):
            if self.emotionList[i].name == emotion.name:
                self.emotionList[i].intensity += emotion.intensity
                added = True
        if added:
            #copy on keep, we need to maintain a list of current emotions for the relation, not a list refs to the appraisal engine
            self.emotionList.append(Emotion(emotion.name, emotion.intensity))

    def decay(self, decayFunction):
        for  i in range( len(self.emotionList) ):
            newIntensity=decayFunction(self.emotionList[i].intensity)
            if newIntensity < 0:
                #This emotion has decayed below zero, we need to remove it.
                self.emotionList.pop(i)
            else:
                self.emotionList[i].intensity = newIntensity

    def __str__(self):
        s1 = "Target Name: %s, Like: %s\n"%(self.agentName, self.like)
        for emotion in self.emotionList:
            s1 += "Emotion: " + emotion.name + ", " + str(emotion.intensity)
        return s1
