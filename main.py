import shutter


def main():
    MQTT_SERVER = "10.42.0.1"
    MQTT_PORT = 1883
    MQTT_PUB_TOPIC = "salle4/shutter"
    MQTT_SUB_TOPIC = "salle14/shutter/command"

    # declare the 3 shutters in our class
    unitID = "center"
    con = shutter.Shutter(unitID,MQTT_PUB_TOPIC,MQTT_SUB_TOPIC,MQTT_SERVER,MQTT_PORT)
    return 0


# Execution or import
if __name__ == "__main__":
    main()