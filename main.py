import time
import requests
import psycopg2
import uvicorn
from fastapi import FastAPI, Body
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, MetaData, Table, Integer, Column, Text, DateTime, insert, select


#class riddle:
#    def __init__(self, id, answer, question, airdate):
#        self.id = id
#        self.answer = answer
#        self.question = question
#        self.airdate = airdate
 


def create_db(dbname):
    conn = psycopg2.connect(host="postgres", database='postgres', user="postgres", password="postgres", port=5432)
    cursor = conn.cursor()
    conn.autocommit = True
    cursor.execute("SELECT 1 FROM pg_database WHERE datname='{dbname}'".
                                                    format(dbname=dbname))

    if cursor.rowcount == 0:
        cursor.execute('create database {dbname}'.format(dbname=dbname))
        s = f"База данных {dbname} создана"
    else:
        s = f"База данных {dbname} уже существует"
    cursor.close()
    conn.close()
    return s


def get_from_db(value, dbname):
    engine = create_engine("postgresql+psycopg2://postgres:postgres@postgres:5432/{db}".format(db=dbname))
    print(engine)
    conn = engine.connect()
    metadata = MetaData()
    ridlist = Table('ridlist', metadata, 
            Column('id_ins', Integer(), primary_key=True),
            Column('id', Integer()),
            Column('answer', Text),
            Column('question', Text),
            Column('airdate', DateTime())
    )
    metadata.create_all(engine)
    if value == 'latest':
        s = conn.execute(select(ridlist).order_by(ridlist.c.id_ins.desc()))
        if s.rowcount == 0:
            result_dic = []
        else:
            print(s.rowcount)
            r = [x for x in s.first()[1:]]
            result_dic = {['id', 'answer', 'question', 'airdate'][i]:r[i] for i in range(len(r))}
    else:
        s = conn.execute(select(ridlist).where(ridlist.c.id == value))
        if s.rowcount == 0:
            result_dic = [0]
        else:
            print(s.rowcount)
            result_dic = [s.rowcount]
    conn.commit()
    conn.close()
    return result_dic


def add_to_db(n, dbname):
    engine = create_engine("postgresql+psycopg2://postgres:postgres@postgres:5432/{db}".format(db=dbname))
    print(engine)
    conn = engine.connect()
    metadata = MetaData()
    ridlist = Table('ridlist', metadata, 
            Column('id_ins', Integer(), primary_key=True),
            Column('id', Integer()),
            Column('answer', Text),
            Column('question', Text),
            Column('airdate', DateTime())
    )
    metadata.create_all(engine)
    new_riddles = [get_from_site(dbname) for i in range(n)]
    r = conn.execute(insert(ridlist), new_riddles)
    print(r.rowcount)
    conn.commit()
    conn.close()
    return f"Добавлены {n} загадок"
 

# получение загадки с сайта, проверка ее наличия в базе
def get_from_site(dbname):
    resp = requests.get("https://jservice.io/api/random?count=1")
    if resp.text.find('Retry later\n') == 0:
        time.sleep(61)       
        resp = requests.get("https://jservice.io/api/random?count=1")
    while get_from_db(resp.json()[0]['id'], dbname) != [0]:
        print('такая загадка уже есть ', resp.json()[0]['id'])
        resp = requests.get("https://jservice.io/api/random?count=1")
    return {'id':(resp.json()[0]['id']), 'answer':(resp.json()[0]['answer']), 'question':(resp.json()[0]['question']), 'airdate':(resp.json()[0]['airdate'])}



app = FastAPI()
 
@app.get("/")
def get_fpage():
    return FileResponse("./index.html")

@app.post("/")
def answer(sent = Body()):
    db_name = "riddles3_db"
    create_db(db_name)
    last_riddle = get_from_db('latest', db_name)
    n = int(str(sent).split('=')[1].strip("'"))
    add_to_db(n, db_name)
    return last_riddle
        
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")

#print("*"*200)
#print(add_to_db(1, "riddles2_db"))
#r = get_from_db('latest', "riddles2_db")
#print(r)
#print(create_db("riddles_db"))
#for i in range(200): 
#    print(i, end='')
#    print(get_from_site())
   