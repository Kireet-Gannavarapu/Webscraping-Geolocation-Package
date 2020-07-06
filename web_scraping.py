import requests
from bs4 import BeautifulSoup
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from textblob import TextBlob
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import chromedriver_binary

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

def __getWebsite(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, features="html.parser")
    return soup

#This Function returns a list of all the headlines currently displayed on the website Times of India.
def getAllHeadlinesFromToI():
    soup = __getWebsite('https://timesofindia.indiatimes.com/home/headlines')
    headlines = [headline.get_text() for headline in soup.find_all('span', class_ = 'w_tle')]
    return headlines

"""This function returns two lists, first one is a list containing the headlines and second one is the actual article of the headline. 
The articles are extracted from the NDTV news website on the topic which is to be given in the function parameter"""
def getArticlesFromNDTV(topic):
    headlines = []
    articles = []

    soup = __getWebsite('https://www.ndtv.com/')
    news_headlines = soup.find_all('a', class_ = 'item-title')

    for headline in news_headlines:
        if topic.lower() in headline.get_text().lower():
            headlines.append(headline.get_text())
            subSoup = __getWebsite(headline.get('href'))
            articles.append("".join([x.get_text() for x in subSoup.find(id='ins_storybody').find_all('p')]))

    return headlines, articles

"""This function returns two lists, first one is a list containing the headlines and second one is the actual article of the headline. The articles are
extracted from the Cnet website on the topic which is to be given in the function parameter. It is to be noted that the function extracts data
from the tech reviews section of Cnet, so the topic is limited to tech / gadgets. The second parameter is to specify how many cnet pages the
program searches for the required information. The lower the number, the faster the search and the higher the number, the more detailed is the search
the range of the parameter pages is (1, 1000) """
def getArticlesFromCnet(topic, pages = 10):
    titles = []
    articles = []
    urls = ["https://www.cnet.com/reviews/"]

    for url in urls:
        soup = __getWebsite(url)
        headlines = soup.find_all('div', class_ = 'assetText')

        for headline in headlines:
            if topic.lower() in headline.h3.get_text().lower():
                titles.append(headline.h3.get_text())
                subSoup = __getWebsite("https://www.cnet.com" + headline.a.get('href'))
                articles.append("".join([x.get_text() for x in subSoup.find('div', class_ = 'article-main-body').find_all("p")]))

        if len(urls) <= min(pages, 1000):
            urls.append("https://www.cnet.com" + soup.find('a', class_ = 'next').get('href'))
    return titles, articles

"""This function returns two lists, first one is a list containing the headlines and second one is the actual article of the headline. The articles are
extracted from the TechRadar website on the topic which is to be given in the function parameter. Tech Radar website is specifically only for
tech related articles and tech reviews, so the topic is limited to tech/ gadgets """
def getArticlesFromTechRadar(topic):
    titles = []
    articles = []

    urls = ["https://www.techradar.com/reviews"]

    soup = __getWebsite(urls[0])
    pages = soup.find('ul', class_ = 'pagination-numerical-list').find_all('a')
    for page in pages:
        urls.append(page.get('href'))

    urls = urls[:-1]

    for url in urls:
        soup = __getWebsite(url)
        headlines = soup.find_all('div', class_ = 'listingResult')

        for headline in headlines:
            if headline.h3 is not None:
                if topic.lower() in headline.h3.get_text().lower():
                    subSoup = __getWebsite(headline.a.get('href'))
                    titles.append(headline.h3.get_text())
                    articles.append("".join([x.get_text() for x in subSoup.find(id = 'article-body').find_all("p")]))
    return titles, articles

"""This function returns two lists, first one is a list containing the headlines and second one is the actual article of the headline. The articles are
extracted from the Tom's Guide website on the topic which is to be given in the function parameter. Tom's guide is specifically only for
tech related articles and tech reviews, so the topic is limited to tech/ gadgets """
def getArticlesFromTomsGuide(topic):
    titles = []
    articles = []

    urls = ["https://www.tomsguide.com/reviews"]

    soup = __getWebsite(urls[0])
    pages = soup.find('ul', class_ = 'pagination-numerical-list').find_all('a')
    for page in pages:
        urls.append(page.get('href'))

    urls = urls[:-1]

    for url in urls:
        soup = __getWebsite(url)
        headlines = soup.find_all('a', class_ = 'article-link')

        for headline in headlines:
            if topic.lower() in headline.h3.get_text().lower():
                subSoup = __getWebsite(headline.get('href'))
                titles.append(headline.h3.get_text())
                articles.append("".join([x.get_text() for x in subSoup.find(id = 'article-body').find_all('p')]))
    return titles, articles

