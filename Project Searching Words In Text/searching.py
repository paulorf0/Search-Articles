import numpy as np
import nltk
from nltk.tokenize import word_tokenize
import os
import io
import re
import PyPDF2
import requests

from GetArticles import SearchArticlesWithKeyWord

searchkeySet = set()
searchedPages = 0
keywordsArray = []
matrixDocumentsQuery = []
query_matrix = None


def explain():
    global searchkeySet, query_matrix, searchedPages
    
    keys = input("Forneça as palavras chaves que melhor adeque a pesquisa: ").split()
    
    for index, key in enumerate(keys):
    
        if index == len(keys) - 1:
            keywordsArray.append(key)
            break
        word = key + "+"
        keywordsArray.append(word)
        
    searchkey = input("Quais palavras você deseja buscar no texto: ").replace("-", "").split()
    searchedPages = int(int(input("Quantas páginas deseja pesquisar. Ex: 1 (primeira página), 2 (primeira e segunda página), ... ")) * 10)
    
    searchkeySet.update(searchkey)

    os.system('cls')
    
    rank = list(map(float, input("Forneça um \"rank\" de importância, na ordem em que as palavras foram inseridas, para cada palavra chave (De 0 a 1): ").split()))
    
    os.system('cls')
    query_matrix = np.array(rank).reshape(-1,1)

    


def GetText():
    words_text = []
    links = SearchArticlesWithKeyWord(keywordArray=keywordsArray, param=".pdf", NumPageSearched=searchedPages)

    for index, linkArray in enumerate(links):
        links[index] = list(set(linkArray))

    print(f"links: {links}")

    total_documents = sum(len(sublista) for sublista in links)
    current_document_number = 0
    
    CreateMatrix(total_documents)

    for linkArray in links:
        for link in linkArray:
            try:
                response = requests.get(link)
                
                #Talvez eu tenha que criar um arquivo temporario para o programa poder ler e apagar logo depois.
                #O servidor está recusando o pedido do python de ler o arquivo.  
                if response.status_code == 200:
                    
                    pdf_file = io.BytesIO(response.content)
                    pdf_reader = PyPDF2.PdfReader(pdf_file)

                    print(f"Site Atual: {link} e num_documentoAtual: {current_document_number} ")

                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
                        if len(text.strip()) != 0:
                            treat_text = Treat_Text(page.extract_text())
                            words_text.append(treat_text)
                        
                    SearchWord(words_text, current_document_number)

                words_text.clear()
            except:
                continue
            
            current_document_number += 1

        words_text.clear()
            


def CreateMatrix(total_documents):
    global matrixDocumentsQuery

    matrixDocumentsQuery = np.zeros((total_documents, len(searchkeySet), 1))


def SearchWord(words_text, current_document_number):
    global searchkeySet, matrixDocumentsQuery

    countWords = {}
    porcentWords = {}
    lenWordsInPage = 0
    
    for key in searchkeySet:
        countWords[key] = 0

    for word_in_page in words_text:
        lenWordsInPage += len(word_in_page)

    for word_in_page in words_text:
        for word in word_in_page:
            if word      in searchkeySet:
                countWords[word] = countWords.get(word, 0) + 1
        
    for key, valueKey in countWords.items():
        if lenWordsInPage != 0:
            porcentWords[key] = (valueKey / lenWordsInPage)
        else:
            porcentWords[key] = 0 

    matrix = np.zeros((len(searchkeySet), 1)) 
    
    for idx, (key, valueKey) in enumerate(porcentWords.items()):
        matrix[idx, 0] = valueKey 

    matrixDocumentsQuery[current_document_number, :, :] = matrix
  
    print(f"\nWords: {countWords}, WordsPage: {lenWordsInPage}, Porcent: {porcentWords}")
    print(f"Array: {matrix}")


def Treat_Text(text):
    words = [word.split('\n')[0].lower() for word in text.split()]
    specials = ['"', '-', '@', '!', '?', '”', '*', '”', '*', '“', '•', '\\n•', ',', '(', ')', '[', ']', '.', " ", ':', '{', '}', '^', '>', '<', ';', '/', '\\', '´', '`']
    soloWord = ["and", "for", 'our', 'you', 'the']
    others = [ '\n', '\t', '\\', '\'', '\"', '\x00', '\x01', '\x02', '\x03', '\x04', '\r', '\f', '\v', '\x19', '\x00', '\x7f', '=', '+']

    for character in specials:
        words = [word.replace(character, '') for word in words]

    tagged = nltk.pos_tag(words)
    articles_prepositions = ['DT', 'IN']

    words = [phrase for phrase, pos in tagged if pos not in articles_prepositions]

    index = len(words) - 1
    while index >= 0:
        word = words[index]

        for special in others:
            if word.find(special) != -1:
                words.pop(index)
                break

        index -= 1

    index = len(words) - 1
    while index >= 0:
        word = words[index]

        if (len(word) == 2) or (len(word) == 1) or word == '':
            words.pop(index)

        index -= 1 

    return words



explain()
GetText()

print(matrixDocumentsQuery)