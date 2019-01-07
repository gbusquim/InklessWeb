from django.shortcuts import render
from django.http import HttpResponse 
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from google.cloud import firestore
import os
import google
import datetime
from django.views.decorators.csrf import csrf_protect








os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='inkless/key.json'


#Configuração do Firebase
cred = credentials.Certificate('inkless/key.json')
app = firebase_admin.initialize_app(cred, {
    'storageBucket': 'inklessapp-1922c.appspot.com',
}, name='storage')
db = firestore.Client()



#Ja sei que funciona mudando storage.googleapis para storage.cloud.google.com

bucket = storage.bucket(app=app)


# Variáveis Globais
numSegurado = 0
identBen = ""


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
    listaPropostas=[]
    doc_ref = db.collection(u'users')
    docs = doc_ref.get()
    for doc in docs:
        segurado = doc.to_dict()
        listaSegurados.append(segurado["segurado"]["nomeCompleto"])
        listaPropostas.append(segurado["segurado"]["numeroProposta"])
    # data["listaSegurados"]=listaSegurados
    # data["listaPropostas"]=listaPropostas
    data["listaTabela"] = zip(listaSegurados, listaPropostas)
    return render(request, 'inkless/tabelaSeguradora.html',data)




def paginaBeneficiario(request):
    global identBen
    data={}
    doc_ref = db.collection('users')
    docs = doc_ref.get()
    i = 1
    for doc in docs:
        if i == int(numSegurado):
            #obtendo dados do beneficiario   
            beneficiario = doc.to_dict()
            nome = beneficiario["nomeCompleto"]
            nome = nome.lower()
            nome = nome.title()
            data["Nome"] = nome
            cpf = beneficiario["cpf"]
            data["CPF"] = cpf
            dataDeNasc = beneficiario["dataNascimento"]
            dataDeNasc = retornaData(dataDeNasc)
            data["email"] = beneficiario["email"]

            dataExpedicao = beneficiario["dataExpedicao"]
            data["dataExpedicao"] = retornaData(dataExpedicao)
            data["dataDeNasc"] = dataDeNasc
      

            data["telefone"] = beneficiario["telefone"]
            data["celular"] = beneficiario["celular"]

            data["grauParentesco"] = beneficiario["grauParentesco"]
            data["registroGeral"] = beneficiario["registroGeral"]
            data["orgãoEmissor"] = beneficiario["orgãoEmissor"]
            data["profissao"] = beneficiario["profissao"]
            
            data["endereco"] = beneficiario["endereco"]["endereco"]
            data["bairro"] = beneficiario["endereco"]["bairro"]
            data["cep"] = beneficiario["endereco"]["cep"]
            data["cidade"] = beneficiario["endereco"]["cidade"]
            data["complemento"] = beneficiario["endereco"]["complemento"]
            data["numero"] = beneficiario["endereco"]["numero"]
            #identBen = beneficiario["uid"]

            # ###obtendo status dos documentos##
            # status_ref = db.collection("users").document(identBen).collection("beneficiario").document("requerimentos")
            # statusDict = status_ref.get()
            # statusDict = statusDict.to_dict()
            # if "status" in statusDict:
            #     data["statusDoc"]=statusDict["status"]["docId"]
            # else:
            #     data["statusDoc"]="false"

            ###obtendo status do processo##
            status_ref = db.collection("users").document(identBen)
            statusDict = status_ref.get()
            statusDict = statusDict.to_dict()
            if "status" in statusDict:
                data["status"]=statusDict["status"]
            else:
                data["status"]="Aviso"



            ####obtendo arquivos###
            arquivos = db.collection("users").document(identBen).collection("beneficiario").document("requerimentos").collection("Documento de Identificação")
            arquivos_ref = arquivos.get()
            for arquivo in arquivos_ref:
                identArq = arquivo.to_dict()
                pathArquivo = identArq["imageStorage"]
                blob = bucket.blob(pathArquivo)
                link = blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET')
                link = link.replace("googleapis","cloud.google")
                data["linkId"] = link
                break
            break
        i = i + 1
    return render(request, 'inkless/paginaBeneficiario.html',data)




def paginaSegurado(request):
    global identBen
    data={}
    #doc_ref = db.collection(u'requerimentos').document(u'bCSwF0QWuUUV0c9DIqXaWpVKOJr2')
    #doc_tef = db.collection("users").document("wgB6q0D9iNVNX5EMSGCSyiCmvRX2").collection("beneficiario").document("requerimentos").collection("Documento de Identificação")
    doc_ref = db.collection('users')
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
            data["numeroProposta"] = segurado["segurado"]["numeroProposta"]
            identBen = segurado["uid"]
            if "matricula" in segurado["segurado"]:
                data["matricula"]=segurado["segurado"]["matricula"]
            else:
                 data["matricula"]=""
            if "nomeEstipulante" in segurado["segurado"]:
                data["nomeEstipulante"]=segurado["segurado"]["nomeEstipulante"]
            else:
                 data["nomeEstipulante"]=""

            
            # ###obtendo status do processo##
            # status_ref = db.collection("users").document(identBen)
            # statusDict = status_ref.get()
            # statusDict = statusDict.to_dict()
            # if "status" in statusDict:
            #     data["status"]=statusDict["status"]
            # else:
            #     data["status"]="Aviso"



            status_ref = db.collection("users").document(identBen)
            statusDict = status_ref.get()
            statusDict = statusDict.to_dict()
            if "status" in statusDict:
                data["status"]=statusDict["status"]
            else:
                data["status"]="Aviso"

            break
        i = i + 1
    return render(request, 'inkless/paginaSegurado.html',data)

def obtemNomeSegurado(request):
    global numSegurado
    numSegurado = request.POST.get('nomeSegurado')
    return HttpResponse('success') # if everything is OK
    # nothing went well


def atualizaStatusDocBeneficiario(request):
    statusDoc = request.POST.get('statusDoc')
    doc_ref = db.collection("users").document(identBen).collection("beneficiario").document("requerimentos")
    doc_ref.set({
    u'status': {
        statusDoc:False
    }
    }, merge=True)
    
    return HttpResponse('success') # if everything is OK
    
    # nothing went well


def atualizaStatusDocSegurado(request):
    statusDoc = request.POST.get('statusDoc')
    doc_ref = db.collection("users").document(identBen).collection("segurado").document("requerimentos")
    doc_ref.set({
    u'status': {
        statusDoc:False
    }
    }, merge=True)
    
    return HttpResponse('success') # if everything is OK
    
    # nothing went well


def atualizaStatus(request):
    status = request.POST.get('statusProc')
    doc_ref = db.collection("users").document(identBen)
    doc_ref.set({u'status':status}, merge=True)
    return HttpResponse('success') # if everything is OK
    
    # nothing went well


# Codigo nao usado:
# Colocar data de dataNascimento
#dataNascimento = segurado["segurado"]["dataNascimento"]
#client = storage.Client()

#Create a reference from a Google Cloud Storage URI
# client = storage_google.Client(project="my-project")
# bucket = client.get_bucket("inklessapp-1922c.appspot.com")
# blob = Blob("meuBlob",bucket)
# print(blob.path)