"""This function returns the reviews on a specific gadget or tech related item. The information is extracted from Cnet, TechRadar, Tom's guide.
The function has three optional parameters. by default, all of them are true. but by specifying (Cnet = False), the function does not extract info
from cnet and gives it from the other two websites. The same is true for other two parameters """
def gadgetReviews(topic, Cnet = True, TechRadar = True, TomsGuide = True):
    titles = []
    articles = []
    articleDict = {}
    i = 0

    if Cnet == True:
        title, article = getArticlesFromCnet(topic, 10)
        titles.extend(title)
        articles.extend(article)

    if TechRadar == True:
        title2, article2 = getArticlesFromTechRadar(topic)
        titles.extend(title2)
        articles.extend(article2)

    if TomsGuide == True:
        title3, article3 = getArticlesFromTomsGuide(topic)
        titles.extend(title3)
        articles.extend(article3)

    for title in titles:
        articleDict[title] = articles[i]
        i += 1
    return articleDict

""" This is a class which handles text summarization. The constructor takes in a string as input and an optional parameter "percent"
percent describes the percentage of sentences to be left after summarization. Example, if the initial paragraph has 100 sentences
by mentioning pencent = 50, the summary will have 50 sentences. By default, the percentage is set to 20%
Class Methods: 1) TextSummarization.summarize(), this method returns the summary of the paragraph
2) TextSummarization.compareWordCount(), this method returns an array whose first element is the word count of the summary and the 
second element is the word count of the original paragraph 
3) textSummarization.sentimentAnalysis(), this method returns the sentiment of the final summary """
class TextSummarization():
    def __init__(self, paragraph, percent = 20):
        self.paragraph = paragraph
        self.percent = percent
        stopwords = list(STOP_WORDS)
        nlp = spacy.load('en_core_web_sm')
        docx = nlp(paragraph)

        tokens = [token.text for token in docx]

        for i in punctuation:
            stopwords.append(i)

        word_frequencies = {}
        for word in tokens:
            if word.lower() not in stopwords:
                if word.lower() not in word_frequencies.keys():
                    word_frequencies[word.lower()] = 1
                else:
                    word_frequencies[word.lower()] += 1

        max_frequency = max(word_frequencies.values())
        for word in word_frequencies.keys():
            word_frequencies[word] = (word_frequencies[word]/max_frequency)

        sentence_tokens = [sentence for sentence in docx.sents]

        self.sentence_scores = {}

        for sent in sentence_tokens:
            for word in sent:
                if word.text.lower() in word_frequencies.keys():
                    if sent not in self.sentence_scores.keys():
                        self.sentence_scores[sent] = word_frequencies[word.text.lower()]
                    else:
                        self.sentence_scores[sent] += word_frequencies[word.text.lower()]

        self.sentTokenLength = len(sentence_tokens)

    def summarize(self):
        from heapq import nlargest
        finalSentenceCount = int(self.sentTokenLength* self.percent * 0.01)
        summarized_sentences = nlargest(finalSentenceCount, self.sentence_scores, key = self.sentence_scores.get)
        summary = " ".join(w.text for w in summarized_sentences)
        return summary

    def compareWordCount(self):
        summaryLength = len((self.summarize()).split(" "))
        originalLength = len((self.paragraph).split(" "))

        return {"original": originalLength, "final": summaryLength}

    def sentimentAnalysis(self):
        return TextBlob(self.summarize()).sentiment


def getNSEData(company):

    if "_" in company:
        company = " ".join(company.split("_"))

    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get("https://economictimes.indiatimes.com/markets")

    driver.find_element_by_name("ticker").send_keys(company)
    driver.find_element_by_name("ticker").send_keys(Keys.ENTER)

    nseTradeprice = driver.find_element_by_id("nseTradeprice").text
    nseOpenprice = driver.find_element_by_id("nseOpenprice").text
    nseCloseprice = driver.find_element_by_id("nseCloseprice").text
    nsetodaychange = driver.find_element_by_id("nseNetchange").text
    today_low = driver.find_element_by_css_selector(".dt_lh div:nth-of-type(1) div").text
    today_high = driver.find_element_by_css_selector(".dt_lh div:nth-of-type(2) div").text
    week52_high_low = driver.find_element_by_css_selector(".d2 ul li:nth-of-type(5) span:nth-of-type(2)").text
    driver.quit()

    resp = {"Trade Price": nseTradeprice, "Open Price": nseOpenprice, "Close Price": nseCloseprice, "Net Change today": nsetodaychange, "Today's low": today_low, "Today's high": today_high, "52 week low": (week52_high_low).split("/")[0], "52 week high": (week52_high_low).split("/")[1]}

    return resp

def getCompanyInfo(company):
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get("https://economictimes.indiatimes.com/markets")

    driver.implicitly_wait(5)
    driver.find_element_by_name("ticker").send_keys(company)
    driver.find_element_by_name("ticker").send_keys(Keys.ENTER)

    link = driver.find_element_by_css_selector("#newsRecosData a").get_attribute("href")

    soup = __getWebsite(link)

    news = [x.find("a").get("href") for x in soup.find_all("div", class_ = "eachStory") if "News" in x.find("span").get_text()]

    articles = []
    for new in news:
        subSoup = __getWebsite("https://economictimes.indiatimes.com" + new)

        if subSoup.find("div", class_ = "Normal") is not None:
            articles.append(subSoup.find("div", class_ = "Normal").get_text())

    
    driver.quit()

    return articles