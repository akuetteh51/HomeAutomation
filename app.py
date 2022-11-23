from flask import Flask,request
import os
from datetime import datetime,timezone
import psycopg2
from dotenv import load_dotenv

load_dotenv()
CREATE_ROOMS_TABLE=(
    "CREATE TABLE IF NOT EXISTS rooms(id SERIAL PRIMARY KEY,name TEXT);"
)
CREATE_AUTO_TABLE="""CREATE TABLE IF NOT EXISTS automate(room_id INTEGER,temperature REAL,hummidity REAL,smoke REAL,date TIMESTAMP,FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE);"""
CREATE_DEVICE_TABLE="""CREATE TABLE IF NOT EXISTS device (room_id INTEGER,Light BOOL,fun BOOL,door BOOL,date TIMESTAMP,FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE);"""
INSERT_ROOM_RETURN_ID="INSERT INTO rooms (name) VALUES (%s) RETURNING id;"
INSERT_AUTO="INSERT INTO automate(room_id,temperature,hummidity,smoke,date) VALUES (%s,%s,%s,%s,%s);"
INSERT_TOGLE="INSERT INTO device(room_id,light,fun,door,date) VALUES (%s,%s,%s,%s,%s);"

app=Flask(__name__)
url=os.getenv("DATABASE_URL")
connection=psycopg2.connect(url)

@app.post("/api/room")
def create_room():
    data=request.get_json()
    name=data['name']
    print(type(name))
    print(name)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_ROOMS_TABLE)
            cursor.execute(INSERT_ROOM_RETURN_ID,(name,))
            room_id=cursor.fetchone()
    return {"id":room_id,"message":f"Room {name} created"},201


@app.post("/api/addSensorData")
def addSensorData():
    data=request.get_json()
    room_id=data['id']
    temperature=data['temperature']
    hummidity=data['hummidity']
    smoke=data['smoke']
    # date=data['date']
    try:
        date=datetime.strptime(data["date"],"%m-%d-%Y %H:%M:%S")
    except KeyError:
        date = datetime.now(timezone.utc)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_AUTO_TABLE)
            cursor.execute(INSERT_AUTO,(room_id,temperature, hummidity,smoke,date))
            # rm_id=cursor.fetchall()[0]
    return "done",201

@app.get("/api/SensorData")
def SensorData():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM automate ")
            rm_id=cursor.fetchall()[0]
    
    return {"data":{"room_id":rm_id[0],"temperature":rm_id[1],"hummidity":rm_id[2],"smoke":rm_id[3],"date":rm_id[4]}},201


@app.post("/api/toggle")
def toggle_device():
    data=request.get_json()
    room_id=data['id']
    light=data['light']
    fan=data['fan']
    door=data['door']
    # date=data['date']
    try:
        date=datetime.strptime(data["date"],"%m-%d-%Y %H:%M:%S")
    except KeyError:
        date = datetime.now(timezone.utc)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_DEVICE_TABLE)
            cursor.execute(INSERT_TOGLE,(room_id,light,fan,door,date))
            
    return "done",201


@app.get("/api/device_stat")
def device_status():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM device ")
            rm_id=cursor.fetchall()[0]
    
    return {"data":{"room_id":rm_id[0],"light":rm_id[1],"fan":rm_id[2],"door":rm_id[3],"date":rm_id[4]}},201 