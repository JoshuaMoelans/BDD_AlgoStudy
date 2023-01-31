import time


from PetersonState import PetersonState
from LamportState import LamportState


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
            if toState != t:
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
                if outgoing != s.id:
                    outString += f"  {seqmap[outgoing]}\n"
        outString += "--END--"
        with open(f"./output/TS_{self.name}.hoa", "w") as f:
            f.write(outString)


def generateTS(n,algo="Peterson"):
    root = PetersonState(n)
    if algo != "Peterson":
        root = LamportState(n)
    allStates = {root}
    allTransitions = dict()  # if 0→[1,2,3] stores {0:[1,2,3]}

    newStates = [root]

    while True:
        oldStates = newStates  # BFS expansion
        newStates = []
        for state in oldStates:
            newStates += state.getSuccessors()  # add all successors to newStates

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

    return TS(allStates, allTransitions, name=f"{algo[0]}{n}",n=n)


if __name__ == '__main__':
    start = time.time()
    # P = generateTS(n=2,algo="Peterson")
    P = generateTS(n=3,algo="Lamport")
    P.toDot()
    P.toHOA()
    end = time.time()
    print(f"Time taken: {round(end-start,3)}s")
