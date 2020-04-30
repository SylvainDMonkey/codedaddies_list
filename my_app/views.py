import requests
from requests.compat import quote_plus
from django.shortcuts import render
from bs4 import BeautifulSoup

from . import models

#Récupérer l'URL de craiglist afin de faire du web-scrapping
BASE_CRAIGLIST_URL =  'https://paris.craigslist.org/search/?query={}'
#Récupérer l'URL des images de la craiglist afin de faire du web-scrapping
BASE_IMAGE_URL = 'https://images.craigslist.org/{}_300x300.jpg'

# Create your views here.
def home(request):
    return render(request, 'base.html')

def new_search(request):
    
    #Récupérer l'objet de la requête passé en arfument d ela méthode
    search = request.POST.get('search')
    
    #Récupérer l'objet de la requête afin de la récupérer en BDD (utile pour avoir les recherches favorites)
    models.Search.objects.create(search=search)
    
    #Quote plus (import) afin de mettre un + à la place des espaces pour l'URL
    final_url = BASE_CRAIGLIST_URL.format(quote_plus(search))
    
    #Pour rendre l'URL plus lisible pour les humains
    response = requests.get(final_url)
    
    #Pour récupérer les balises html
    data = response.text
    
    #BeautifulSoup afin de parser l'URL
    soup = BeautifulSoup(data, features='html.parser')
    
    #findAll pour trouver les balises qui nous intéresse, ici les liens a et la classe result-title
    # post_tiltle = soup.findAll('a', {'class':'result-title'})
    # print(post_tiltle)
    # #Pour récupérer le 1er lien
    # print(post_tiltle[0])
    # #Pour récupérer le texte du 1er lien
    # print(post_tiltle[0].text)
    # #Pour récupérer le lien uniquement
    # print(post_tiltle[0].get('href'))
    
    #findAll pour trouver les balises qui nous intéresse, ici les balise <li> et la classe result-row
    post_listings = soup.find_all('li', {'class': 'result-row'})
    final_postings = []

    for post in post_listings:
        post_title = post.find(class_='result-title').text
        post_url = post.find('a').get('href')

        if post.find(class_='result-price'):
            post_price = post.find(class_='result-price').text
        else:
            post_price = 'N/A'

        if post.find(class_='result-image').get('data-ids'):
            post_image_id = post.find(class_='result-image').get('data-ids').split(',')[0].split(':')[1]
            post_image_url = BASE_IMAGE_URL.format(post_image_id)
            print(post_image_url)
        else:
            post_image_url = 'https://craigslist.org/images/peace.jpg'

        final_postings.append((post_title, post_url, post_price, post_image_url))

    stuff_for_frontend = {
        'search': search,
        'final_postings': final_postings,
    }
    
    return render(request, 'my_app/new_search.html', stuff_for_frontend)
