import copy

stateCounter = 0

class LamportState:
    def __init__(self, n):
        global stateCounter
        self.n = n
        self.entering = [False]*n
        self.number = [0]*n
        self.process_states = [{"it":0,"line":0,"status":"exec"}]*n
        self.children:[LamportState] = []
        self.id = stateCounter
        self.parent_id = -1
        stateCounter+=1

    def getSuccessors(self):
        parentId = self.id
        sc = []

        for i in range(len(self.process_states)):
            processState = self.process_states[i]
            prevProcessLine = processState["line"]
            j = processState["it"]  # process' iteration counter stored as 'j'
            ns = self.constructChildState()
            ns.parent_id = parentId
            if prevProcessLine == 0:
                ns.entering[i] = True # entering[i] = true
                ns.process_states[i]["line"] = 1
            elif prevProcessLine == 1:
                ns.number[i] = (1+max(ns.number)) % ns.n+1  # last_to_enter[l] = i
                ns.process_states[i]["line"] = 2
                ns.process_states[i]["status"] = "exec"
            elif prevProcessLine == 2:
                ns.entering[i] = False # entering[i] = false
                ns.process_states[i]["line"] = 3
            elif prevProcessLine == 3:
                if not ns.entering[j]:  # if while condition is NOT met, we can go to next wait
                        ns.process_states[i]["status"] = "wait2"
                        ns.process_states[i]["line"] = 4
                else:  # while condition still holds, we must wait
                    ns.process_states[i]["status"] = "wait1"
                    ns.process_states[i]["line"] = 3
            elif prevProcessLine == 4:
                if not ((ns.number[j] != 0) and ((ns.number[j],j) < (ns.number[i],i)) ): # WHILE condition is not met, next iteration or Critical section
                    if j == ns.n-1:
                        ns.process_states[i]["line"] = 5
                        ns.process_states[i]["status"] = "critical"
                    else:
                        ns.process_states[i]["line"] = 0
                        ns.process_states[i]["it"] = j + 1
                else:
                    ns.process_states[i]["status"] = "wait2"
                    ns.process_states[i]["line"] = 4
            elif prevProcessLine == 5:
                ns.process_states[i]["line"] = 6
                ns.process_states[i]["status"] = "exec"
            elif prevProcessLine == 6:
                ns.number[i] = 0
                ns.process_states[i]["line"] = 0
                ns.process_states[i]["it"] = 0

            sc.append(ns)
        return sc

    def constructChildState(self):
        ns = LamportState(self.n)
        ns.parent_id = self.id
        ns.entering = copy.deepcopy(self.entering)
        ns.number = copy.deepcopy(self.number)
        ns.process_states = []
        for ps in self.process_states:
            ns.process_states.append(copy.deepcopy(ps))  # necessary deepcopy of dict
        return ns

    def simpleString(self):
        out = f"{self.entering} {self.number}\\n"
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
            elif pState["status"] == "wait1":
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
        return f"---\nState {self.id} \n\tEntering - {self.entering} \n\tnumber - {self.number} \n\tpstates - {self.process_states} \n"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        levelEQ = self.entering == other.entering
        lteEQ = self.number == other.number
        processEQ = True
        for i in range(len(self.process_states)):
            processEQ = processEQ & (self.process_states[i]["it"] == other.process_states[i]["it"])
            processEQ = processEQ & (self.process_states[i]["line"] == other.process_states[i]["line"])
        return levelEQ & lteEQ & processEQ

    def __hash__(self):
        return 0  # (I think) hash is not used, so we can return 0; implemented to allow set() to work
