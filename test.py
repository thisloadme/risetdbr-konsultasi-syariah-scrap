import requests
from bs4 import BeautifulSoup
import os
from selenium import webdriver
import urllib.parse
import re
import csv
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

def preprocessing(text):
    stop_words = set(stopwords.words('indonesian'))
    # word_tokens = word_tokenize(text)

    # kata_terfilter = [w for w in word_tokens if not w.lower() in stop_words]
    # text = ' '.join(kata_terfilter)
    # text = text.replace(' .', '.').replace(' ,', ',').replace(" '", "'").replace(' "', '"')
    # return text

    for stop_word in stop_words:
        text = text.replace(' '+stop_word+' ', ' ')
    
    return text

dataset = ""
scraped_pages = 40
offset_pages = 30
for page in range((offset_pages + 1), (scraped_pages + offset_pages + 1)):
    url = 'https://konsultasisyariah.com/page/' + str(page)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all('li', {'class': 'post'})

    for post in posts:
        judul_post = post.find('h2', {'class': 'title'})
        if judul_post == None:
            continue
        judul_post = judul_post.get_text()

        url_post = post.find('a')
        if url_post == None:
            continue
        url_post = url_post['href']

        response_post = requests.get(url_post)
        response_soup = BeautifulSoup(response_post.text, 'html.parser')
        response_text = response_soup.find('div', {'class': 'entry-content'})
        if response_text == None:
            continue
        isi_post_raw = response_text.get_text()

        # tes = preprocessing(isi_post)
        list_kalimat = [re.sub("[^A-Za-z0-9.,:;'\"\\&%!()-_ ]", '', sent) for sent in sent_tokenize(isi_post_raw)]
        list_kalimat = [re.sub(r" : ", ' ', sent) for sent in list_kalimat]
        list_kalimat = [re.sub(r" - ", ' ', sent) for sent in list_kalimat]
        list_kalimat = [re.sub(r"\s+", ' ', sent) for sent in list_kalimat]

        panjang_kalimat = len(list_kalimat)
        idx_dijawab_oleh = [i for i,s in enumerate(list_kalimat) if 'dijawab oleh' in s.lower()]
        idx_dijawab_oleh = idx_dijawab_oleh[0] if len(idx_dijawab_oleh) > 0 else (panjang_kalimat - 5)

        list_kalimat = list_kalimat[:(idx_dijawab_oleh-panjang_kalimat)]
        isi_post = ' '.join(list_kalimat)

        dataset = dataset + judul_post + "\n" + isi_post + "\n\n"
        print('post', post, 'page', page, '/', scraped_pages)

with open("dataset.txt", "r") as f:
  content = f.read()

file = open("dataset.txt", "w")
file.write(content + dataset)
file.close()