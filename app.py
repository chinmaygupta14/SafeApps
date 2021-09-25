from flask import Flask,render_template,url_for,request
from google_play_scraper import app,Sort, reviews 
from app_store_scraper import AppStore
import nltk
nltk.download('stopwords')
nltk.download('punkt')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re


app = Flask(__name__)

@app.route('/')
def home():
	return render_template('landingPage.html')

@app.route('/google')
def google():
	return render_template('googlePredict.html')

@app.route('/apple')
def apple():
	return render_template('applePredict.html')

@app.route('/home')
def landingPage():
	return render_template('landingPage.html')

def getScore(data):
    cleandata = re.sub('[^A-Za-z0-9]+',' ',data)
    low=cleandata.lower()

    stop=set(stopwords.words('english'))
    wordstoken=word_tokenize(low)

    sentences=[w for w in wordstoken if not w in stop]
    sentences=[]


    for w in wordstoken:
        if w not in stop:
            sentences.append(w)

    total=0
    tot=0
    positive = open("positive.txt", "r",encoding='utf-8')
    negative = open("negative.txt", "r",encoding='utf-8')
    pos=positive.read().split()
    neg=negative.read().split()
    for word in sentences:
        tot=tot+1
        if word in pos:
            total=total+1
        if word in neg:
            total=total-1
            
    score=total/tot
    return score

@app.route('/googlePredict',methods=['POST'])
def googlePredict():
    score=0
    if request.method == 'POST':
        url = request.form['url']
        
        link=url
        findId=link.find('id=')    
        url=link[findId+3:]
        result, continuation_token = reviews(
            url,
            lang='en', # defaults to 'en'
            country='us', # defaults to 'us'
            sort=Sort.MOST_RELEVANT, # defaults to Sort.MOST_RELEVANT
            count=200, 
        )

        result, _ = reviews(
            url,
            continuation_token=continuation_token # defaults to None(load from the beginning)
        )
        appReviews = ""
        for review in result:
            appReviews += review['content']
        
        score = getScore(appReviews)        

    return render_template('result.html',score = score)

@app.route('/applePredict',methods=['POST'])
def applePredict():
    score=0
    if request.method == 'POST':
        url = request.form['url']
        link=url
        start=link.find('/app/')
        end = link.find('/id')
        appName = link[start+5:end]
        app = AppStore(country="nz", app_name=appName)
        app.review(how_many=200)
        reviews = app.reviews
        reviews
        appReviews = ""
        for review in reviews:
            appReviews+=review['review']
        score = getScore(appReviews) 
    return render_template('result.html',score = score)


if __name__ == '__main__':
	app.run(debug=True)