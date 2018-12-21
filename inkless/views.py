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
nome=""


#Funções dos templates
def home(request):
    #user= auth.sign_in_with_email_and_password("yang@mail.com","123456")
    # session_id = user['idToken']
    # request.session['uid']=str(session_id)
    doc_ref = db.collection(u'users')
    docs = doc_ref.get()
    for doc in docs:
       print(u'{} => {}'.format(doc.id, doc.to_dict()))
    return render(request, 'inkless/tabelaSeguradora.html')

def paginaBeneficiario(request):
    return render(request, 'inkless/paginaBeneficiario.html')

def paginaSegurado(request):
    data={}
    data["Nome"]=nome
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
    global nome
    nome = request.POST.get('nomeSegurado')
    return HttpResponse('success') # if everything is OK
    # nothing went well
