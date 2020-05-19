import abc
from SystemState import SystemState

class HaltCondition(abc.ABC):
    @abc.abstractmethod
    def update_and_check(self,current_system_state:SystemState):
        pass

    def __and__(self, other):
        return Or_OfTwoHaltConditions(self,other)

    def __or__(self, other):
        return And_OfTwoHaltConditions(self, other)

class Or_OfTwoHaltConditions(HaltCondition):
    cond1: HaltCondition
    cond2: HaltCondition
    def __init__(self,cond1: HaltCondition, cond2: HaltCondition):
        self.cond1 = cond1
        self.cond2 = cond2

    def update_and_check(self, current_system_state: SystemState):
        return self.cond1.update_and_check(current_system_state) or self.cond2.update_and_check(current_system_state)

class And_OfTwoHaltConditions(HaltCondition):
    cond1: HaltCondition
    cond2: HaltCondition
    def __init__(self,cond1: HaltCondition, cond2: HaltCondition):
        self.cond1 = cond1
        self.cond2 = cond2

    def update_and_check(self, current_system_state: SystemState):
        return self.cond1.update_and_check(current_system_state) and self.cond2.update_and_check(current_system_state)
