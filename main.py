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

    def toHOA(self):
        label = ""
        processId = 0
        critCount = 0
        for pState in self.process_states:
            offset = 0
            if pState["status"] == "exec":
                offset = 0
            elif pState["status"] == "wait":
                offset = 1
            elif pState["status"] == "critical":
                offset = 2
                critCount += 1
            label += f"{processId*3+offset}&"
            processId += 1
        if critCount > 1:
            print("HERE")
        label=label[:-1]
        return f"State: [{label}] {self.id}"

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
        prevProcessLine = processState["line"]
        l = processState["it"]  # process' iteration counter
        ns = constructChildState(state)
        ns.parent_id = parentId
        if prevProcessLine == 0:
            ns.levels[i] = l  # levels[i] = l
            ns.process_states[i]["line"] = 1
        elif prevProcessLine == 1:
            ns.last_to_enter[l] = i  # last_to_enter[l] = i
            ns.process_states[i]["line"] = 2
            ns.process_states[i]["status"] = "wait"
        elif prevProcessLine == 2:
            condition = (ns.last_to_enter[l] == i)  # last_to_enter[l] == i
            kExists = False
            for k in range(len(ns.levels)):
                if (k != i) & (ns.levels[k] >= l):
                    kExists = True
            condition = condition & kExists
            if not condition:  # if while condition is NOT met, we can go to next iteration OR to critical section
                if l < ns.n-2:  # if we are not at the last iteration, we can go to next iteration
                    ns.process_states[i]["line"] = 0
                    ns.process_states[i]["it"] = l + 1
                else:  # if we are at the last iteration, we can enter the critical section
                    ns.process_states[i]["status"] = "critical"
                    ns.process_states[i]["line"] = 4
            else:  # while condition still holds, we must wait
                ns.process_states[i]["status"] = "wait"
                ns.process_states[i]["line"] = 2
        elif prevProcessLine == 4:
            ns.process_states[i]["line"] = 5
            ns.process_states[i]["status"] = "exec"
        elif prevProcessLine == 5:
            ns.levels[i] = -1  # levels[i] = -1
            ns.process_states[i]["line"] = 0
            ns.process_states[i]["it"] = 0

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
    with open(f"./output/{filename}.dot", "w") as f:
        f.write(printDot(allStates, allTransitions))

class TS:
    def __init__(self, states, transitions,name="TS",n=2):
        self.states = states
        self.transitions = transitions
        self.name = name
        self.n = n

    def toDot(self):
        saveDot(self.states, self.transitions, f"TS_{self.name}")

    def toHOA(self):
        seqmap = {}  # store sequential mapping of states for HOA parsing
        sc = 0
        for s in self.states:
            seqmap[s.id] = sc
            sc += 1
        outString = "HOA: v1\n"
        outString += f"States: {len(self.states)}\n"
        outString += "Start: 0\n"
        outString += "Acceptance: 1 Fin(0)\n"  # todo reason about Acceptance condition
        outString += f"AP: {self.n*3}"
        for i in range(self.n):
            outString += f" \"e{i}\" \"w{i}\" \"c{i}\""
        outString += "\n--BODY--\n"
        for s in self.states:
            oldId = s.id
            s.id = seqmap[s.id]
            outString += s.toHOA() + "\n"
            s.id = oldId
            for outgoing in self.transitions[s.id]:
                outString += f"  {seqmap[outgoing]}\n"
        outString += "--END--"
        with open(f"./output/TS_{self.name}.hoa", "w") as f:
            f.write(outString)

def generatePeterson(n):
    root = State(n)
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
                if s.parent_id not in allTransitions:
                    allTransitions[s.parent_id] = [s.id]
                else:
                    allTransitions[s.parent_id] = allTransitions[s.parent_id] + [s.id]
            else:  # state already exists, so we need to store transition from parent to existing state
                for s2 in allStates:
                    if s == s2:      # find existing duplicate state
                        if s.parent_id not in allTransitions:
                            allTransitions[s.parent_id] = [s2.id]
                        else:
                            allTransitions[s.parent_id] = allTransitions[s.parent_id] + [s2.id]

        if not filteredStates:
            break  # stop if no new states were found
        else:
            newStates = filteredStates

    return TS(allStates, allTransitions, name=f"P{n}",n=n)


if __name__ == '__main__':
    start = time.time()
    P = generatePeterson(n=2)
    P.toDot()
    P.toHOA()
    end = time.time()
    print(f"Time taken: {round(end-start,3)}s")
