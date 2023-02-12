import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
import random
from pymygdala.engines import Gamygdala
from pymygdala.concepts import Goal, Belief
from pymygdala.agent import Agent

def generateReactionForAgent(g_agent):
    print(g_agent.getEmotionalState(True))

def printAgentHistory(agent: str, pads_per_step: list[dict[str, list[float]]], article_history: list[tuple[str, float]]):
    print("%s's PAD History" % agent)
    for step in range(len(pads_per_step)):
        print("An article %s -> %s" % (article_history[step], pads_per_step[step][agent]))

def fuzzyOpinion(opinion: float) -> str:
    if opinion >= 0.6:
        return "loves"
    elif opinion >= 0.10:
        return "likes"
    elif opinion > -0.10:
        return "dislikes"
    elif opinion > -0.6:
        return "hates"
    else:
        return "is indifferent to"

def showGraph(G):
    # All the fancy code for making the graph is below.
    pos = nx.spring_layout(G)

    edges,weights = zip(*nx.get_edge_attributes(G,'relationship').items())

    # Transform the weights into temperatures.
    # Matplotlib has a RdYlGn Diverging Colormap that looks perfect
    # Scale the [-1, 1] tp [0, 1]
    uniform = [(i + 1.0) * 0.5 for i in weights]
    colormap = mpl.colormaps["RdYlGn"]
    temperatures = [colormap(i) for i in uniform]


    # Draw and show the graph
    fig = plt.figure()
    nx.draw(G, pos, edgelist=edges, edge_color=temperatures)
    fig.set_facecolor("#888888")
    plt.show()

def generateAgent(engine, agent_name):
    gamygdala_agent = engine.createAgent(agent_name)
    agents[agent_name] = gamygdala_agent

    # Create the goals dict for this agent
    goals[agent_name] = {}

    # Need to ensure unique choices
    opinions = random.sample(ALLOWED_THINGS, NUM_OPINIONS)

    # Create a list of tuples of the form (goal_name, goal_utility)
    for opinion in [(i, random.uniform(-1.0, 1.0)) for i in opinions]:

        goal_name = agent_name + "_" + opinion[0]

        print("%s %s %s" % (agent_name, fuzzyOpinion(opinion[1]), opinion[0]))

        #Create a Goal object and ensure we register it
        goal = Goal(goal_name, opinion[1], True)

        goals[agent_name][goal_name] = goal
        engine.registerGoal(goal)

        # Add the goal to the Gamygdala agent
        gamygdala_agent.addGoal(goal)

# The things that agents have opinions about and Articles discuss
ALLOWED_THINGS = ["\N{baby}", "\N{rat}", "\N{cat}", "\N{dog}", "\N{potato}"]

# Number of personal opinions per agent
NUM_OPINIONS = 5

NAMES = ["John", "Jan", "Juan", "Jean", "Johann"]

# An article is a tuple of the form ("<thing>", attitude: [-1.0, 1.0])

engine = Gamygdala()
        
# String agent_name to Gamygdala Agent
agents : dict[str, Agent] = {}

# String agent_name to a dict of goal_name to Gamygala Goal, 
# ie {agent_name: {goal_name: goal}}
goals : dict[str, dict[str: Goal]] = {}

NUM_ROUNDS = 10
likelihood = 1.0 / float(NUM_ROUNDS)
DECAY_SPEED = 2
EMO_GAIN = 20

random.seed(2)

for name in NAMES:
    generateAgent(engine, name)

# Create a complete (fully interconnected) graph of all the agents, with their names as Node keys
G = nx.complete_graph(agents.keys())

# Assign weights to the relationships randomly 
# And add the relationships to Gamygdala
for e in nx.edges(G):
    G.edges[e]['relationship'] = random.triangular(-0.5, 0.5)
    engine.createRelation(e[0], e[1], G.edges[e]['relationship'])
    engine.createRelation(e[1], e[0], G.edges[e]['relationship'])

#showGraph(G)
engine.setGain(EMO_GAIN)
    
article_history = []

#pads_per_step[step][agent] = [Their PAD state at step]
pads_per_step: list[dict[str, list[float]]] = []

for round in range(NUM_ROUNDS):
    # Generate the article
    article = (random.choice(ALLOWED_THINGS), random.uniform(-1.0, 1.0))
    article_history.append(article)
    print("------------------------------------")
    print("Round %d article: (%s, %s)" % (round, article[0], fuzzyOpinion(article[1])))

    step_pads: dict[str, list[float]] = {}

    # Submit the article for agents to review
    for agent_name, g_agent in agents.items():
        # Determine if this agent has a goal relevant to this THING
        goal_name = agent_name + "_" + article[0]
        if not g_agent.hasGoal(goal_name):
            print("%s skipping due to no interest in %s" % (agent_name, article[0]))
            continue

        # Form the belief
        b = Belief(likelihood, "Article", [goal_name], [article[1]], isIncremental=True)
        g_agent.appraise(b)
        g_agent.decay(engine, DECAY_SPEED)

        # Add to the PAD history for this agent
        step_pads[agent_name] = g_agent.getPADState(True)

        #g_agent.printAllRelations()
        #generateReactionForAgent(g_agent)
        
        if round == 0:
            prev_pad = [0.0, 0.0, 0.0]
        else:
            prev_pad = pads_per_step[round - 1][agent_name]

        cur_pad = g_agent.getPADState(True)

        agent_opinion = g_agent.getGoalByName(goal_name).utility
        # "Jim who likes rats"
        print("%s who %s %s: " % (agent_name, fuzzyOpinion(agent_opinion), article[0]))
        print("Mood delta: %s" % (str([cur_pad[i] - prev_pad[i] for i in range(3)])))
        print("++++")

    pads_per_step.append(step_pads)

    #engine.printAllEmotions()

    print("------------------------------------")
    # Agents submit their opinion of the article
    # Agents react to each others reactions. Apparently Gamygdala decay function handles relationships?
    # Update the relations in NetworkX

# Print out the graph again

#showGraph(G)

printAgentHistory("John", pads_per_step, article_history)