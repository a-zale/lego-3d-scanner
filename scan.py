# This code gets run on the Spike hub (microcontroller) using the Spike app:
# https://education.lego.com/en-us/downloads/spike-app/software/

import motor
import force_sensor
import color_sensor
from hub import motion_sensor
import runloop
from runloop import until
from hub import port
from hub import sound
from hub import button
from app import linegraph
import color
import sys
import time

## globals
MOTOR_PORT = {
    'x' : port.C,
    'y' : port.B,
    'z' : port.A
}

SENSOR_PORT = {
    'x' : port.E,
    'y' : port.D,
    'z' : port.F
}

# note: for x,y,z, pos=0 is the initial position set by user, and clockwise => increasing pos => torward touch/light sensor being triggered
MAX_SPEED = {
    'x' : 600,
    'y' : 600,
    'z' : 400
}

# bool functions
SENSOR = {
    'x' : lambda : color_sensor.color(SENSOR_PORT['x']) is color.AZURE,
    'y' : lambda : color_sensor.color(SENSOR_PORT['y']) is color.AZURE,
    'z' : lambda : force_sensor.pressed(SENSOR_PORT['z']),
    'g' : lambda : motion_sensor.tilt_angles()[1]>100 or motion_sensor.tilt_angles()[1]<-100,
    'r' : lambda : color_sensor.color(SENSOR_PORT['x']) is color.RED
}

# position at which force/light sensor gets triggered
MAX_POS = {
    'x' : 0,
    'y' : 0,
    'z' : 0
}

INCREMENT = {
    'x' : 10, # 20
    'y' : 10, # 20
    'z' : None
}

COLOR = {
    'x' : color.BLACK,
    'y' : color.GREEN,
    'z' : color.RED
}

TIMEOUT = 10 * 1000

XYZ = ['x', 'y', 'z']

# not technically constant, these messages will get set to True at most once
FAULT_DETECTED = False # stop everything and exit now
STOP_EARLY = False # reset to initial position then exit

def chime():
    return sound.beep(523, 500)

# moves until the sensor is triggered, sets MAX_POS, then moves back
async def init(xyz):
    global MAX_POS
    m = MOTOR_PORT[xyz]
    v = MAX_SPEED[xyz]

    motor.reset_relative_position(m, 0) # from now on, relative_position == 0 will be the reference position; won't raise the probe above this
    motor.run(m, v//2)
    await until(SENSOR[xyz], timeout=TIMEOUT)
    motor.stop(m)
    chime()
    MAX_POS[xyz] = motor.relative_position(m)
    print("Max ",xyz,": ", MAX_POS[xyz])
    await reset(xyz)
    motor.stop(m)
    await chime()

async def increment(xyz):
    m = MOTOR_PORT[xyz]
    await motor.run_for_degrees(m, INCREMENT[xyz], MAX_SPEED[xyz]//2)
    motor.stop(m)

# return to initial position set by user
async def reset(xyz):
    await motor.run_to_relative_position(MOTOR_PORT[xyz], 0, -MAX_SPEED[xyz])

# collect a datapoint
# x,y,z in degrees
async def probe(i, x, y):
    m = MOTOR_PORT['z']
    v = MAX_SPEED['z']
    motor.run(m, v//2)
    await until(lambda : SENSOR['z']() or STOP_EARLY, timeout=TIMEOUT)
    if STOP_EARLY:
        motor.stop(m)
        await reset('z')
        return
    motor.stop(m)
    z = MAX_POS['z'] - motor.relative_position(m)
    print(x, y, z)
    linegraph.plot(COLOR['x'], i, x)
    linegraph.plot(COLOR['y'], i, y)
    linegraph.plot(COLOR['z'], i, z)
    await reset('z')

async def user_stop():
    global STOP_EARLY
    await until(lambda : button.pressed(button.LEFT) == 1 or button.pressed(button.RIGHT) == 1 or SENSOR['r']())
    STOP_EARLY = True
    print("Stopping early because user requested")
    await chime()
    # the rest is handled in probe() and main()

async def gyro_stop():
    global FAULT_DETECTED
    await until(SENSOR['g'])
    FAULT_DETECTED = True
    print("Stopping because pitch measures ", motion_sensor.tilt_angles()[1]//10, " degrees")
    for xyz in XYZ:
        motor.stop(MOTOR_PORT[xyz])
    await chime()
    sys.exit()

async def main():
    linegraph.clear_all()
    #linegraph.show(fullscreen=True)
    for xyz in XYZ:
        await init(xyz)

    i = 0
    #linegraph.show(fullscreen=True)
    Nx = MAX_POS['x']//INCREMENT['x']
    Ny = MAX_POS['y']//INCREMENT['y']
    N = Nx * Ny
    for nx in range(Nx):
        if SENSOR['x']() or STOP_EARLY:
            break
        await increment('x')
        for ny in range(Ny):
            if SENSOR['y']() or STOP_EARLY:
                break
            await increment('y')
            await probe(i, nx*INCREMENT['x'], ny*INCREMENT['y'])
            linegraph.show(fullscreen=False)
            i += 1
            print("Progress:", (i*100) // N, "%")
            print()
        await reset('y')

    await reset('x')
    await chime()

    sys.exit(0)


runloop.run(main(), user_stop(), gyro_stop())
