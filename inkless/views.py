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
bucket = storage.bucket(app=app)


# Variáveis Globais
numSegurado = 0
identBen = ""
pessoaLegal = False


# Função retornaData: Recebe uma data no formato Timestamp do Firebase e retorna a mesma no formato dd/mm/aaaa
def retornaData(dataNasc):
            if dataNasc == "":
                return ""
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

            
            


# Função home: Retorna o template com a página inicial.  
def home(request): 
    data = {}
    listaSegurados=[]
    listaPropostas=[]
    doc_ref = db.collection(u'users')
    docs = doc_ref.get()
    for doc in docs:
        segurado = doc.to_dict()
        listaSegurados.append(segurado["segurado"]["nomeCompleto"])
        if "numeroProposta" in segurado["segurado"] and segurado["segurado"]["numeroProposta"] != "":
            listaPropostas.append(segurado["segurado"]["numeroProposta"])
        else:
            listaPropostas.append("12345")
    data["listaTabela"] = zip(listaSegurados, listaPropostas)
    return render(request, 'inkless/tabelaSeguradora.html',data)



# Função paginaBeneficiario: Retorna o template com a página do beneficiario.  
def paginaBeneficiario(request):
    global identBen
    data={}
    doc_ref = db.collection('users')
    docs = doc_ref.get()
    i = 1
    cont = 0
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
            data["dataDeNasc"] = dataDeNasc
            data["email"] = beneficiario["email"]
            data["registroGeral"] = beneficiario["registroGeral"]


            if "dataExpedicao" in beneficiario:
                data["dataExpedicao"] = retornaData(beneficiario["dataExpedicao"])
            else:
                data["dataExpedicao"] = ""           
            
            if "faixaRenda" in beneficiario:
                data["faixaRenda"] = beneficiario["faixaRenda"]
            else:
                data["faixaRenda"] = "" 

            if "pessoaPoliticamenteExposta" in beneficiario:
                data["pessoaPoliticamenteExposta"] = beneficiario["pessoaPoliticamenteExposta"]
            else:
                data["pessoaPoliticamenteExposta"] = ""   

            if "telefone" in beneficiario:
                data["telefone"] = beneficiario["telefone"]
            else:
                data["telefone"] = ""

            if "celular" in beneficiario:
                data["celular"] = beneficiario["celular"]
            else:
                data["celular"] = ""

            if "grauParentesco" in beneficiario:
                data["grauParentesco"] = beneficiario["grauParentesco"]
            else:
                data["grauParentesco"] = ""
  
            if "orgãoEmissor" in beneficiario:
                data["orgãoEmissor"] = beneficiario["orgãoEmissor"]
            else:
                data["orgãoEmissor"] = ""

            if "profissao" in beneficiario:
                data["profissao"] = beneficiario["profissao"]
            else:
                data["profissao"] = ""

            if "fiscalExterior" in beneficiario:
                data["fiscalExterior"] = beneficiario["fiscalExterior"]
            else:
                data["fiscalExterior"] = ""

            if "fiscalExterior" in beneficiario:
                data["fiscalExterior"] = beneficiario["fiscalExterior"]
            else:
                data["fiscalExterior"] = ""
            
            if "endereco" in beneficiario:
                data["existeEndereco"] = True
                if "endereco" in beneficiario["endereco"]:
                    data["endereco"] = beneficiario["endereco"]["endereco"]
                else:
                    data["endereco"] = ""

                if "bairro" in beneficiario["endereco"]:
                    data["bairro"] = beneficiario["endereco"]["bairro"]
                else:
                    data["bairro"] = ""

                if "cep" in beneficiario["endereco"]:
                    data["cep"] = beneficiario["endereco"]["cep"]
                else:
                    data["cep"] = ""

                if "cidade" in beneficiario["endereco"]:
                    data["cidade"] = beneficiario["endereco"]["cidade"]
                else:
                    data["cidade"] = ""

                if "complemento" in beneficiario["endereco"]:
                    data["complemento"] = beneficiario["endereco"]["complemento"]
                else:
                    data["complemento"] = ""

                if "numero" in beneficiario["endereco"]:
                    data["numero"] = beneficiario["endereco"]["numero"]
                else:
                    data["numero"] = ""
            else:
                data["existeEndereco"] = False


            ##obtendo status do processo##
            status_ref = db.collection("users").document(identBen)
            statusDict = status_ref.get()
            statusDict = statusDict.to_dict()
            if "status" in statusDict:
                data["status"]=statusDict["status"]
            else:
                data["status"]="Aviso"




           ##obtendo status de cada documento#
            doc_ref = db.collection("users").document(identBen).collection("beneficiario").document("requerimentos")
            documentos = doc_ref.get().to_dict()["documents"]
            for doc in documentos:
                if cont != 0:
                    if  doc["completed"] == True:
                        data["statusDoc" + str(cont)] = True
                        link = obtemLinkArquivo(doc_ref,identBen,doc["requirement"])
                        data["link" + str(cont)] = link
                    else:
                        if doc["optional"] == True:
                            data["statusDoc" + str(cont)] = "Nao solicitado"
                        else:
                            data["statusDoc" + str(cont)] = False
                cont = cont + 1
            break
        i = i + 1
    return render(request, 'inkless/paginaBeneficiario.html',data)



