from django.shortcuts import render
from django.http import HttpResponse
from pyrebase import pyrebase

# Create your views here.

def home(request):
    return render(request, 'inkless/tabelaSeguradora.html')

def paginaBeneficiario(request):
    return render(request, 'inkless/paginaBeneficiario.html')

def paginaSegurado(request):
    return render(request, 'inkless/paginaSegurado.html')

