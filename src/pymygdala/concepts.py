from typing import Union

class Emotion:
    def __init__(self, name: str = "joy", intensity: float = 0.0):
        self.name = name
        self.intensity = intensity
    
    def __str__(self):
        return "Emotion: name(" + self.name + "), intensity(" + str(self.intensity) + ")."

class Goal:
    def __init__(self, name: str = "main", utility: float = 1.0, isMaintenanceGoal: bool = False):
        self.name = name
        self.utility = utility
        self.likelihood = 0.5
        self.calculateLikelyhood = None
        self.maintenanceGoal = isMaintenanceGoal #There are maintenance and achievement goals. When an achievement goal is reached (or not), this is definite (e.g., to a the promotion or not). A maintenance goal can become true/false indefinetly (e.g., to be well-fed)
    
    def __str__(self):
        return "Goal: name(" + self.name + "), utility(" + str(self.utility) + "), likelihood(" + str(self.likelihood) + ")." 

class Belief:
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
    def __init__(self, targetName: str, like: float = 1.0):
        self.agentName = targetName
        self.like = like
        self.emotionList = []

    def addEmotion(self, emotion: Emotion):
        added = False
        for  i in range( len(self.emotionList) ):
            if self.emotionList[i].name == emotion.name:
                '''
                if (this.emotionList[i].intensity < emotion.intensity){
                    this.emotionList[i].intensity = emotion.intensity;
                }'''
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
