from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from .models import Record, Token
from django.middleware.csrf import get_token
from datetime import datetime as dt
from datetime import timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.forms.models import model_to_dict
from math import radians, sin, cos, sqrt, atan2
from opencage.geocoder import OpenCageGeocode
import requests
from google_auth_oauthlib.flow import Flow
import os, pickle
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()
GIS_KEY = os.getenv("GIS_KEY")
URL = 'https://feebly-settled-killifish.cloudpub.ru'

TOKEN=os.getenv("TOKEN")
MIN_DIST = 500

# user_tokens = {}
# Create your views here.
def index(request):
    return HttpResponse("hello")

def delete_event_for_user(user_id: int, event_id: str) -> bool:
    token_path = f"tokens/{user_id}.pickle"
    if not os.path.exists(token_path):
        raise ValueError("Пользователь не авторизован.")

    with open(token_path, 'rb') as token_file:
        credentials = pickle.load(token_file)

    service = build('calendar', 'v3', credentials=credentials)

    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return True
    except Exception as e:
        print(f"Ошибка при удалении события: {e}")
        return False
    
def add_event_for_user(user_id: int, text: str, time: str) -> str:
    
    token_path = f"tokens/{user_id}.pickle"
    if not os.path.exists(token_path):
        return False

    with open(token_path, 'rb') as token_file:
        credentials = pickle.load(token_file)

    service = build('calendar', 'v3', credentials=credentials)

    # Парсим старт и считаем конец события через 15 минут
    dt_start = dt.fromisoformat(time)
    dt_end = dt_start + timedelta(minutes=15)

    timezone = 'Asia/Novosibirsk'

    event = {
        'summary': text,
        'start': {
            'dateTime': dt_start.isoformat(),
            'timeZone': timezone,
        },
        'end': {
            'dateTime': dt_end.isoformat(),
            'timeZone': timezone,
        },
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return created_event.get('id')


def send_message(CHAT_ID, TEXT):
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": TEXT
    }
    response = requests.post(url, data=payload)
    return response

def get_coords(address):
    geocoder = OpenCageGeocode(GIS_KEY)
    print(address)
    results = geocoder.geocode(address)

    if results:
        latitude = results[0]['geometry']['lat']
        longitude = results[0]['geometry']['lng']
        print(f"Координаты: {latitude}, {longitude}")
    else:
        latitude = 0
        longitude = 0
    
    return latitude, longitude

def add(request):
    if request.method == 'POST':
        
        user_id = request.POST['user_id']
        text = request.POST['text']
        category = request.POST['category']
        
        done = request.POST['done']
        condition = request.POST['condition']
        if 'datetime' in request.POST and request.POST['datetime']:
            datetime = request.POST['datetime']
        else:
            datetime = None

        latitude = 0
        longitude = 0
        address = 0
        if 'address' in request.POST and request.POST['address'] != '':
            address = request.POST['address']
            latitude, longitude = get_coords(address)
        

        if len(Record.objects.filter(user_id=user_id, text=text, category=category, location_x=latitude, 
                     location_y=longitude, datetime=datetime, done=done, condition=condition)) != 0:
            return JsonResponse({"message": "Record exists", 'check': "Success"})
        
        was_calendar = 0
        if condition == 'time':
            was_calendar = add_event_for_user(user_id, text, datetime)

        rec = Record(user_id=user_id, text=text, category=category, location_x=latitude, 
                     location_y=longitude, datetime=datetime, done=done, condition=condition, address=address, calendar_id=was_calendar)
        rec.save()
        
        return JsonResponse({"message": "Record saved", 'check': "Success", "calendar": bool(was_calendar)})

def all_recs(request):
    user_id = request.GET['user_id']
    records = Record.objects.filter(user_id=user_id, done=False).order_by("datetime")
    ans = []
    for rec in records:
        ans.append(model_to_dict(rec))
        #ans.append(rec.datetime.strftime("%d-%m %H:%M") + " - " + rec.text)
    #return JsonResponse({"recs": '\n'.join(ans)})
    return JsonResponse({"recs": ans})

