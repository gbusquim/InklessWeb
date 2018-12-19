from django.shortcuts import render
from django.http import HttpResponse
from pyrebase import pyrebase

# Create your views here.

nome=""

def home(request):
    return render(request, 'inkless/tabelaSeguradora.html')

def paginaBeneficiario(request):
    return render(request, 'inkless/paginaBeneficiario.html')

def paginaSegurado(request):
    data={}
    data["Nome"]=nome
    return render(request, 'inkless/paginaSegurado.html',data)

def obtemNomeSegurado(request):
    global nome
    nome = request.POST.get('nomeSegurado')
    return HttpResponse('success') # if everything is OK
    # nothing went well