# Função paginaSegurado: Retorna o template com a página do segurado. 
def paginaSegurado(request):
    global identBen
    global pessoaLegal
    data={}
    doc_ref = db.collection('users')
    docs = doc_ref.get()
    i = 1
    cont = 0
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
            if "numeroProposta" in segurado["segurado"]:
                data["numeroProposta"] = segurado["segurado"]["numeroProposta"]
            else:
                data["numeroProposta"]=""
            identBen = segurado["uid"]
            if "matricula" in segurado["segurado"]:
                data["matricula"]=segurado["segurado"]["matricula"]
            else:
                 data["matricula"]=""
            if "plano" in segurado["segurado"]:
                data["plano"]=segurado["segurado"]["plano"]
            else:
                 data["plano"]=""
            if "nomeEstipulante" in segurado["segurado"]:
                data["nomeEstipulante"]=segurado["segurado"]["nomeEstipulante"]
            else:
                 data["nomeEstipulante"]=""
            pessoaLegal = segurado["pessoaLegal"]  
            data["Juridica"]=pessoaLegal

            
            
            ##obtendo status de cada documento##
            doc_ref = db.collection("users").document(identBen).collection("segurado").document("requerimentos")
            documentos = doc_ref.get().to_dict()["documents"]
            for doc in documentos:
                if  doc["completed"] == True:
                    data["statusDoc" + str(cont)] = True
                    link = obtemLinkArquivo(doc_ref,identBen,doc["requirement"])
                    data["link" + str(cont)] = link
                else:
                    if doc["optional"] == True:
                        data["statusDoc" + str(cont)] = "Nao solicitado"
                    else:
                        data["statusDoc" + str(cont)] = False
                cont = cont + 1



                

            ####obtendo status do processo##
            status_ref = db.collection("users").document(identBen)
            statusDict = status_ref.get()
            statusDict = statusDict.to_dict()
            if "status" not in statusDict:
                data["status"]="Aviso"
            else:
                data["status"] = statusDict["status"]

            break
        i = i + 1
    return render(request, 'inkless/paginaSegurado.html',data)

# Função obtemNomeSegurado: Obtem o segurado selecionado
def obtemNomeSegurado(request):
    global numSegurado
    numSegurado = request.POST.get('nomeSegurado')
    return HttpResponse('success') 

# Função atualizaStatusDocBeneficiario: Solicita o documento requisitado na página do beneficiário
def atualizaStatusDocBeneficiario(request):
    nomeDoc = request.POST.get('nomeDoc')
    doc_ref = db.collection("users").document(identBen).collection("beneficiario").document("requerimentos")
    meu_doc = doc_ref.get().to_dict()
    seenMessage = meu_doc["seenDocumentsMessage"]
    if nomeDoc == "Documento de identificação":          
        meu_doc["documents"][1]["optional"] = False
        meu_doc["documents"][1]["completed"] = False
    elif  nomeDoc == "CPF":
        meu_doc["documents"][2]["optional"] = False
        meu_doc["documents"][2]["completed"] = False
    elif nomeDoc == "Comprovante de residência":
        meu_doc["documents"][3]["optional"] = False
        meu_doc["documents"][3]["completed"] = False
    elif nomeDoc == "Informações tributárias complementares":
        meu_doc["documents"][4]["optional"] = False
        meu_doc["documents"][4]["completed"] = False
    elif nomeDoc == "Certidão de casamento ou nascimento":
        meu_doc["documents"][5]["optional"] = False
        meu_doc["documents"][5]["completed"] = False
    elif nomeDoc == "Termo de tutela":
        meu_doc["documents"][6]["optional"] = False
        meu_doc["documents"][6]["completed"] = False
    elif nomeDoc == "Termo de curatela":
        meu_doc["documents"][7]["optional"] = False
        meu_doc["documents"][7]["completed"] = False
    elif nomeDoc == "Declaração de rol de herdeiros":
        meu_doc["documents"][8]["optional"] = False
        meu_doc["documents"][8]["completed"] = False
    elif nomeDoc == "Declaração de união estável":
        meu_doc["documents"][9]["optional"] = False
        meu_doc["documents"][9]["completed"] = False
    elif nomeDoc == "Nota fiscal das despesas funerais":
        meu_doc["documents"][10]["optional"] = False
        meu_doc["documents"][10]["completed"] = False
        

    doc_ref.set({u'documents':meu_doc["documents"],
                 u'seenDocumentsMessage':seenMessage})
    
    return HttpResponse('success')


