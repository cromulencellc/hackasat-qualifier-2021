# Temperature Sensor
# If temperature above/below threshold, deactivate/activate heater
import sys

def readTemp(temp,state):
    if temp < 15 and not state:
        print("Temp: %.2fC Activating heater"%temp)
        return 1
    elif temp > 35 and state:
        print("Temp: %.2fC Deactivating heater"%temp)
        return 0
    else:
        return state