from semana1.fsm_demo import (
    TrafficLightState,
    TrafficLightFSM
)

def test_initial_state():
    fsm = TrafficLightFSM()
    assert fsm.state == TrafficLightState.RED

def test_transition_red_to_green():
    fsm = TrafficLightFSM()
    fsm.transition() # RED -> GREEN
    assert fsm.state == TrafficLightState.GREEN

def test_full_cycle():
    fsm = TrafficLightFSM()
    fsm.transition()  # RED -> GREEN
    fsm.transition()  # GREEN -> YELLOW
    fsm.transition()  # YELLOW -> RED
    assert fsm.state == TrafficLightState.RED

def test_cycle_count():
    fsm = TrafficLightFSM()
    fsm.transition()
    fsm.transition()
    fsm.transition() 
    assert fsm._cycle_count == 3  # _cycle_count en fsm_demosuma 1 cada que usamos fsm.transition() por eso es 3