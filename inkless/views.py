from django.shortcuts import render
from django.http import HttpResponse 
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage as storage_firebase
from google.cloud import firestore
from google.cloud import storage as storage_google
import os
import google
from google.cloud.storage import Blob

import datetime






os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='inkless/key.json'


#Configuração do Firebase
cred = credentials.Certificate('inkless/key.json')
app = firebase_admin.initialize_app(cred, {
    'storageBucket': 'inklessapp-1922c.appspot.com',
}, name='storage')

db = firestore.Client()
#client = storage.Client()

#Create a reference from a Google Cloud Storage URI
client = storage_google.Client(project="my-project")
bucket = client.get_bucket("inklessapp-1922c.appspot.com")
blob = Blob("meuBlob",bucket)
print(blob.path)


#Ja sei que funciona mudando storage.googleapis para storage.cloud.google.com
# app = firebase_admin.initialize_app(cred, {
#     'storageBucket': 'inklessapp-1922c.appspot.com',
# }, name='storage')
# bucket = storage.bucket(app=app)
#blob = bucket.blob("users/Inkless-FichaDeProjeto.pdf")
# print(blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET'))

# Variáveis Globais
numSegurado = 0


def retornaData(dataNasc):
            dataNascimento=google.api_core.datetime_helpers.to_rfc3339(dataNasc,ignore_zone=True)
            dataNascimento=dataNascimento[:-17]
            ano=dataNascimento[0:4]
            dia=dataNascimento[8:10]
            mes=dataNascimento[5:7]
            dtNascList=list(dataNascimento)
            dtNascList[5:9]=ano
            dtNascList[0:1]=dia
            dtNascList[2]='/'
            dtNascList[5]='/'
            dtNascList[3:5]=mes
            del dtNascList[-1]
            dtNascList = ''.join(str(num) for num in dtNascList)
            return dtNascList

            
            


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
            beneficiario = doc.to_dict()
            nome = beneficiario["nomeCompleto"]
            nome = nome.lower()
            nome = nome.title()
            data["Nome"] = nome
            cpf = beneficiario["cpf"]
            data["CPF"] = cpf
            dataDeNasc = beneficiario["dataNascimento"]
            dataDeNasc = retornaData(dataDeNasc)
            data["dataDeNasc"] = dataDeNasc
            email = beneficiario["email"]
            data["email"] = email
            celular = beneficiario["telefone"]
            data["celular"] = celular

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
            cpf = segurado["segurado"]["cpf"]
            plano = segurado["segurado"]["beneficioRequerido"]
            data["CPF"] = cpf 
            data["Nome"] = nome
            data["beneficioRequerido"] = plano
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




# Codigo nao usado:
# Colocar data de dataNascimento
#dataNascimento = segurado["segurado"]["dataNascimento"]
