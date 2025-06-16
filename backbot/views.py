from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.middleware.csrf import get_token


def index(request):
    content = {'message' : 'hello', 'csrf': get_token(request)}
    if request.method == 'POST':
        print(request.POST['message'])
        print(request.POST['user_id'])
        content = {'message' : request.POST['message']}
        return JsonResponse(content)
    
    return JsonResponse(content)