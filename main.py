stateCounter = 0

import copy

class State:
    def __init__(self, n):
        global stateCounter
        self.n = n
        self.levels = [-1]*n
        self.last_to_enter = [0]*(n-1)
        self.process_states = [{"it":0,"line":0}]*n
        self.children:[State] = []
        self.id = stateCounter
        self.parent_id = -1
        stateCounter+=1

    def toDot(self):
        return f"{self.id} [label=\"{self.levels} {self.last_to_enter}\\n{self.process_states}\"]"

    def __str__(self):
        return f"---\nState {self.id} \n\tLevels - {self.levels} \n\tlte - {self.last_to_enter} \n\tpstates - {self.process_states} \n"


    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        levelEQ = self.levels == other.levels
        lteEQ = self.last_to_enter == other.last_to_enter
        processEQ = True
        for i in range(len(self.process_states)):
            processEQ = processEQ & (self.process_states[i]["it"] == other.process_states[i]["it"])
            processEQ = processEQ & (self.process_states[i]["line"] == other.process_states[i]["line"])
        return levelEQ & lteEQ & processEQ

def constructChildState(state:State):
    ns = State(state.n)
    ns.parent_id = state.id
    ns.levels = copy.deepcopy(state.levels)
    ns.last_to_enter = copy.deepcopy(state.last_to_enter)
    ns.process_states = []
    for ps in state.process_states:
        ns.process_states.append(copy.deepcopy(ps))  # necessary deepcopy of dict
    return ns

def getSuccessors(state:State):
    parentId = state.id
    sc = []

    for i in range(len(state.process_states)):
        processState = state.process_states[i]
        processLine = processState["line"]
        l = processState["it"]  # process' iteration counter
        ns = constructChildState(state)
        ns.parent_id = parentId
        if processLine == 0:
            ns.levels[i] = l  # levels[i] = l
        elif processLine == 1:
            ns.last_to_enter[l] = i  # last_to_enter[l] = i
        elif processLine == 2:
            pass
        elif processLine == 3:
            pass
        elif processLine == 4:
            pass
        elif processLine == 5:
            pass
        ns.process_states[i]["line"] = processLine + 1

        sc.append(ns)
    return sc

def printDot(allStates:dict, allTransitions:dict):
    print("digraph G {")
    for s in allStates.values():
        print(s.toDot())
    for t in allTransitions:
        for toState in allTransitions[t]:
            print(f"{t} -> {toState}")
    print("}")

def performBFS():
    root = State(2)
    allStates = {0: root}
    allTransitions = dict()  # if 0→[1,2,3] stores {0:[1,2,3]}
    newStates = [root]
    oldSC = stateCounter
    while True:
        oldStates = newStates  # BFS expansion
        newStates = []
        for state in oldStates:
            successors = getSuccessors(state)
            for s in successors:
                newStates.append(s)
        # ToDo check if new states are duplicate, and if all of them are, break.
        #  Do so by looping over allStates and checking ==? if duplicate, store transition from new state's parent
        #  to found duplicate state
        for s in newStates:
            allStates[s.id] = s
            allTransitions[s.parent_id] = allTransitions.get(s.parent_id, []) + [s.id]
        if stateCounter > 5:
            break

    printDot(allStates, allTransitions)

if __name__ == '__main__':
    performBFS()
