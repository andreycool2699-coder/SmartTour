from fastapi import FastAPI
from utils import json_to_dict_list
import os
from typing import Optional
import os
import requests
from yattag import Doc
#import papermill as pm
from pathlib import Path
from ploomber import DAG
from ploomber.tasks import NotebookRunner
from ploomber.products import File
from fastapi import FastAPI
#from utils import json_to_dict_list
import os
from typing import Optional
import requests
from datetime import date
import json
from dotenv import load_dotenv
import uuid
from fastapi import FastAPI, Body, status
from fastapi.responses import JSONResponse, FileResponse
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import typing as tp
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import numpy as np
import pandas as pd
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import io
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt
from fastapi import FastAPI, Response, BackgroundTasks
import seaborn as sns

app = FastAPI()

access_token = '2acc0c8b2acc0c8b2acc0c8b6429f6e88322acc2acc0c8b4216c004c7aa2b3abf53ebe6'
api_version = '5.89'

# Load environment variables
load_dotenv()

today = date.today()

# Получаем путь к директории текущего скрипта
script_dir = os.path.dirname(os.path.abspath(__file__))

# Переходим на уровень выше
parent_dir = os.path.dirname(script_dir)

#@app.get("/hotels/list")

# Получаем путь к директории текущего скрипта
script_dir = os.path.dirname(os.path.abspath(__file__))

# Переходим на уровень выше
parent_dir = os.path.dirname(script_dir)

# Получаем путь к JSON
path_to_json = os.path.join(script_dir, 'hotels.json')


class Person:
    def __init__(self, name, post, age):
        self.name = name
        self.post = post
        self.age = age
        self.id = str(uuid.uuid4())

# условная база данных - набор объектов Person
people = [Person("Андрей","Хороший отель!", 43), Person("Данил","Приятное путешествие", 25), Person("Артем","Хорошая поездка",29),Person("Алина","В Ялте хорошо!",25)]
# для поиска пользователя в списке people

def find_person(id):
   for person in people: 
        if person.id == id:
           return person
   return None
 
@app.get("/")
async def main():
    return FileResponse("public/index.html")
 
@app.get("/api/users")
def get_people():
    return people

@app.get("/api/users/{id}")
def get_person(id):
    # получаем пользователя по id
    person = find_person(id)
    print(person)
    # если не найден, отправляем статусный код и сообщение об ошибке
    if person==None:  
        return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, 
                content={ "message": "Пользователь не найден" }
        )
    #если пользователь найден, отправляем его
    return person

@app.post("/api/users")
def create_person(data  = Body()):
    person = Person(data["name"],data["post"], data["age"])
    # добавляем объект в список people
    people.append(person)
    return person
 
@app.put("/api/users")
def edit_person(data  = Body()):
  
    # получаем пользователя по id
    person = find_person(data["id"])
    # если не найден, отправляем статусный код и сообщение об ошибке
    if person == None: 
        return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, 
                content={ "message": "Пользователь не найден" }
        )
    # если пользователь найден, изменяем его данные и отправляем обратно клиенту
    person.age = data["age"]
    person.name = data["name"]
    person.post = data["post"]
    return person

@app.delete("/api/users/{id}")
def delete_person(id):
    # получаем пользователя по id
    person = find_person(id)
  
    # если не найден, отправляем статусный код и сообщение об ошибке
    if person == None:
        return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, 
                content={ "message": "Пользователь не найден" }
        )
  
    # если пользователь найден, удаляем его
    people.remove(person)
    return person

@app.get("/hotels")
def get_all_hotels():
    return json_to_dict_list(path_to_json)

@app.get("/hotels/{friend}")
def get_all_hotel_friends(friend:Optional[str] = None,hotel:Optional[str] = None,hotel_address:Optional[str] = None,date1: Optional[str] = None, date2: Optional[str] = None):
    hotels = json_to_dict_list(path_to_json)
    return_list = []
    
    for hotel in hotels:
        if hotel["friend"] == friend:
            return_list.append(hotel)

    #if hotel:
        #return_list = [hotel for hotel in return_list if hotel["hotel"].lower() == hotel.lower()]
            
    if hotel_address:
        return_list = [hotel for hotel in return_list if hotel["hotel_address"].lower() == hotel_address.lower()]
        
    if date1:
        return_list = [hotel for hotel in return_list if hotel["date1"] == date1]

    if date2:
        return_list = [hotel for hotel in return_list if hotel["date2"] == date2]
    return return_list

