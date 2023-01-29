import time

stateCounter = 0

import copy

class State:
    def __init__(self, n):
        global stateCounter
        self.n = n
        self.levels = [-1]*n
        self.last_to_enter = [0]*(n-1)
        self.process_states = [{"it":0,"line":0,"status":"exec"}]*n
        self.children:[State] = []
        self.id = stateCounter
        self.parent_id = -1
        stateCounter+=1

    def simpleString(self):
        out = f"{self.levels} {self.last_to_enter}\\n"
        for ps in self.process_states:
            out += f"[l:{ps['it']}|#{ps['line']}|{ps['status']}]"
        return  out

    def toDot(self):
        return f"{self.id} [label=\"{self.simpleString()}\"]\n"

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

    def __hash__(self):
        return 0  # (I think) hash is not used, so we can return 0; implemented to allow set() to work

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
            ns.process_states[i]["line"] = processLine + 1
        elif processLine == 1:
            ns.last_to_enter[l] = i  # last_to_enter[l] = i
            ns.process_states[i]["line"] = processLine + 1
        elif processLine == 2 or processLine == 3:
            condition = ns.last_to_enter[l] == i  # last_to_enter[l] == i
            for k in range(len(ns.levels)):
                condition = condition & ns.levels[k] >= l  # levels[k] >= l
            if not condition:  # if while condition not met, we can go to next iteration
                if l+1 != ns.n-2:  # if we are not at the last iteration, we can go to next iteration
                    ns.process_states[i]["line"] = 0
                    ns.process_states[i]["it"] = l + 1
                else:  # if we are at the last iteration, we can enter the critical section
                    ns.process_states[i]["line"] = 4
            else:
                ns.process_states[i]["status"] = "wait"
                ns.process_states[i]["line"] = processLine + 1
        elif processLine == 4:
            ns.process_states[i]["status"] = "critical"
            ns.process_states[i]["line"] = processLine + 1
        elif processLine == 5:
            ns.levels[i] = -1  # levels[i] = -1
            ns.process_states[i]["line"] = 0
            ns.process_states[i]["it"] = 0
            ns.process_states[i]["status"] = "exec"

        sc.append(ns)
    return sc

def printDot(allStates:set, allTransitions:dict):
    stateIDs = set([s.id for s in allStates])
    out = ""
    out += "digraph G {\n"
    for s in allStates:
        out += s.toDot()
    for t in allTransitions:
        if t not in stateIDs:
            continue
        for toState in allTransitions[t]:
            out += f"{t} -> {toState}\n"
    out += "\n}"
    return out

def saveDot(allStates:set, allTransitions:dict, filename:str):
    with open(f"{filename}.dot", "w") as f:
        f.write(printDot(allStates, allTransitions))

def performBFS():
    root = State(2)
    allStates = {root}
    allTransitions = dict()  # if 0→[1,2,3] stores {0:[1,2,3]}

    newStates = [root]

    while True:
        oldStates = newStates  # BFS expansion
        newStates = []
        for state in oldStates:
            newStates += getSuccessors(state)  # add all successors to newStates

        filteredStates = []
        for s in newStates:
            if s not in allStates:
                allStates.add(s)
                filteredStates.append(s)  # store new state to be explored
                allTransitions[s.parent_id] = allTransitions.get(s.parent_id, []) + [s.id]
            else:  # state already exists, so we need to store transition from parent to existing state
                for s2 in allStates:
                    if s == s2:      # find existing duplicate state
                        allTransitions[s.parent_id] = [s2.id]

        if not filteredStates:  # todo what else? replace newStates with filteredStates?
            break  # stop if no new states were found

    saveDot(allStates, allTransitions,"TS")


if __name__ == '__main__':
    start = time.time()
    performBFS()
    end = time.time()
    print(f"Time taken: {round(end-start,3)}s")
