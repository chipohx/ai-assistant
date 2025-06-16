from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from .models import Record
from django.middleware.csrf import get_token
from datetime import datetime as dt

# Create your views here.
def index(request):
    return HttpResponse("hello")

def add(request):
    if request.method == 'POST':
        print("In records add:")
        print(request.POST)
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
        return JsonResponse({"message": "Record saved"})
    content = {'message' : 'hello', 'csrf': get_token(request)}
    return JsonResponse(content)



