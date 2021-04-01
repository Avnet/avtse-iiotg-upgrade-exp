global MySensor

def __init__(self,myglobals):
    globals().update(myglobals)

def MySensor(value):
    # all voltages are positive so remove zero point counts.  Whats left is 0 - 10 volt range counts or 4 to 20 ma counts
    value = float(value)
    value = value - float(32768)
    # range
    value = value + float(my_config_parser_dict['IoTFnPluginMySensor']['offset'])
    value = (value / float(32768)) * float(my_config_parser_dict['IoTFnPluginMySensor']['range_high'])
    return value

