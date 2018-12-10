from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def home(request):
    data= {}
    data['nome']=['t1','t2','t1']
    return render(request, 'inkless/home.html',data)

def teste(request):
    return render(request, 'inkless/teste.html')