@app.get("/hotels/{date1}")
def get_all_hotel_date(date1:Optional[str] = None):
    hotels = json_to_dict_list(path_to_json)
    return_list = []
    
    for hotel in hotels:
        if hotel["date1"] == date1:
            return_list.append(hotel)
            
    return return_list

def TextToHtml(text1):
    doc, tag, text = Doc().tagtext()  
    with tag('html'):  
        with tag('head'):  
            with tag('title'):  
                text('Отзывы друзей')  
    with tag('body'):  
        with tag('p', id='intro'):  
            text(text1)  
    html = doc.getvalue()
    #html= doc.save()
    #print(html)

def createhtmlfile(file,text):
    Func = open(file+".html","w")
    Func.write("<html>\n<head>\n<title> \posts\n \
           </title>\n</head> <body> <h1> text </h1>\n\</body></html>")
    Func.close()

def output():
    res_wall = requests.get(f'https://api.vk.com/method/wall.get?domain=moscow.hotel&count=100&access_token={access_token}&v={api_version}')
    url = 'https://api.vk.com/method/wall.get?domain=moscow.hotel&count=100&offset = {offset}&access_token={access_token}&v={api_version}'
    texts = []
    for i in range(0, 301, 100):
        url_formatted = url.format(access_token = access_token, api_version = api_version, offset = i)
        #print(i)
        res_wall = requests.get(url_formatted)
        for post in res_wall.json()["response"]['items']:
            texts.append(post["text"])

    with open("posts3.txt", "wt", encoding = "utf8") as f:
        for text in texts:
            f.write(text.replace("\n", " ") + "\n")

    res_wall = requests.get(f'https://api.vk.com/method/wall.get?domain=aziahotel.perm&count=100&access_token={access_token}&v={api_version}')
    url = 'https://api.vk.com/method/wall.get?domain=aziahotel.perm&count=100&offset = {offset}&access_token={access_token}&v={api_version}'
    texts = []
    for i in range(0, 301, 100):
        url_formatted = url.format(access_token = access_token, api_version = api_version, offset = i)
        #print(i)
        res_wall = requests.get(url_formatted)
        for post in res_wall.json()["response"]['items']:
            texts.append(post["text"])

    with open("posts4.txt", "wt", encoding = "utf8") as f:
        for text in texts:
            f.write(text.replace("\n", " ") + "\n")

    res_wall = requests.get(f'https://api.vk.com/method/wall.get?domain=saleof90=100&access_token={access_token}&v={api_version}')
    url = 'https://api.vk.com/method/wall.get?domain=saleof90&count=100&offset = {offset}&access_token={access_token}&v={api_version}'
    texts = []
    for i in range(0, 301, 100):
        url_formatted = url.format(access_token = access_token, api_version = api_version, offset = i)
        #print(i)
        res_wall = requests.get(url_formatted)
        for post in res_wall.json()["response"]['items']:
            texts.append(post["text"])

    with open("posts5.txt", "wt", encoding = "utf8") as f:
        for text in texts:
            f.write(text.replace("\n", " ") + "\n")

@app.get("/api/bot")
def start_bot():
    #pm.execute_notebook( 'D:/Work/Hakathons/Ostrovok/FastApi/Main/SmartTour_Bot.ipynb', 'D:/Work/Hakathons/Ostrovok/FastApi/Main/output.ipynb', parameters=dict(alpha=0.6, ratio=0.1) )
    dag = DAG()
    first = NotebookRunner(Path('D:\Work\Hakathons\Ostrovok\FastApi\Main\SmartTour_Bot.ipynb'), File('D:\Work\Hakathons\Ostrovok\FastApi\Main\firstout.ipynb'), dag=dag)
    dag.build()

    filename = 'SmartTour_Bot.ipynb'
    with open(filename) as ff:
        nb_in = nbformat.read(ff, nbformat.NO_CONVERT)
    
    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')

    nb_out = ep.preprocess(nb_in)
    return "Бот запущен!"

