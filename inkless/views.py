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
        if "numeroProposta" in segurado["segurado"]:
            listaPropostas.append(segurado["segurado"]["numeroProposta"])
        else:
            listaPropostas.append("12345")
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
            data["fiscalExterior"] = beneficiario["fiscalExterior"]
            
            data["endereco"] = beneficiario["endereco"]["endereco"]
            data["bairro"] = beneficiario["endereco"]["bairro"]
            data["cep"] = beneficiario["endereco"]["cep"]
            data["cidade"] = beneficiario["endereco"]["cidade"]
            data["complemento"] = beneficiario["endereco"]["complemento"]
            data["numero"] = beneficiario["endereco"]["numero"]


            ##obtendo status do processo##
            status_ref = db.collection("users").document(identBen)
            statusDict = status_ref.get()
            statusDict = statusDict.to_dict()
            if "status" in statusDict:
                data["status"]=statusDict["status"]
            else:
                data["status"]="Aviso"




           ##obtendo status de cada documento E PEGAR PATH DE CADA UM##
            doc_ref = db.collection("users").document(identBen).collection("beneficiario").document("requerimentos")
            doc_ref = doc_ref.get()
            doc_ref = doc_ref.to_dict()
            if "status" not in doc_ref:
                ## todos os documentos para solicitar,com execeao dos obrigatorios ##
                #data["statusDoc1"] = True
                #data["linkId"]=obtemLinkArquivo(db,identBen,"Documento de Identificação","beneficiario")
                data["statusDoc2"] = True
                #data["linkRes"]=obtemLinkArquivo(db,identBen,"Comprovante de Residência","beneficiario")
                data["statusDoc3"] = "Nao solicitado"
                data["statusDoc4"] = "Nao solicitado"
                data["statusDoc5"] = "Nao solicitado"
                data["statusDoc6"] = "Nao solicitado"
                data["statusDoc7"] = "Nao solicitado"
                data["statusDoc8"] = "Nao solicitado"
                data["statusDoc9"] = "Nao solicitado"
                data["statusDoc10"] = "Nao solicitado"
                data["statusDoc11"] = "Nao solicitado"
                data["statusDoc12"] = "Nao solicitado"

            else:
                ## testar documento por documento ##
                ## obrigatorios ##

                ## "Documento de Identificação" ##
                if "Documento de Identificação" not in  doc_ref["status"]:
                    data["statusDoc1"] = True
                    #data["linkId"]=obtemLinkArquivo(db,identBen,"Documento de Identificação","beneficiario")
                else:
                    if doc_ref["status"]["Documento de Identificação"] == False:
                        data["statusDoc1"] = False
                    else:
                        data["statusDoc1"] = True
                        #data["linkRes"]=obtemLinkArquivo(db,identBen,"Comprovante de Residência","beneficiario")

                ## "Comprovante de Residência" ##
                if "Comprovante de Residência" not in  doc_ref["status"]:
                    data["statusDoc2"] = True
                    #data["linkRes"]=obtemLinkArquivo(db,identBen,"Comprovante de Residência","beneficiario")
                else:
                    if doc_ref["status"]["Comprovante de Residência"] == False:
                        data["statusDoc2"] = False
                    else:
                        data["statusDoc2"] = True
                        #data["linkRes"]=obtemLinkArquivo(db,identBen,"Comprovante de Residência","beneficiario")


                 ## nao-obrigatorios ##

                ## "Informações tributárias complementares" ##
                if "Informações tributárias complementares" not in  doc_ref["status"]:
                    data["statusDoc3"] = "Nao solicitado"
                else:
                    if doc_ref["status"]["Informações tributárias complementares"] == False:
                        data["statusDoc3"] = False
                    else:
                        data["statusDoc3"] = True
                        #data["linkITC"]=obtemLinkArquivo(db,identBen,"Comprovantes de Informações Tributárias Complementares","beneficiario")

                ## "Certidão de nascimento" ##
                if "Certidão de nascimento" not in  doc_ref["status"]:
                    data["statusDoc4"] = "Nao solicitado"
                else:
                    if doc_ref["status"]["Certidão de nascimento"] == False:
                        data["statusDoc4"] = False
                    else:
                        data["statusDoc4"] = True
    
                ## "Termo de tutela" ##
                if "Termo de tutela" not in  doc_ref["status"]:
                    data["statusDoc5"] = "Nao solicitado"
                else:
                    if doc_ref["status"]["Termo de tutela"] == False:
                        data["statusDoc5"] = False
                    else:
                        data["statusDoc5"] = True

                ## "Termo de cautela" ##
                if "Termo de cautela" not in  doc_ref["status"]:
                    data["statusDoc6"] = "Nao solicitado"
                else:
                    if doc_ref["status"]["Termo de cautela"] == False:
                        data["statusDoc6"] = False
                    else:
                        data["statusDoc6"] = True

                ## "Contrato social" ##
                if "Contrato social" not in  doc_ref["status"]:
                    data["statusDoc7"] = "Nao solicitado"
                else:
                    if doc_ref["status"]["Contrato social"] == False:
                        data["statusDoc7"] = False
                    else:
                        data["statusDoc7"] = True

                ## "Declaração de rol de herdeiros" ##
                if "Declaração de rol de herdeiros" not in  doc_ref["status"]:
                    data["statusDoc8"] = "Nao solicitado"
                else:
                    if doc_ref["status"]["Declaração de rol de herdeiros"] == False:
                        data["statusDoc8"] = False
                    else:
                        data["statusDoc8"] = True



                ## Declaração de união estável ##
                if "Declaração de união estável" not in  doc_ref["status"]:
                    data["statusDoc9"] = "Nao solicitado"
                else:
                    if doc_ref["status"]["Declaração de união estável"] == False:
                        data["statusDoc9"] = False
                    else:
                        data["statusDoc9"] = True

                ## Comprovante de vínculo com o segurado##
                if "Comprovante de vínculo com o segurado" not in  doc_ref["status"]:
                    data["statusDoc10"] = "Nao solicitado"
                else:
                    if doc_ref["status"]["Comprovante de vínculo com o segurado"] == False:
                        data["statusDoc10"] = False
                    else:
                        data["statusDoc10"] = True

                ## Cédula de financiamento ##
                if "Cédula de financiamento" not in  doc_ref["status"]:
                    data["statusDoc11"] = "Nao solicitado"
                else:
                    if doc_ref["status"]["Cédula de financiamento"] == False:
                        data["statusDoc11"] = False
                    else:
                        data["statusDoc11"] = True

                ## Cópia do domicílio bancário ##
                if "Cópia do domicílio bancário" not in  doc_ref["status"]:
                    data["statusDoc12"] = "Nao solicitado"
                else:
                    if doc_ref["status"]["Cópia do domicílio bancário"] == False:
                        data["statusDoc12"] = False
                    else:
                        data["statusDoc12"] = True


            ####obtendo arquivos###
            arquivos = db.collection("users").document(identBen).collection("beneficiario").document("requerimentos").collection("Documento de Identificação")
            arquivos_ref = arquivos.get()
            arquivos_ref_list=list(arquivos_ref)
            if(len(arquivos_ref_list)==0):
                data["statusDoc1"] = False
            else:
                data["statusDoc1"] = True
            # print(len(arquivos_ref_list))
            for arquivo in arquivos_ref:
                identArq = arquivo.to_dict()
                pathArquivo = identArq["imageStorage"]
                blob = bucket.blob(pathArquivo)
                #print("whaaat " + blob.public_url)
                link = blob.generate_signed_url(datetime.timedelta(seconds=1000), method='GET')
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
            ## obtendo cada campo ##
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
            data["Juridica"]=segurado["pessoaLegal"]

            
            
            ##obtendo status de cada documento E PEGAR PATH DE CADA UM##
            doc_ref = db.collection("users").document(identBen).collection("segurado").document("requerimentos")
            doc_ref = doc_ref.get()
            doc_ref = doc_ref.to_dict()
            if "status" not in doc_ref:
                ## todos os documentos para solicitar,com execeao dos obrigatorios ##
                data["statusDoc1"] = True
                data["statusDoc2"] = True
                data["statusDoc3"] = "Nao solicitado"
                data["statusDoc4"] = "Nao solicitado"
                data["statusDoc5"] = "Nao solicitado"
                data["statusDoc6"] = "Nao solicitado"
                data["statusDoc7"] = "Nao solicitado"
                data["statusDoc8"] = "Nao solicitado"
                data["statusDoc9"] = "Nao solicitado"

            else:
                ## testar documento por documento ##
                ## obrigatorios ##

                ## "Documento de Identificação" ##
                if "Documento de Identificação" not in  doc_ref["status"]:
                    data["statusDoc1"] = True
                else:
                    if doc_ref["status"]["Documento de Identificação"] == False:
                        data["statusDoc1"] = False
                    else:
                        data["statusDoc1"] = True

                ## "Certificado de óbito" ##
                if "Certificado de óbito" not in  doc_ref["status"]:
                    data["statusDoc2"] = True
                else:
                    if doc_ref["status"]["Certificado de óbito"] == False:
                        data["statusDoc2"] = False
                    else:
                        data["statusDoc2"] = True


                 ## nao-obrigatorios ##

                ## "Certidão de casamento" ##
                if "Certidão de casamento" not in  doc_ref["status"]:
                    data["statusDoc3"] = "Nao solicitado"
                else:
                    if doc_ref["status"]["Certidão de casamento"] == False:
                        data["statusDoc3"] = False
                    else:
                        data["statusDoc3"] = True

                ## "Declaração médica de morte natural" ##
                if "Declaração médica de morte natural" not in  doc_ref["status"]:
                    data["statusDoc4"] = "Nao solicitado"
                else:
                    if doc_ref["status"]["Declaração médica de morte natural"] == False:
                        data["statusDoc4"] = False
                    else:
                        data["statusDoc4"] = True
    
                ## "Laudo médico" ##
                if "Laudo médico" not in  doc_ref["status"]:
                    data["statusDoc5"] = "Nao solicitado"
                else:
                    if doc_ref["status"]["Laudo médico"] == False:
                        data["statusDoc5"] = False
                    else:
                        data["statusDoc5"] = True

                ## "GFIP/SEFIP" ##
                if "GFIP/SEFIP" not in  doc_ref["status"]:
                    data["statusDoc6"] = "Nao solicitado"
                else:
                    if doc_ref["status"]["GFIP/SEFIP"] == False:
                        data["statusDoc6"] = False
                    else:
                        data["statusDoc6"] = True

                ## "FRE" ##
                if "FRE" not in  doc_ref["status"]:
                    data["statusDoc7"] = "Nao solicitado"
                else:
                    if doc_ref["status"]["FRE"] == False:
                        data["statusDoc7"] = False
                    else:
                        data["statusDoc7"] = True

                ## "CAGED" ##
                if "CAGED" not in  doc_ref["status"]:
                    data["statusDoc8"] = "Nao solicitado"
                else:
                    if doc_ref["status"]["CAGED"] == False:
                        data["statusDoc8"] = False
                    else:
                        data["statusDoc8"] = True



                ## Nota fiscal das despesas funerais ##
                if "Nota fiscal das despesas funerais" not in  doc_ref["status"]:
                    data["statusDoc9"] = "Nao solicitado"
                else:
                    if doc_ref["status"]["Nota fiscal das despesas funerais"] == False:
                        data["statusDoc9"] = False
                    else:
                        data["statusDoc9"] = True
                

            ####obtendo status do processo##
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



# def obtemLinkArquivo(db,identBen,nomeDoc,tipoPesooa):
#             arquivos = db.collection("users").document(identBen).collection(tipoPesooa).document("requerimentos").collection(nomeDoc)
#             arquivos_ref = arquivos.get()
#             arquivos_ref_list=list(arquivos_ref)
#             print(len(arquivos_ref_list))
#             for arquivo in arquivos_ref:
#                 identArq = arquivo.to_dict()
#                 pathArquivo = identArq["imageStorage"]
#                 blob = bucket.blob(pathArquivo)
#                 link = blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET')
#                 link = link.replace("googleapis","cloud.google")
#                 return link
#                 break



# Codigo nao usado:
# Colocar data de dataNascimento
#dataNascimento = segurado["segurado"]["dataNascimento"]
#client = storage.Client()

#Create a reference from a Google Cloud Storage URI
# client = storage_google.Client(project="my-project")
# bucket = client.get_bucket("inklessapp-1922c.appspot.com")
# blob = Blob("meuBlob",bucket)
# print(blob.path)
