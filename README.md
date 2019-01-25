# mqtt-server
MQTT server that receives data from IoT devices and stores the data into a Postgres Data Base

Requirements
--
- Install MQTT broker mosquitto
```
brew install mosquitto
```
- Edit mqtt.config file to work on port 8883
```
nano /usr/local/etc/mosquitto/mosquitto.conf
brew services restart mosquitto
```
- Install PostgresSQL as the data base - [link](https://www.postgresql.org/download/)
  - in case usr and pass is required to access the DB, this should be edited in the `Server.py`
  - the data base name should be bloom_ai
  - to generate the tables:
  ```
  CREATE TABLE Images(
    id SERIAL PRIMARY KEY,
    image_data BYTEA
  )
  CREATE TABLE Sensor(
    id SERIAL PRIMARY KEY,
    temp FLOAT,
    press FLOAT,
    humidity FLOAT
  )
  ```
- Edit the `mqtt_config.json` with the IP from the mosquitto broker
- Activate pipenv and run the code
```
pipenv install
pipenv run python Server.py
```
