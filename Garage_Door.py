# View the README for an explanation of how this design works.

import pyrtl

# These are the four input wires. The buttonPressed, closedSwitch, and openedSwitch all
# have the same function and will be either 00 or 01. The sensor input will also be either
# a 00 or a 01 - however it can only be 01 when the current state is CLOSING.
buttonPressed = pyrtl.Input(2, 'IN-buttonPressed')
closedSwitch = pyrtl.Input(2, 'IN-closedSwitch')
openedSwitch = pyrtl.Input(2, 'IN-openedSwitch')
sensor = pyrtl.Input(2, 'IN-sensor')

# These are two general wire vecors that will take the input and move it to the adder.
# Input_A will be the result of buttonPressed, closedSwitch, or openedSwitch. Input_B
# will be the result of sensor if the state is CLOSING.
input_A = pyrtl.WireVector(2, 'W-input_A')
input_B = pyrtl.WireVector(2, 'W-input_B')

# These are the output wires which describe the action of the motor driver. The motor driver
# can be direct the motor to be pause, open or close. These output wires are a result of the
# current state, not the input.
pausing = pyrtl.Output(2, 'OUT-pausing')
opening = pyrtl.Output(2, 'OUT-opening')
closing = pyrtl.Output(2, 'OUT-closing')

# This is a two bit register which will hold the current state.
state = pyrtl.Register(bitwidth=2, name='R-state')  # this two bit register holds the current state

# These constants represent each state: 00 is closed/pause, 01 is opening, 10 is opened/pause, 11 is closing.
CLOSED, OPENING, OPENED, CLOSING = [pyrtl.Const(x, bitwidth=2) for x in range(4)]

# This wire vector is the result of oring these three inputs.
input_A <<= (buttonPressed | closedSwitch | openedSwitch)

# The sensor is only triggered when it detects something while the state is CLOSING.
# There is a 2* because this  input needs to represent two if the statement is true. In the logic diagram
# this input is one bit and goes to the 2^1 place in the adder because that would be like adding a 10
# in binary or 2 in decimal. However for simplicity this wire holds two bits and will just be 2* the
# result, which is 0 or 1, and makes 0 or two.
input_B <<= 2 * (sensor & (state == CLOSING))

# We must make sure you can add these numbers.
assert len(buttonPressed) == len(state) == len(input_A) == len(input_B) == 2

# Here we add the current state to the input which will have the effect
# of incrementing the state based on the input.
sum = input_A + input_B + state

# Here the state increments.
state.next <<= sum

# These three output wires are dependent on the current state. Only one can be true.
pausing <<= (state == CLOSED) | (state == OPENED)
opening <<= state == OPENING
closing <<= state == CLOSING

# This is where the simulation begins.
print('--- Garage door implementation ---')
print(pyrtl.working_block())
print()

sim_trace = pyrtl.SimulationTrace()
sim = pyrtl.Simulation(tracer=sim_trace)

# Our inputs cannot be random, they must be realistic. For example, you cannot
# have multiple inputs be true. Either the button is pressed, a switch is triggered,
# or the sensor is triggered. So in this example the input is first the button is pressed
# which will open the garage. Then the Opened switch is triggered so the garage is open.
# Then the button is pressed again to close the garage. Then the sensor detects something
# causing the garage to open. Then the button is pressed to "Pause" then pressed again
# to close and then the closed switch is triggered.
sim_inputs = {
    'IN-buttonPressed': '10101100',
    'IN-openedSwitch': '01000000',
    'IN-closedSwitch': '00000010',
    'IN-sensor': '00010000'
}

for cycle in range(8):
    sim.step({w: int(v[cycle]) for w, v in sim_inputs.items()})

sim_trace.render_trace(symbol_len=10, segment_size=1)

# In the rendering of the simulation, the input is one cycle ahead of the output.
# This is because the output is a result of the state not the input and it takes one
# clock cycle for the state to change. For example in cycle 0 the state is 00 which is
# pausing (closed/ opened/ paused) and our input is button pressed. The state will only change to
# 01 next clock cycle because registers depend on the rising edge of the clock in order to change.
# The output is in sync with the state, not the input, so we only see it change with the state.