def update(request):
    rec_id = request.POST['rec_id']
    params = request.POST['params']
    rec = Record.get(pk=rec_id)
    for k, v in params.items():
        rec[k] = v
    rec.save()
    JsonResponse({"message": "Record updated", 'check': "Success"})

def delete(request):
    rec_id = request.POST['rec_id']
    if len(Record.objects.filter(pk=rec_id)) == 0:
        return JsonResponse({"message": "Record does not exists", 'check': "Success"})
    rec = Record.objects.get(pk=rec_id)
    was_calendar = False
    if rec.calendar_id:
        was_calendar = delete_event_for_user(rec.user_id, rec.calendar_id)
    rec.delete()
    return JsonResponse({"message": "Record deleted", 'check': "Success", "calendar": was_calendar})

def get_passed_records(request):
    #user_id = request.GET['user_id']
    now = dt.now()
    records = Record.objects.filter(condition='time', done=False, datetime__lte=now).order_by("datetime")
    
    return JsonResponse({"recs": [[rec.id, rec.user_id, rec.text, rec.category, rec.datetime.strftime("%d-%m %H:%M"), rec.condition] for rec in records]})


def distance_m(lat1, lon1, lat2, lon2):
    R = 6371000  # радиус Земли в метрах
    phi1, phi2 = radians(lat1), radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lambda = radians(lon2 - lon1)

    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def get_location_records(request):
    user_id = request.POST['user_id']
    location_x = float(request.POST['x'])
    location_y = float(request.POST['y'])
    records = Record.objects.filter(done=False, user_id=user_id)
    for rec in records:
        x = rec.location_x
        y = rec.location_y
        r = distance_m(x, y, location_x, location_y)
        if r < MIN_DIST:
            CHAT_ID = user_id

            TEXT = (
                    f"🕒 Напоминание!\n" +
                    f"📍 {rec.address}\n" + 
                    f"📝 Не забудь: {rec.text.capitalize()}.\n" +
                    f"📌 Категория: {rec.category.capitalize()}\n" +
                    f"✨ Хорошего дня!"
                )
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            payload = {
                "chat_id": CHAT_ID,
                "text": TEXT
            }

            response = requests.post(url, data=payload)
            if response.status_code == 200:
                csrftoken = requests.get(URL+"/csrf").json()['csrf']
                header = {'X-CSRFToken': csrftoken}
                cookies = {'csrftoken': csrftoken}
                content = {"rec_id": rec.id}
                mes = requests.post(URL + '/records/delete', data=content, headers=header, cookies=cookies)
    return JsonResponse({"check": "Success"})


def get_top_similar_sentences(indexed_corpus, query):
    """
    indexed_corpus: список кортежей (индекс, предложение)
    query: строка — запрос
    top_n: сколько похожих вернуть
    """
    texts = [text for _, text in indexed_corpus]
    all_sentences = texts + [query]

    # Векторизация
    vectorizer = TfidfVectorizer().fit(all_sentences)
    vectors = vectorizer.transform(all_sentences)

    # Сходство между запросом и всеми в корпусе
    similarity_scores = cosine_similarity(vectors[-1], vectors[:-1])[0]

    # Сортировка и выбор топ-N
    top_indices = similarity_scores.argsort()[::-1]

    # Возвращаем индексы, текст и метрику сходства
    results = [
        (indexed_corpus[i][0], indexed_corpus[i][1], similarity_scores[i])
        for i in top_indices
    ]
    return results

def get_similar(request):
    user_id = request.GET['user_id']
    text = request.GET['text']
    
    records = Record.objects.filter(user_id=user_id).order_by("datetime")
    rec_texts = list(map(lambda x: (x.id, x.text), records))
    
    similar = get_top_similar_sentences(rec_texts, text)
    
    recs = [Record.objects.get(pk=x[0]) for x in similar]
    #recs = [[rec.id, rec.user_id, rec.text, rec.category, (rec.location_x, rec.location_y),
                    #rec.datetime, rec.done, rec.condition] for rec in recs]
    
    recs = [model_to_dict(rec) for rec in recs]
    
    return JsonResponse({"recs": recs})





