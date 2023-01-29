""" PSEUDOCODE
line    command
-----
i <- processNr
     for l in range(0,n-1)
0        levels[i] = l
1        last_to_enter[l] = i
2        while last_to_enter[l]=i & there exists k!=i : levels[k]>=l:
3            wait(i)
4    critical(i)
5    levels[i]=-1
"""
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

    def __str__(self):
        return f"---\nState {self.id} \n\tLevels - {self.levels} \n\tl_t_e - {self.last_to_enter} \n\tpstates - {self.process_states} \n"


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
    ns.process_states = copy.deepcopy(state.process_states)
    return ns

def getSuccessors(state:State):
    parentId = state.id
    sc = []

    for i in range(len(state.process_states)):
        processState = state.process_states[i]
        processLine = processState["line"]
        processIt = processState["it"]
        ns = constructChildState(state)
        ns.parent_id = parentId
        if processLine == 0:
            ns.levels[i] = processIt
        elif processLine == 1:
            ns.last_to_enter[processIt] = i
        elif processLine == 2:
            pass
        elif processLine == 3:
            pass
        elif processLine == 4:
            pass
        ns.process_states[i]["line"] = processLine + 1

        sc.append(ns)
    return sc


if __name__ == '__main__':
    root = State(3)
    allStates = {0:root}
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
        if newStates:
            break
    for s in newStates:
        print(s)
    pass