@app.get("api/analytics")
def create_img():
    with open("posts3.txt", "r", encoding = "utf8") as f:
        lines = f.readlines()
    sentences = lines
    # Преобразование текста 
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(sentences)

    # Определение количества кластеров
    num_clusters = 350

    # Обучение модели KMeans
    model = KMeans(n_clusters=num_clusters, random_state=42)
    model.fit(X)

    # Получение кластеров
    clusters = model.labels_.tolist()

    # Создание DataFrame для визуализации
    df = pd.DataFrame({'sentence': sentences, 'cluster': clusters})

    # Вывод результатов
    #print(df)


    fig = plt.figure()  # make sure to call this, in order to create a new figure
    # Визуализация кластеров
    plt.rcParams['figure.figsize'] = [7.50, 3.50]
    plt.rcParams['figure.autolayout'] = True
    ax = plt.subplots()
    for color in ['tab:blue']:
      plt.scatter(X.toarray()[:, 0], X.toarray()[:, 1], c=clusters,  label=color, cmap='viridis')
      plt.title('Кластерный анализ текста')
      plt.xlabel('cluster')
      plt.ylabel('sentence')
      plt.legend()
      plt.grid(True)
      plt.show()
      #return sentence
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    plt.close(fig)
    return img_buf

def create_img2():
    with open("posts4.txt", "r", encoding = "utf8") as f:
        lines = f.readlines()
    sentences = lines
    # Преобразование текста 
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(sentences)

    # Определение количества кластеров
    num_clusters = 350

    # Обучение модели KMeans
    model = KMeans(n_clusters=num_clusters, random_state=42)
    model.fit(X)

    # Получение кластеров
    clusters = model.labels_.tolist()

    # Создание DataFrame для визуализации
    df = pd.DataFrame({'sentence': sentences, 'cluster': clusters})

    # Вывод результатов
    #print(df)


    fig = plt.figure()  # make sure to call this, in order to create a new figure
    # Визуализация кластеров
    plt.rcParams['figure.figsize'] = [7.50, 3.50]
    plt.rcParams['figure.autolayout'] = True
    ax = plt.subplots()
    for color in ['tab:blue']:
      plt.scatter(X.toarray()[:, 0], X.toarray()[:, 1], c=clusters,  label=color, cmap='viridis')
      plt.title('Кластерный анализ текста')
      plt.xlabel('cluster')
      plt.ylabel('sentence')
      plt.legend()
      plt.grid(True)
      plt.show()
      #return sentence
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    plt.close(fig)
    plt.figure(figsize=(10, 7))            #задаем размер
    cmap = sns.diverging_palette(200, 5, as_cmap=True)    #цветовую палитру
    mask = np.zeros_like(df.corr(), dtype=float)
    mask[np.triu_indices_from(mask)] = True          #оставим половину карты (инфо дублируется)
    sns.heatmap(df.corr(), mask=mask, cmap=cmap);
    return img_buf

def get_img2(background_tasks: BackgroundTasks):
    img_buf = create_img()
    Background_tasks.add_task(img_buf.close)
    headers = {'Content-Disposition': 'inline; filename="out.png"'}
    return Response(img_buf.getvalue(), headers=headers, media_type='image/png')

def create_img3():
    with open("posts5.txt", "r", encoding = "utf8") as f:
        lines = f.readlines()
    sentences = lines
    # Преобразование текста 
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(sentences)

    # Определение количества кластеров
    num_clusters = 350

    # Обучение модели KMeans
    model = KMeans(n_clusters=num_clusters, random_state=42)
    model.fit(X)

    # Получение кластеров
    clusters = model.labels_.tolist()

    # Создание DataFrame для визуализации
    df = pd.DataFrame({'sentence': sentences, 'cluster': clusters})

    # Вывод результатов
    #print(df)


    fig = plt.figure()  # make sure to call this, in order to create a new figure
    # Визуализация кластеров
    plt.rcParams['figure.figsize'] = [7.50, 3.50]
    plt.rcParams['figure.autolayout'] = True
    ax = plt.subplots()
    for color in ['tab:blue']:
      plt.scatter(X.toarray()[:, 0], X.toarray()[:, 1], c=clusters,  label=color, cmap='viridis')
      plt.title('Кластерный анализ текста')
      plt.xlabel('cluster')
      plt.ylabel('sentence')
      plt.legend()
      plt.grid(True)
      plt.show()
      #return sentence
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    plt.close(fig)
    return img_buf