# Função atualizaStatus: Atualiza a mudanças no status do processo
def atualizaStatus(request):
    status = request.POST.get('statusProc')
    doc_ref = db.collection("users").document(identBen)
    doc_ref.set({u'status':status}, merge=True)
    return HttpResponse('success') # if everything is OK
    


# Função atualizaStatusDocSegurado: Solicita o documento requisitado na página do segurado
def atualizaStatusDocSegurado(request):
    nomeDoc = request.POST.get('nomeDoc')
    doc_ref = db.collection("users").document(identBen).collection("segurado").document("requerimentos")
    meu_doc = doc_ref.get().to_dict()
    seenMessage = meu_doc["seenDocumentsMessage"]
    if nomeDoc == "GFIP/SEFIP":          
        meu_doc["documents"][7]["optional"] = False
        meu_doc["documents"][7]["completed"] = False
    elif nomeDoc == "FRE":          
        meu_doc["documents"][8]["optional"] = False
        meu_doc["documents"][8]["completed"] = False
    elif nomeDoc == "CAGED":          
        meu_doc["documents"][9]["optional"] = False
        meu_doc["documents"][9]["completed"] = False
    elif nomeDoc == "Documento de identificação do representante da empresa":          
        meu_doc["documents"][10]["optional"] = False
        meu_doc["documents"][10]["completed"] = False
    elif nomeDoc == "Contrato social ou Estatuto social":          
        meu_doc["documents"][11]["optional"] = False
        meu_doc["documents"][11]["completed"] = False
    elif nomeDoc == "CPF do representante da empresa":          
        meu_doc["documents"][12]["optional"] = False
        meu_doc["documents"][12]["completed"] = False
    elif nomeDoc == "Comprovante de vínculo do segurado com o estipulante":          
        meu_doc["documents"][13]["optional"] = False
        meu_doc["documents"][13]["completed"] = False
    elif nomeDoc == "Cédula de financiamento":          
        meu_doc["documents"][14]["optional"] = False
        meu_doc["documents"][14]["completed"] = False
    elif nomeDoc == "Cópia do comprovante de endereço em nome da pessoa jurídica":          
        meu_doc["documents"][15]["optional"] = False
        meu_doc["documents"][15]["completed"] = False
    if nomeDoc == "Documento de identificação":          
        meu_doc["documents"][1]["optional"] = False
        meu_doc["documents"][1]["completed"] = False
    elif  nomeDoc == "CPF":
        meu_doc["documents"][2]["optional"] = False
        meu_doc["documents"][2]["completed"] = False
    elif nomeDoc == "Declaração médica de morte natural":
        meu_doc["documents"][3]["optional"] = False
        meu_doc["documents"][3]["completed"] = False
    elif nomeDoc == "Laudo médico":
        meu_doc["documents"][4]["optional"] = False
        meu_doc["documents"][4]["completed"] = False
    elif nomeDoc == "Certificado de óbito":
        meu_doc["documents"][5]["optional"] = False
        meu_doc["documents"][5]["completed"] = False
    elif nomeDoc == "Certidão de casamento ou nascimento":
        meu_doc["documents"][6]["optional"] = False
        meu_doc["documents"][6]["completed"] = False
        

    doc_ref.set({u'documents':meu_doc["documents"],
                 u'seenDocumentsMessage':seenMessage})
    
    return HttpResponse('success') 







# Função obtemLinkArquivo: Obtem o link para visualização do documento solicitado
def obtemLinkArquivo(db,identBen,nomeDoc):
    arquivos = db.collection(nomeDoc).order_by('photoName',direction=firestore.Query.DESCENDING)
    arquivos_ref = arquivos.get()
    link = ""
    for arquivo in arquivos_ref:
        arquivoDoc = arquivo.to_dict()
        pathArquivo = arquivoDoc["imageStorage"]
        blob = bucket.blob(pathArquivo)
        link = blob.generate_signed_url(datetime.timedelta(seconds=1000), method='GET')
        link = link.replace("googleapis","cloud.google")
        break
    return link




