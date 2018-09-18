#View the README for an explanation of how this design works

import pyrtl

#INPUT WIRES
buttonPressed = pyrtl.Input(2, 'IN-buttonPressed') #this will either be 00 if not pressed or 01 if pressed
closedSwitch = pyrtl.Input(2, 'IN-closedSwitch') #has the same action as button pressed
openedSwitch = pyrtl.Input(2, 'IN-openedSwitch') #has the same action as button pressed
sensor = pyrtl.Input(2, 'IN-sensor') # this will be 00 or 10 - only if the garage is closing

#WIRE VECTORS
input_A = pyrtl.WireVector(2, 'W-input_A')# this wire will take the button and switch input and move it to the adder
input_B = pyrtl.WireVector(2, 'W-input_B')#this wire will take the sensor input and move it to the adder

#OUTPUT WIRES
pausing = pyrtl.Output(2, 'OUT-pausing') # when state is CLOSED or OPENED the output is pausing which stops the motor
opening = pyrtl.Output(2, 'OUT-opening') # when state is OPENING the output is opening
closing = pyrtl.Output(2, 'OUT-closing') # when state is CLOSING the output is closing

#REGISTER
state = pyrtl.Register(bitwidth = 2, name = 'R-state')#this two bit register holds the current state

#CONSTANTS
CLOSED, OPENING, OPENED, CLOSING = [pyrtl.Const(x, bitwidth=2) for x in range(4)]
#these constants represent each state, 00 is closed/pause, 01 is opening, 10 is opened/pause, 11 is closing

input_A <<= (buttonPressed | closedSwitch | openedSwitch) #only one needs to be true to increment the state

input_B <<= 2*(sensor & (state == CLOSING)) #only triggered when the sensor detects something while closing
#There is a 2* because this  input needs to represent two if the statement is true. In the logic diagram
#this input is one bit and goes to the 2^1 place in the adder because that would be like adding a 10
#in binary or 2 in decimal. However for simplicity this wire holds two bits and will just be 2* the
#result, which is 0 or 1, and makes 0 or two.

assert len(buttonPressed) == len(state) == len(input_A) == len(input_B) == 2 #make sure you can add these numbers

sum = input_A + input_B + state
#add the current state to the input, essentially move it up by one or two.
# You can only have input_A or input_B  but not both

state.next <<= sum #the next state is the result of the addition

pausing <<= (state == CLOSED) | (state == OPENED) #the pause output is true if the state is equivelant to CLOSED or OPEN
opening <<= state == OPENING #the open output is true if the state is equivilant to OPENING
closing <<= state == CLOSING #the close output is true if the state is equivelent to CLOSING

print('--- Garage door implementation ---')
print(pyrtl.working_block())
print()

sim_trace = pyrtl.SimulationTrace()
sim = pyrtl.Simulation(tracer=sim_trace)

sim_inputs = {
    #our inputs cannot be random, they must be realistic. For example, you cannot
    #have multiple inputs be true. Either the button is pressed, a switch is triggered,
    #or the sensor is triggered. So in this example the input is first the button is pressed
    #which will open the garage. Then the Opened switch is triggered so the garage is open.
    #Then the button is pressed again to close the garage. Then the sensor detects something
    #causing the garage to open. Then the button is pressed to "Pause" then pressed again
    #to close and then the closed switch is triggered
    'IN-buttonPressed': '10101100',
    'IN-openedSwitch':  '01000000',
    'IN-closedSwitch':  '00000010',
    'IN-sensor':        '00010000'
}

for cycle in range(8):
    sim.step({w: int(v[cycle]) for w, v in sim_inputs.items()})

sim_trace.render_trace(symbol_len=10, segment_size=1)

#In the rendering of the simulation, the input is one cycle ahead of the output.
#This is because the output is a result of the state not the input and it takes one
#clock cycle for the state to change. For example in cycle 0 the state is 00 which is
#pausing (closed/ opened/ paused) and our input is button pressed. The state will only change to
#01 next clock cycle because registers depend on the rising edge of the clock in order to change.
#The output is in sync with the state, not the input, so we only see it change with the state.