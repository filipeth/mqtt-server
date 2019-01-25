import psycopg2
import io
from PIL import Image
import base64


# Connect to the PostgreSQL database server
def connect():
    conn = None
    global cur
    cur = None
    try:
        # read connection parameters
        # params = config()

        # connect to the PostgreSQL server
        database = "bloom_ai"
        print('Connecting to the PostgreSQL database {}'.format(database))
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


# Request data to the connected database
def request_image(id):
    try:
        print("Requesting database image for ID: {}".format(id))
        sql = """SELECT image_data FROM images
                 WHERE id = %s;"""
        # Execute the get statement
        cur.execute(sql, (id,))
        images = cur.fetchall()[0]
        print("Received total of {} images".format(len(images)))
        for i in range(len(images)):
            # print(type(images[i]))
            img = Image.open(io.BytesIO(base64.b64decode(images[i])))
            img.show()
            # img.save("output{}_db.jpg".format(i), 'JPEG')
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


connect()
request_image(15)
