import base64
import io
import json
import time
import datetime
import paho.mqtt.client as mqtt
import psycopg2
from PIL import Image

# Connect to the PostgreSQL database server
# def connect():
conn = None
try:
    # read connection parameters
    # params = config()

    # connect to the PostgreSQL server
    database = "bloom_ai"
    print('Connecting to the PostgreSQL database {}....'.format(database))
    conn = psycopg2.connect(host="localhost", database=database, user="postgres", password="1234")

    # create a cursor
    cur = conn.cursor()

    # execute a statement
    cur.execute('SELECT version()')

    # display the PostgreSQL database server version
    db_version = cur.fetchone()
    print('PostgreSQL database version: {}'.format(db_version))

    # close the communication with the PostgreSQL
    # cur.close()
except (Exception, psycopg2.DatabaseError) as error:
    print(error)


# finally:
#     if conn is not None:
#         conn.close()
#         print('Database connection closed.')


# Send data to the connected database
def insert_data(db_temp, db_pres, db_hum):
    try:
        sql = """INSERT INTO sensor(id, temp, press, humidity)
                 VALUES(DEFAULT, %s, %s, %s) RETURNING id;"""
        # execute the INSERT statement
        cur.execute(sql, (db_temp, db_pres, db_hum))
        # commit the changes to the database
        conn.commit()
        # get the generated id back
        id = cur.fetchone()[0]
        print('Data inserted in database with ID: ' + str(id))
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Send data to the connected database
def insert_image(db_image):
    try:
        sql = """INSERT INTO images(id, image_data, created_at)
                 VALUES(DEFAULT, %s, %s) RETURNING id;"""
        # execute the INSERT statement
        insert_time = str(datetime.datetime.now().replace(second=0, microsecond=0))
        cur.execute(sql, (db_image, insert_time,))
        # commit the changes to the database
        conn.commit()
        # get the generated id back
        id = cur.fetchone()[0]
        print('Image inserted in database with ID: ' + str(id))
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Request data to the connected database
def request_image(id):
    try:
        print("Requesting database image for ID: {}".format(id))
        sql = """SELECT image_data FROM images
                 WHERE id = %s;"""
        # Execute the get statement
        cur.execute(sql, (str(id),))
        images = cur.fetchall()[0]
        print("Received total of {} images".format(len(images)))
        for i in range(len(images)):
            # print(type(images[i]))
            img = Image.open(io.BytesIO(base64.b64decode(images[i])))
            img.show()
            img.save("output{}_db.jpg".format(i), 'JPEG')
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    global conn_flag
    conn_flag = True
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    for topic in topics:
        client.subscribe(topic)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    if str(msg.topic).split('/')[-1] == 'image':
        print("New message from: " + str(msg.topic).split('/')[0])
        msg_in = json.loads(msg.payload)
        time_taken = msg_in.get('captured_at')
        img = msg_in.get('image_data')
        insert_image(db_image=img)
        # print(len(img))
        # Save image
        im = Image.open(io.BytesIO(base64.b64decode(img)))
        im.save("images/output-{}.jpg".format(time_taken), 'JPEG')

    elif str(msg.topic).split('/')[-1] == 'sensor':
        print("New message from: " + str(msg.topic).split('/')[0].upper())
        msg_in = json.loads(msg.payload)
        insert_data(db_temp=msg_in.get('temp'), db_pres=msg_in.get('press'), db_hum=msg_in.get('humidity'))


# Loads MQTT broker info to connect
with open('mqtt_config.json') as config:
    json_data = json.load(config)

broker = json_data.get("broker")
port = json_data.get("port")
conn_flag = False


# Topics to subscribe
topics = ['+/sensor', '+/image']
client = mqtt.Client(clean_session=False, client_id="Local Server")
client.on_connect = on_connect
client.on_message = on_message
# client.tls_set('ca.crt')

client.connect(broker, port)
while not conn_flag:
    time.sleep(1)
    print('Connecting...')
    client.loop()

print("CONNECTED TO MQTT SERVER")
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()

# request_image(1)
# client.publish('test', 'segura')
# client.disconnect()
print("MQTT connection closed.")
conn.close()
print("Database connection closed.")
