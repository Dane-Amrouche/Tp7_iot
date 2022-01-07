import time
import json
import threading
import paho.mqtt.client as mqtt_client
import os
import sys
import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime
from uuid import getnode as get_mac
import shutter
import temperature_sensor
import luminosity_sensor
import presence_sensor
import light_actuator
import heater_actuator
import connected_led

GPIO.setmode(GPIO.BCM)
MQTT_SERVER = "10.42.0.1"
MQTT_PORT = 1883

def get_date_time():
    weekdays= ("Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche")
    # detect time and the day
    time = datetime.now().strftime("%H:%M")
    date = datetime.today().weekday()
    print(weekdays[date], time)
    return (weekdays[date],time)

# instanciation of materials :
# 1. light sensor
MQTT_PUB_TOPIC = "salle14/Luminosity"
MQTT_SUB_TOPIC = "salle14/Luminosity/command"
 
unitID = get_mac()
subID = 57
thread = threading.Thread(target=luminosity_sensor.Luminosity_sensor,args=(unitID,subID,MQTT_PUB_TOPIC,MQTT_SUB_TOPIC,MQTT_SERVER,MQTT_PORT))
thread.start()


# 2. temperature sensor
MQTT_PUB_TOPIC = "salle14/Temperature"
MQTT_SUB_TOPIC = "salle14/Temperature/command"

unitID = get_mac()
subID = 24
thread = threading.Thread(target=temperature_sensor.Temperatue_sensor, args=(unitID,subID,MQTT_PUB_TOPIC,MQTT_SUB_TOPIC,MQTT_SERVER,MQTT_PORT))
thread.start()
    
# 3. the shutter
MQTT_PUB_TOPIC = "salle14/shutter"
MQTT_SUB_TOPIC = "salle14/shutter/command"

unitID = "center"
thread = threading.Thread(target=shutter.Shutter, args=(unitID,MQTT_PUB_TOPIC,MQTT_SUB_TOPIC,MQTT_SERVER,MQTT_PORT))
thread.start()

# 4. presence detector
MQTT_PUB_TOPIC = "salle14/Presence"
MQTT_SUB_TOPIC = "salle14/Presence/command"

unitID = get_mac() 
subID = 120
pin = 22
thread = threading.Thread(target=presence_sensor.Presence_sensor, args=(pin, unitID, subID, MQTT_PUB_TOPIC, MQTT_SERVER, MQTT_PORT, MQTT_SUB_TOPIC))
thread.start()

# 5. lights
Type ="light"
PIN_LIGHT = 20
unitID = "led"
GPIO.setup(PIN_LIGHT,GPIO.OUT) 
GPIO.output(PIN_LIGHT,GPIO.LOW)
MQTT_SUB_LIGHT = "salle14/light/command"
thread = threading.Thread(target=connected_led.Connected_led, args=(unitID, None,MQTT_SUB_LIGHT,MQTT_SERVER,MQTT_PORT,Type, PIN_LIGHT))
thread.start()

# 6. heater
Type="heater"
PIN_HEATER = 26
unitID = "heater"
GPIO.setup(PIN_HEATER,GPIO.OUT)  
GPIO.output(PIN_HEATER,GPIO.LOW)
MQTT_SUB_HEATER = "salle14/Heater/command"
thread = threading.Thread(target=connected_led.Connected_led, args=(unitID, None,MQTT_SUB_HEATER,MQTT_SERVER,MQTT_PORT,Type, PIN_HEATER))
thread.start()

# the core function of the Actuators
# 1. light actuator
MQTT_PUB_SHUTTER = "salle14/shutter/command"
MQTT_SUB_SHUTTER = "salle14/shutter"
MQTT_PUB_LUM = "salle14/Luminosity/command"
MQTT_SUB_LUM = "salle14/Luminosity"
MQTT_SUB_PRESENCE = "salle14/Presence"
MQTT_PUB_ALARM = "Security/Alarm"
MQTT_PUB_LIGHT = "salle14/light/command"
presence_sensor_subID = 120
luminosity_sensor_subID = 57
shutter_unitID = "center"

# declare the 3 shutters in our class
unitID = get_mac()
subID = 125
thread = threading.Thread(target=light_actuator.Light_actuator, args=(unitID, MQTT_PUB_SHUTTER,MQTT_SUB_SHUTTER,MQTT_SERVER,MQTT_PORT,MQTT_PUB_LUM, MQTT_SUB_LUM,
                                    MQTT_SUB_PRESENCE,MQTT_PUB_ALARM,MQTT_PUB_LIGHT,presence_sensor_subID,luminosity_sensor_subID,shutter_unitID))

thread.start()

# 2. heat actuator
MQTT_PUB_TOPIC = "salle14/Temperature/command"
MQTT_SUB_TOPIC = "salle14/Temperature"
MQTT_PUB_HEATER = "salle14/Heater/command"

# declare the 3 shutters in our class
unitID = get_mac()
subID = 110
seuil_min = 19
seuil_max = 22
thread = threading.Thread(target=heater_actuator.Heater_actuator, args=(unitID,MQTT_PUB_TOPIC,MQTT_SUB_TOPIC,MQTT_SERVER,MQTT_PORT,seuil_min,seuil_max,MQTT_PUB_HEATER))
thread.start()

def main():
    pass
# Execution or import
if __name__ == "__main__":
    main() 