def get_img3(background_tasks: BackgroundTasks):
    img_buf = create_img3()
    Background_tasks.add_task(img_buf.close)
    headers = {'Content-Disposition': 'inline; filename="out3.png"'}
    return Response(img_buf.getvalue(), headers=headers, media_type='image/png')


def create_img4():
    with open("posts5.txt", "r", encoding = "utf8") as f:
        lines = f.readlines()
    sentences = lines
    # Преобразование текста 
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(sentences)

    # Определение количества кластеров
    num_clusters = 350

    # Обучение модели KMeans
    model = KMeans(n_clusters=num_clusters, random_state=42)
    model.fit(X)

    # Получение кластеров
    clusters = model.labels_.tolist()

    # Создание DataFrame для визуализации
    df = pd.DataFrame({'sentence': sentences, 'cluster': clusters})

    # Вывод результатов
    #print(df)


    fig = plt.figure()  # make sure to call this, in order to create a new figure
    # Визуализация кластеров
    plt.rcParams['figure.figsize'] = [7.50, 3.50]
    plt.rcParams['figure.autolayout'] = True
    ax = plt.subplots()
    for color in ['tab:blue']:
      plt.scatter(X.toarray()[:, 0], X.toarray()[:, 1], c=clusters,  label=color, cmap='viridis')
      plt.title('Кластерный анализ текста')
      plt.xlabel('cluster')
      plt.ylabel('sentence')
      plt.legend()
      plt.grid(True)
      plt.show()
      #return sentence
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    plt.close(fig)
    return img_buf

def get_img4(background_tasks: BackgroundTasks):
    img_buf = create_img3()
    Background_tasks.add_task(img_buf.close)
    headers = {'Content-Disposition': 'inline; filename="out4.png"'}
    return Response(img_buf.getvalue(), headers=headers, media_type='image/png')

class Hotel:
    def __init__(self, hotel,date1,email,phone_number,hotel_address,date2,special_notes):
        self.hotel = hotel
        self.date1 = date1
        self.email = email
        self.phone_number = phone_number
        self.hotel_address = hotel_address
        self.date2 = date2
        self.special_notes = special_notes
        self.id = str(uuid.uuid4())
# условная база данных - набор объектов Person
hotels = [Hotel("Мечта", "27.09.2025","dream@example.com","+7 (123) 456-7890","г. Москва, ул. Пушкина, д. 10, кв. 5","29.09.2025","Без примечаний"), Hotel("Парус", "27.09.2025","parus@example.com","+7 (234) 567-8901","г. Санкт-Петербург, ул. Ленина, д. 5, кв. 8","29.09.2025","Без примечаний"), Hotel("Паруса", "27.09.2025","parusa@example.com","+7 (345) 678-9012","г. Новосибирск, ул. Гагарина, д. 15, кв. 12","29.09.2025","Без примечаний"),Hotel("Океан", "27.09.2025","ocean@example.com","+7 (456) 789-0123","г. Екатеринбург, ул. Пушкина, д. 20, кв. 3","29.09.2025","Без примечаний")]
# для поиска отеля в списке hotels
def find_hotel(id):
   for hotel in hotels: 
        if hotel.id == id:
           return hotel
   return None
 
@app.get("/hotels/posts")
async def hotel_posts():
    return FileResponse("public/hotels.html")

@app.get("/api/hotels")
def get_hotels():
    return hotels
 
@app.get("/api/hotels/{id}")
def get_hotel(id):
    # получаем отель по id
    hotel = find_hotel(id)
    print(hotel)
    # если не найден, отправляем статусный код и сообщение об ошибке
    if hotel == None:  
        return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, 
                content={ "message": "Отель не найден" }
        )
    #если отель найден, отправляем его
    return hotel
 
@app.post("/api/hotels")
def create_hotel(data  = Body()):
    person = Hotel(data["hotel"], data["date1"],data["email"], data["phone_number"],data["hotel_address"],data["date2"],data["special_notes"])
    # добавляем объект в список hotels
    hotels.append(hotel)
    return hotel

