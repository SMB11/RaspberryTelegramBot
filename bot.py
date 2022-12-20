import paho.mqtt.client as mqtt
import requests
import json
import _thread
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
#mosquitto broker url (ip)
broker_url = "192.168.0.106"
#mosquitto broker url (ip)
broker_port = 1883
#mqtt topic for get insideTemperature value
mqtt_topic_sensors = "Main_Controller_sensors"

#mqtt topic for  setInsideTemperature value
mqtt_topic_tasks = "Main_Controller_tasks"

#telegram botfather Token Api (put yours here)
TOKEN = "5804234248:AAFsgNd88Fn_-q99D7EzBcjfLa2-Ypo7k6w"
# telegram bot chat id (put yours here)
chat_id = "523560553"
threshold = 4
#mqtt connect callback function
def on_connect(client, userdata, flags, rc):
   print("Connected With Result Code "+str(rc))
   
#mqtt disconnect callback function
def on_disconnect(client, userdata, rc):
    print("Client Got Disconnected")
    

#mqtt received message for sensors topic callback function
def on_message_sensors(client, userdata, message):
    if str(message.topic) == mqtt_topic_sensors: 
       msg1 = json.loads(message.payload.decode())
       print("Message Recieved2: " + str(msg1))
       print("Message topic: " + str(message.topic))
       jsonString = json.dumps(msg1)
       jsonFile = open("/home/yerznka/bot/data_sensors.json", "w")
       jsonFile.write(jsonString)
       jsonFile.close() 

#mqtt received message for tasks topic callback function
def on_message_tasks(client, userdata, message):
    if str(message.topic) == mqtt_topic_tasks: 
       msg2 = json.loads(message.payload.decode())
       json_object2 = json.dumps(msg2)
       print("Message Recieved2: " + str(msg2))
       print("Message topic: " + str(message.topic))
       jsonString = json.dumps(msg2)
       jsonFile = open("/home/yerznka/bot/data_tasks.json", "w")
       jsonFile.write(jsonString)
       jsonFile.close()

#send notification to boot if temperature condition formula was true function
def send_notification_bot():
    fileObject1 = open("/home/yerznka/bot/data_sensors.json", "r")
    jsonContent1 = fileObject1.read()
    data_sensors = json.loads(jsonContent1)
    fileObject2 = open("/home/yerznka/bot/data_tasks.json", "r")
    jsonContent2 = fileObject2.read()
    data_tasks = json.loads(jsonContent2)
    if (((data_tasks["setInsideTemp"]-data_sensors["insideTemp"]) >= threshold) or (data_sensors["insideTemp"]-data_tasks["setVentilationTemp"])>=threshold):
       message = "!!! warning insideTemp: " + str(data_sensors["insideTemp"]) + "°C pass threshold value ("+str(threshold)+"°C)"
       url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
       print(requests.get(url).json()) # this sends the message
    
def get_status_command(update, context):
    fileObject = open("/home/yerznka/bot/data_sensors.json", "r")
    jsonContent = fileObject.read()
    get_status = json.loads(jsonContent)
    update.message.reply_text( "insideTemperature : " + str(get_status["insideTemp"])+ "°C" +", insideHumidity : " + str(get_status["insideHumidity"]))

def get_OutsideStatus_command(update, context):
    fileObject = open("/home/yerznka/bot/data_sensors.json", "r")
    jsonContent = fileObject.read()
    get_status = json.loads(jsonContent)
    update.message.reply_text( "outsideTemperature : " + str(get_status["outsideTemp"])+ "°C" +", outsideHumidity : " + str(get_status["outsideHumidity"]))



#mqtt received message main callback function
def on_message(client, userdata, message):
    on_message_sensors(client, userdata, message)
    on_message_tasks(client, userdata, message)
    send_notification_bot()

# the main program here 
def bot():
   updater = Updater(TOKEN, use_context=True)
   dp = updater.dispatcher
   dp.add_handler(CommandHandler("get_status", get_status_command))
   dp.add_handler(CommandHandler("get_outsideStatus", get_OutsideStatus_command))
   #dp.add_handler(MessageHandler(Filters.text, "unknown command"))
   updater.start_polling()
   #updater.idle()


def mqtt_client():   
   client = mqtt.Client("sub")
   client.on_connect = on_connect
   client.on_message = on_message
   client.connect(broker_url, broker_port)
   client.subscribe(mqtt_topic_sensors, qos=1)
   client.subscribe(mqtt_topic_tasks, qos=1)
   client.on_disconnect
   client.loop_forever()

try:
   _thread.start_new_thread( mqtt_client,())
   _thread.start_new_thread( bot,())
except:
   print("Error: unable to start thread")

while 1:
   pass




