import requests
from bs4 import BeautifulSoup
import time

excluded_words = ["+-book", "+filetype%3Apdf"]
filter_links = [".pdf"]


#Essa função é para a página do google academico. Deve personalizar para cada site pesquisado.
def ExtractLinkOfArticle(url, param):
    response = requests.get(url)
    print(f"Resposta http ao site de pesquisa: {response.status_code}")
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        titles = soup.find_all('h3', class_='gs_rt')
        a_ = soup.find_all(id='gs_res_ccl_mid')
        a = []
        
        for element in a_:
            element_a = element.find_all('a')
            a.extend(element_a)


        #.find('div', class_='gs_r gs_or gs_scl').find('div', class_='gs_ggs gs_fl').find('div', class_='gs_ggsd').find('div', class_="gs_or_ggsm gs_press").find('a')
        #print(f"a: {a}, len(a): {len(a)}\n\ntitle: {titles}\n\n")

        
        

        #Posso colocar uma opção de filtrar por links com certos parametros inclusos.
        links = []
        if param == ".pdf":
            links_title = [title.find('a')['href'] for title in titles if title.find('a') and any(word in title.find('a')['href'] for word in filter_links)]
            links_a = [a_['href'] for a_ in a if any(word in a_['href'] for word in filter_links)]
            
            #print(f"links-a: {links_a}\n\nlinks-title: {links_title}\n\n")

            links.extend(links_title)
            links.extend(links_a)
            return links
        else:
            links = [title.find('a')['href'] for title in titles if title.find('a')]
            return links
    else:
        return []

def SearchArticlesWithKeyWord(keywordArray, param, NumPageSearched):
    #keyword = ["Physics+", "Negative+", "Mass"]
    keyword = ""
    
    links = []
    
    for word in keywordArray:
        keyword += word

    for ExcludedWord in excluded_words:
        keyword += ExcludedWord

    #print(f"keyword em getarticles: {keyword}")
    for pagesNum in range(0, NumPageSearched, 10):
        url = f"https://scholar.google.com.br/scholar?start={pagesNum}&q={keyword}&hl=pt-BR&as_sdt=0,5"
        linkResults = ExtractLinkOfArticle(url, param)
        if linkResults:
            links.append(linkResults)
        
        #time.sleep(10) 
        #Pode adicionar uma lógica mais consistente para o tempo de espera.
        #Caso envie um request para outras páginas, funciona. Pode haver uma lógica de enviar request para uma página
        #e depois para outra. Alternando entre as páginas que pesquisa.
     
    return links

#links = SearchArticlesWithKeyWord( ["Physics+", "Negative+", "Mass"], ".pdf", 10)