@app.put("/api/hotels")
def edit_hotel(data  = Body()):
  
    # получаем отель по id
    hotel = find_hotel(data["id"])
    # если не найден, отправляем статусный код и сообщение об ошибке
    if hotel == None: 
        return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, 
                content={ "message": "Отель не найден" }
        )
    # если отель найден, изменяем его данные и отправляем обратно клиенту
    hotel.hotel = data["hotel"]
    hotel.date1 = data["date1"]
    hotel.email= data["email"]
    hotel.phone_number = data["phone_number"]
    hotel.hotel_address = data["hotel_address"]
    hotel.date2 = data["date2"]
    hotel.special_notes = data["special_notes"]
    return hotel
 
@app.delete("/api/hotels/{id}")
def delete_hotel(id):
    # получаем отель по id
    hotel = find_hotel(id)
  
    # если не найден, отправляем статусный код и сообщение об ошибке
    if hotel == None:
        return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, 
                content={ "message": "Отель не найден" }
        )
  
    # если отель найден, удаляем его
    hotels.remove(hotel)
    return hotel


class Admin:
    def __init__(self1, name1,post1, age1):
        self1.name = name1
        self1.post = post1
        self1.age = age1
        self1.id = str(uuid.uuid4())

# условная база данных - набор объектов Admin
admins= [Admin("Андрей","Хороший отель!", 43), Admin("Данил","Приятное путешествие", 25), Admin("Артем","Хорошая поездка",29),Admin("Алина","В Ялте хорошо!",25)]

# для поиска администратора в списке admins
def find_admin(id):
   for admin in admins: 
        if admin.id == id:
           return admin
   return None

@app.get("/api/admins")
def get_admin():
    #return FileResponse("public/index.html")
    return admins

def get_admins():
    return admins

@app.get("/api/admins/{id}")
def get_admin(id):
    # получаем пользователя по id
    admin = find_admin(id)
    print(admin)
    # если не найден, отправляем статусный код и сообщение об ошибке
    if admin==None:  
        return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, 
                content={ "message": "Администратор не найден" }
        )
    #если пользователь найден, отправляем его
    return admin

@app.post("/api/admins")
def create_admin(data1  = Body()):
    admin = Admin(data1["name"],data1["post"], data1["age"])
    # добавляем объект в список admins
    return admin
 
@app.put("/api/admins")
def edit_admin(data1  = Body()):
  
    # получаем пользователя по id
    admin = find_admin(data1["id"])
    # если не найден, отправляем статусный код и сообщение об ошибке
    if admin == None: 
        return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, 
                content={ "message": "Администратор не найден" }
        )
    # если пользователь найден, изменяем его данные и отправляем обратно клиенту
    admin.age = data1["age"]
    admin.name = data1["name"]
    admin.post = data1["post"]
    return admin

@app.delete("/api/admin/{id}")
def delete_admin(id):
    # получаем пользователя по id
    admin = find_admin(id)
  
    # если не найден, отправляем статусный код и сообщение об ошибке
    if admin == None:
        return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, 
                content={ "message": "Администратор не найден" }
        )
  
    # если пользователь найден, удаляем его
    admins.remove(admin)
    return admin

@app.get('/api/plots')
def get_img(background_tasks: BackgroundTasks):
    img_buf = create_img()
    background_tasks.add_task(img_buf.close)
    headers = {'Content-Disposition': 'inline; filename="out.png"'}
    return Response(img_buf.getvalue(), headers=headers, media_type='image/png')


@app.get('/api/plots2')
def get_img5(background_tasks: BackgroundTasks):
    img_buf = create_img3()
    background_tasks.add_task(img_buf.close)
    headers = {'Content-Disposition': 'inline; filename="out5.png"'}
    return Response(img_buf.getvalue(), headers=headers, media_type='image/png')

@app.get('/api/plots3')
def get_img6(background_tasks: BackgroundTasks):
    img_buf = create_img4()
    background_tasks.add_task(img_buf.close)
    headers = {'Content-Disposition': 'inline; filename="out6.png"'}
    return Response(img_buf.getvalue(), headers=headers, media_type='image/png')
