import numpy as np


def decide_acceleration(pos, v, len, v_max, a_max, d_max):
    distance_remaining = len - pos
    if v > 0:
        stopping_distance = np.power(v, 2) / (2 * d_max)
    else:
        stopping_distance = 0

    if distance_remaining <= stopping_distance:
        # need to decelerate to stop in time
        return -d_max
    elif v < v_max:
        # can keep accelerating up to max velocity
        return a_max
    else:
        # continue to cruise at max velocity
        return 0


def power_required(
    acceleration, velocity, drag, rolling_resistance, incline, mass, frontal_area
):
    # power equation from Julian's document
    # unsure about negative incline here
    power = 0.6125 * frontal_area * drag * np.power(
        velocity, 3
    ) + 9.81 * mass * velocity * (rolling_resistance + incline + 0.107 * acceleration)
    return power
