import math
import numpy as np


def process_segment(segment_length, segment_elev_change, parameters):
    # set up initial variables for segment processing
    dt = 0.1
    position = 0
    segment_time = 0
    velocity = 0
    segment_energy = 0
    acceleration = 0
    
    # get the variables out of the parameters dict
    max_velocity = parameters['max_velocity']

    # calculate the incline of the segment
    incline = calculate_incline(segment_length, segment_elev_change)

    while position < segment_length:
        # decide whether the vehicle is accelerating or decelerating
        acceleration = decide_acceleration(position, velocity, segment_length, parameters)

        # update velocity and position
        # cap velocity between zero and max velocity
        velocity = max(0, min(velocity + acceleration * dt, max_velocity))

        # predict next position to ensure no overshoot
        next_position = position + velocity * dt

        # adjust if overshoot is going to happen
        if next_position >= segment_length:
            remaining_distance = segment_length - position
            if velocity > 0:
                fractional_dt = remaining_distance/velocity
            else:
                fractional_dt = dt

            # update power using the fractional_dt left to reach end of segment
            power = power_required(acceleration, velocity, incline, parameters)
            if power > 0:
                segment_energy += power * fractional_dt

            # update time using fractional dt
            segment_time += fractional_dt
            position = segment_length
            break
        else:
            # if theres no overshoot then can update as usual
            position = next_position
            segment_time += dt
            power = power_required(acceleration, velocity, incline, parameters)
            if power > 0:
                segment_energy += power * dt

    return segment_energy, segment_time


def decide_acceleration(position, velocity, current_acceleration, segment_length, parameters):
    # determing target acceleration considering jerk limits and stopping distance
    
    # get the required variables out of the parameters dict
    max_velocity = parameters['max_velocity']
    max_accel = parameters['max_accel']
    max_jerk = parameters['max_jerk']

    # calculate remaining distance given current position
    distance_remaining = segment_length - position

    # calculate the current stopping distance allowing for the impact of jerk
    current_stopping_distance = calculate_stopping_distance(velocity, current_acceleration, max_accel, max_jerk)

    if distance_remaining <= current_stopping_distance:
        # need to start decelerating to stop in time
        return -decel_max
    elif v < v_max:
        # can keep accelerating up to max velocity
        return a_max
    else:
        # continue to cruise at max velocity
        return 0
    

def calculate_stopping_distance(velocity, current_accel, max_accel, max_jerk):
    if velocity <= 0:
        return 0
    
    target_decel = -max_accel
    
    # calculate the time and distance in the phase affected by jerk
    if current_accel > target_decel:
        jerk_phase_time = (current_accel - max_accel) / max_jerk
        jerk_phase_distance = ((velocity * jerk_phase_time) + (0.5 * current_accel * jerk_phase_time**2) - ((1/6) * max_jerk * jerk_phase_time**3))
        velocity_after_jerk_phase = (velocity + (current_accel * jerk_phase_time) - (0.5 * max_jerk * jerk_phase_time**2))
    else:
        # already at or beyond max decel, then there is no jerk phase
        jerk_phase_time = 0
        jerk_phase_distance = 0
        velocity_after_jerk_phase = 0

    if velocity_after_jerk_phase > 0:
        # this is just that standard equation that I do need to find from somewhere to justify
        constant_decel_distance = -velocity_after_jerk_phase**2 / (2*target_decel)
    else:
        constant_decel_distance = 0

    # combine the jerk phase with the constant decel phase distances
    total_stopping_distance = jerk_phase_distance + constant_decel_distance
    # this could have a margin of error added to it if necessary but keeping it raw for now
    return constant_decel_distance

def power_required(acceleration, velocity, incline, parameters):
    drag = parameters["drag"]
    rolling_resistance = parameters["rolling_resistance"]
    mass = parameters["mass"]
    frontal_area = parameters["frontal_area"]
    # power equation from Julian's document
    # unsure about negative incline here
    power = 0.6125 * frontal_area * drag * np.power(
        velocity, 3
    ) + 9.81 * mass * velocity * (rolling_resistance + incline + 0.107 * acceleration)
    return power
    

def calculate_incline(run, rise):
    if run == 0:
        return 0 # avoid zero division error
    return(math.atan(rise/run))
