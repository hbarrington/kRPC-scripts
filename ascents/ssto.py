# Single stage to orbit launch
# - Open logging
#     - Time, alt, pos, thrust, vel
# - Open plotting
#     - Time, alt, pos, thrust, vel
# - Throttle up
# - Stage
# - Confirm available trust = actual thrust
# - Stage
# - Timed delay (8s)
#     - Pitch program
#         - TWR-pitch LUT
#         - Slow pitch
#         - Zero AoA
#     - Throttle program
#         - Discrete throttle back at high Q
#         - _or_ at high G
# - Low Q reached
# - Fairing dump at altitude
# - Pitch program
#     - Limited AoA to control TtA
# - MECO at target Ap
# - Circularize

import krpc
import time

# Params
throttle_min = 0.7
turn_ang = 3
aerodynamic_alt = 30e3
fairing_alt = 50e3

# Setup
conn = krpc.connect(name="stdasc")
vessel = conn.space_center.active_vessel
flight = vessel.flight()

# Liftoff
vessel.auto_pilot.target_pitch_and_heading(90, 90)
vessel.auto_pilot.target_roll = 180
vessel.auto_pilot.engage()
vessel.control.throttle = 1
time.sleep(1)
print("All systems go")
vessel.control.activate_next_stage()
print("Engine start")
time.sleep(2)
vessel.control.activate_next_stage()
print("Liftoff")

# Turn
alt = conn.get_call(getattr, vessel.flight(), 'surface_altitude')
expr = conn.krpc.Expression.greater_than(
    conn.krpc.Expression.call(alt),
    conn.krpc.Expression.constant_double(500))
event = conn.krpc.add_event(expr)
with event.condition:
    event.wait()
vessel.auto_pilot.target_pitch_and_heading(90 - turn_ang, 90)
time.sleep(5)

# Zero AoA
vessel.auto_pilot.reference_frame = vessel.surface_velocity_reference_frame
vessel.auto_pilot.target_direction = (0, 1, 0)

# Throttle back to avoid drag
g_force = conn.get_call(getattr, flight, 'g_force')
expr = conn.krpc.Expression.greater_than(conn.krpc.Expression.call(g_force),
                                         conn.krpc.Expression.constant_float(3.0))
event = conn.krpc.add_event(expr)
with event.condition:
    event.wait()
print("Throttling back")
vessel.control.throttle = throttle_min
