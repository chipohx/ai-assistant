from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from .models import Record
from django.middleware.csrf import get_token
from datetime import datetime as dt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Create your views here.
def index(request):
    return HttpResponse("hello")

def add(request):
    if request.method == 'POST':
        
        user_id = request.POST['user_id']
        text = request.POST['text']
        category = request.POST['category']
        #datetime = dt.strptime(request.POST['datetime'], "%Y-%m-%d %H:%M").date()
        datetime = request.POST['datetime']
        done = request.POST['done']
        condition = request.POST['condition']
        
        if 'location' not in request.POST:
            location_x = 0
            location_y = 0
        else:
            location = request.POST['location']
            location_x = location[0]
            location_y = location[1]
        rec = Record(user_id=user_id, text=text, category=category, location_x=location_x, 
                     location_y=location_y, datetime=datetime, done=done, condition=condition)
        rec.save()
        return JsonResponse({"message": "Record saved", 'check': "Success"})
    content = {'message' : 'hello', 'csrf': get_token(request)}
    return JsonResponse(content)

def all_recs(request):
    user_id = request.GET['user_id']
    records = Record.objects.filter(user_id=user_id).order_by("datetime")
    ans = []
    for rec in records:
        ans.append(rec.datetime.strftime("%d-%m %H:%M") + " - " + rec.text)
    return JsonResponse({"recs": '\n'.join(ans)})


def delete(request):
    rec_id = request.POST['rec_id']
    Record.objects.get(pk=rec_id).delete()


def get_top_similar_sentences(indexed_corpus, query, top_n=5):
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
    top_indices = similarity_scores.argsort()[::-1][:top_n]

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
    return JsonResponse({"options": similar, 'message': "Choose from here", 'check': "ChooseDel"})





