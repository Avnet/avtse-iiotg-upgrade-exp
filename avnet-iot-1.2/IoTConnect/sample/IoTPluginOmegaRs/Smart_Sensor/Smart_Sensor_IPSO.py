# IPSO Definitions

def Measurement_Type(type):
    '''
    Converts IPSO sensor type to string
    '''
    return (Ipso_Types.get(type))

Ipso_Types = {3200: "DIGITAL_INPUT"}

Ipso_Types[3201] = "DIGITAL_OUTPUT"
Ipso_Types[3202] = "ANALOG_INPUT"
Ipso_Types[3203] = "ANALOG_INPUT"
Ipso_Types[3300] = "GENERIC_SENSOR"
Ipso_Types[3301] = "LUMINANCE"
Ipso_Types[3302] = "PRESENCE"
Ipso_Types[3303] = "TEMPERATURE"
Ipso_Types[3304] = "HUMIDITY"
Ipso_Types[3305] = "POWER_MANAGEMENT"
Ipso_Types[3306] = "ACTUATION"
Ipso_Types[3308] = "SETPOINT"
Ipso_Types[3310] = "LOAD_CONTROL"
Ipso_Types[3311] = "LIGHT_CONTROL"
Ipso_Types[3312] = "POWER_CONTROL"
Ipso_Types[3313] = "ACCELEROMETER"
Ipso_Types[3314] = "MAGNETOMETER"
Ipso_Types[3315] = "BAROMETER"
Ipso_Types[3316] = "VOLTAGE"
Ipso_Types[3317] = "CURRENT"
Ipso_Types[3318] = "FREQUENCY"
Ipso_Types[3319] = "DEPTH"
Ipso_Types[3320] = "PERCENTAGE"
Ipso_Types[3321] = "ALTITUDE"
Ipso_Types[3322] = "LOAD"
Ipso_Types[3323] = "PRESSURE"
Ipso_Types[3324] = "LOUDNESS"
Ipso_Types[3325] = "CONCENTRATION"
Ipso_Types[3326] = "ACIDITY"
Ipso_Types[3327] = "CONDUCTIVITY"
Ipso_Types[3328] = "POWER"
Ipso_Types[3329] = "POWER_FACTOR"
Ipso_Types[3330] = "DISTANCE"
Ipso_Types[3331] = "ENERGY"
Ipso_Types[3332] = "DIRECTION"
Ipso_Types[3333] = "TIME"
Ipso_Types[3334] = "GYROMETER"
Ipso_Types[3335] = "COLOUR"
Ipso_Types[3336] = "LOCATION"
Ipso_Types[3337] = "POSITIONER"
Ipso_Types[3338] = "BUZZER"
Ipso_Types[3339] = "AUDIO_CLIP"
Ipso_Types[3340] = "TIMER"
Ipso_Types[3341] = "ADDRESSABLE_TEXT_DISPLAY"
Ipso_Types[3342] = "ON_OFF_SWITCH"
Ipso_Types[3343] = "DIMMER"
Ipso_Types[3344] = "UP_DOWN_CONTROL"
Ipso_Types[3345] = "MULTI_AXIS_JOYSTICK"
   
Ipso_Types[3346] = "RATE"
Ipso_Types[3347] = "PUSH_BUTTON"
Ipso_Types[3348] = "MULTI_STATE_SELECTOR"
Ipso_Types[3349] = "BIT_MAPPED_DIN"

Ipso_Types[33001] = "OMEGA_PWM_OUT"
Ipso_Types[33002] = "OMEGA_COUNTER"
Ipso_Types[33003] = "OMEGA_UP_DOWN_COUNTER"
Ipso_Types[33004] = "OMEGA_QUAD_COUNTER"
Ipso_Types[33005] = "OMEGA_PULSE_WIDTH"
Ipso_Types[33006] = "OMEGA_PULSE_DELAY"
Ipso_Types[33007] = "OMEGA_DUTY_CYCLE"
Ipso_Types[33005] = "OMEGA_PULSE_WIDTH"

Ipso_Types[33100] = "OMEGA_USER_PARAMETER"
Ipso_Types[33110] = "OMEGA_FUNCTION_BLOCK"

