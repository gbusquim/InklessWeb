from django.shortcuts import render
from django.http import HttpResponse 
import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore
import os






os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='inkless/key.json'


#Configuração do Firebase
cred = credentials.Certificate('inkless/key.json')
default_app = firebase_admin.initialize_app(cred)

db = firestore.Client()

# Variáveis Globais
numSegurado = 0


#Funções dos templates
def home(request): 
    #user= auth.sign_in_with_email_and_password("yang@mail.com","123456")
    # session_id = user['idToken']
    # request.session['uid']=str(session_id)
    data = {}
    listaSegurados=[]
    doc_ref = db.collection(u'users')
    docs = doc_ref.get()
    for doc in docs:
        segurado = doc.to_dict()
        listaSegurados.append(segurado["segurado"]["nomeCompleto"])
    data["listaSegurados"]=listaSegurados
    return render(request, 'inkless/tabelaSeguradora.html',data)

def paginaBeneficiario(request):
    data={}
    doc_ref = db.collection(u'users')
    docs = doc_ref.get()
    i = 1
    for doc in docs:
        if i == int(numSegurado):   
            segurado = doc.to_dict()
            nome = segurado["nomeCompleto"]
            data["Nome"] = nome
            break
        i = i + 1
    return render(request, 'inkless/paginaBeneficiario.html',data)

def paginaSegurado(request):
    data={}
    doc_ref = db.collection(u'users')
    docs = doc_ref.get()
    i = 1
    for doc in docs:
        if i == int(numSegurado):   
            segurado = doc.to_dict()
            nome = segurado["segurado"]["nomeCompleto"]
            data["Nome"] = nome
            break
        i = i + 1
    
    # print(request.session['uid'])
    # idtoken = request.session['uid']
    # a = auth.get_account_info(idtoken)
    # a=a['users']
    # a=a[0]
    # a = a['localId']
    # dat = {"name": "Mortimer 'Morty' Smith"}
    # database.child("users").push(dat)
    #print(user.val()) # {name": "Mortimer 'Morty' Smith"}
    return render(request, 'inkless/paginaSegurado.html',data)

def obtemNomeSegurado(request):
    global numSegurado
    numSegurado = request.POST.get('nomeSegurado')
    return HttpResponse('success') # if everything is OK
    # nothing went well
