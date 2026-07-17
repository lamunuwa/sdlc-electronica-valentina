from enum import Enum, auto


class TrafficLightState(Enum):
    RED = auto()
    YELLOW = auto()
    GREEN = auto()


# El codigo en la guia de estudios presentaba un warning, usaba ; para dividir las instancias RED,
# YELLOW y GREEN, lo cual es inneficiente y no es una buena practica. Lo he modificado para que sea
# mas legible y correcto.


class TrafficLightFSM:
    # El estado vive dentro del objeto, no en una variable global.
    def __init__(self) -> None:
        self._state = TrafficLightState.RED
        self._cycle_count = 0

    @property
    def state(self) -> TrafficLightState:
        return self._state

    def transition(self) -> TrafficLightState:
        transitions = {
            TrafficLightState.RED: TrafficLightState.GREEN,
            TrafficLightState.GREEN: TrafficLightState.YELLOW,
            TrafficLightState.YELLOW: TrafficLightState.RED,
        }
        self._state = transitions[self._state]
        self._cycle_count += 1
        return self._state
