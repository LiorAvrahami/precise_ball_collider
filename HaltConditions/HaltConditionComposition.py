import abc
from SystemState import SystemState
from typing import Tuple, Optional


class HaltCondition(abc.ABC):

    @abc.abstractmethod
    def add_new_system_state(self, current_system_state):
        pass

    @abc.abstractmethod
    def update_and_check(self, current_system_state: SystemState) -> Tuple[bool, Optional[SystemState]]:
        """
        recives a new system state, and returns whether or not the halt condition was met, and also returns the most advanced SystemState that dose satisfy the halt condition.
        :param current_system_state:
        """
        pass

    def __and__(self, other):
        return And_OfTwoHaltConditions(self, other)

    def __or__(self, other):
        return Or_OfTwoHaltConditions(self, other)


class HaltConditionComposition(HaltCondition):
    cond1: HaltCondition
    cond2: HaltCondition

    def add_new_system_state(self, current_system_state):
        self.cond1.add_new_system_state(current_system_state)
        self.cond2.add_new_system_state(current_system_state)

    def __init__(self, cond1: HaltCondition, cond2: HaltCondition):
        self.cond1 = cond1
        self.cond2 = cond2


class Or_OfTwoHaltConditions(HaltConditionComposition):

    def update_and_check(self, current_system_state: SystemState) -> Tuple[bool, Optional[SystemState]]:
        ret1 = self.cond1.update_and_check(current_system_state)
        ret2 = self.cond2.update_and_check(current_system_state)
        if ret1[0] or ret2[0]:
            if ret1[0] and ret2[0]:
                t1, t2 = ret1[1].time, ret2[1].time
                if t1 < t2:
                    return ret1
                else:
                    return ret2
            if ret1[0]:
                return ret1
            else:
                return ret2
        return False, None


class And_OfTwoHaltConditions(HaltConditionComposition):

    def update_and_check(self, current_system_state: SystemState) -> Tuple[bool, Optional[SystemState]]:
        ret1 = self.cond1.update_and_check(current_system_state)
        ret2 = self.cond2.update_and_check(current_system_state)
        if ret1[0] and ret2[0]:
            t1, t2 = ret1[1].time, ret2[1].time
            if t1 > t2:
                return ret1
            else:
                return ret2
        return False, None
