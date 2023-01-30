import copy

stateCounter = 0

class PetersonState:
    def __init__(self, n):
        global stateCounter
        self.n = n
        self.levels = [-1]*n
        self.last_to_enter = [0]*(n-1)
        self.process_states = [{"it":0,"line":0,"status":"exec"}]*n
        self.children:[PetersonState] = []
        self.id = stateCounter
        self.parent_id = -1
        stateCounter+=1

    def getSuccessors(self):
        parentId = self.id
        sc = []

        for i in range(len(self.process_states)):
            processState = self.process_states[i]
            prevProcessLine = processState["line"]
            l = processState["it"]  # process' iteration counter
            ns = self.constructChildState()
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
                    if l < ns.n - 2:  # if we are not at the last iteration, we can go to next iteration
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

    def constructChildState(self):
        ns = PetersonState(self.n)
        ns.parent_id = self.id
        ns.levels = copy.deepcopy(self.levels)
        ns.last_to_enter = copy.deepcopy(self.last_to_enter)
        ns.process_states = []
        for ps in self.process_states:
            ns.process_states.append(copy.deepcopy(ps))  # necessary deepcopy of dict
        return ns

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
