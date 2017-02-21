#-------------------------------------------------------------------------------
# Name:
# Purpose:
#
# Author:      Alberto, Andre
#
# Created:     18/02/2017
# Copyright:   (c)
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#Todo: ler os dados
#Todo: selecionar as cocitacoes no intervalor de tempo designado
#Todo: criar os clusters
#Todo: Dentro dos cluster nomealos atraves das palavras chaves

#Todo: Criar tres periodos tempo

#Todo: Verificar o crescimento de certas palavras chaves na rede de cocitacoes


def init_doc():
    result = {'author_list': [],
              'publication_year': 0,
              'reference_list': [],
              'doi': '',
              'title': '',
              'keyword_list': []}
    return result


def split_field(line_string):
    field_string = ""
    value_string = ""
    index = 0
    while index < len(line_string):
        if index < 2:
            field_string += line_string[index]
        elif index > 2:
            value_string += line_string[index]
        index += 1
    return field_string, value_string

def load_doc_list(file_name):

    doc_list = []
    file_handle = open(file_name, 'r')
    if not file_handle:
        exit('load_doc_list')
    file_string = file_handle.read()
    file_lines = file_string.split('\n') #NOTE: no windows retirar '\r'
    keyword_string = ""
    line_index = 0
    doc = init_doc()
    for line_index in range(len(file_lines)):
        line_string = file_lines[line_index]
        line_field, line_value = split_field(line_string)
        if line_field == "  ":
            line_field = last_field
        if line_field == "FN" or line_field == "VR" or line_field == "":
            pass
        elif line_field == "PT":
            del doc
            doc = init_doc()
        elif line_field == "ER":
            keyword_list = keyword_string.split(";")
            for keyword in keyword_list:
                if len(keyword) > 1 and keyword[0] == " ":
                    keyword = keyword[:0] + keyword[1:]
                if keyword != "":
                    doc['keyword_list'].append(keyword)
            keyword_string = ""
            doc_list.append(doc)
        elif line_field == "CR":
            doc['reference_list'].append(line_value)
        elif line_field == "UT":
            doc['doi'] = line_value
        elif line_field == "PY":
            doc['publication_year'] = int(line_value)
        elif line_field == "ID":
            keyword_string += (" " + line_value)
        elif line_field == "AU":
            doc['author_list'].append(line_value)
        else:
            pass
        last_field = line_field
    return doc_list
##############################
#aqui selecionamos o intervalo de ano
def selectyeras(x,MINYEAR,MAXYEAR):
    keyword=[]
    for i in x:
        if i['publication_year']>=MINYEAR and i['publication_year']<=MAXYEAR :

            LL=i['reference_list']
            LL.sort()

            keyword.append(LL)
    return keyword

def selectONEyear(x,YEAR):
    keyword=[]
    for i in x:
        if i['publication_year']==YEAR :

            LL=i['keyword_list']
            LL.sort()

            keyword.append(LL)
    return keyword

def listaparatupla(vetorlist):
    vetor =[]
    for i in vetorlist:
        i.sort()
        for j in range (0,len(i)-1):
            for k in range(j+1,len(i)):
                vetor.append((i[j],i[k]))
                #vetor.append(str(i[j])+' and '+str(i[k]))

    return vetor

##################################
#abrindo os arquivos e usando o metodo selectyearas
x=load_doc_list("downloads_1.txt")
keyword=[]
keyword = selectyeras(x,2000,2005)

vetorlista = listaparatupla(keyword)