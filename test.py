import re
import csv
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup


def openBrowser(url):
    opts = Options()
    opts.headless = True
    browser = Firefox(options=opts)
    browser.get(url)
    tmp = browser.find_element_by_class_name("wrapper").get_attribute("outerHTML")
    findAllPersons(tmp)
    browser.close()
    return tmp

def findAllPersons(text):
    home = "https://leader-id.ru"
    file = open("people.csv", "w", encoding='utf-8')
    fieldnames = ['Name', 'Email', 'Social', 'Rank', 'Place']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    soup = BeautifulSoup(text)
    row = soup.find("div", {"class": "row"})
    persons = row.find_all("div", {"class": "col-sm-5"})
    for person in persons:
        hrefA = person.find("a", {"class": "participant__photo"}).get("href")
        elementUser = openBrowser(home + hrefA)
        leaderInfo = parsPerson(elementUser)
        if leaderInfo != -1:
            writer.writerow(leaderInfo)




def parsPerson(text):
    soup = BeautifulSoup(text)
    name = soup.find("h2", {"class": "profile__name"}).text
    wrapperContent = soup.find("div", {"class": "wrapper__content"})
    profileContent = wrapperContent.find("div", {"class": "section--white"}).find("div", {"class": "profile__content"})
    profInfo = profileContent.find("div", {"class": "profile__info"})
    vk = ''
    email = ''
    try:
        email = profInfo.find_all("div", {"class": "profile__info-section"})[1].find("p").text
        re.search(r'@', email)
    except:
        try:
            socials = profInfo.find_all("div", {"class": "profile__info-section"})[1].find("div", {"class": "socials"})
            vk = socials.find("a", {"class": "socials__item--vk"}).get("href")
        except:
            return -1
    rank = profInfo.find_all("div", {"class": "profile__info-section"})[0].find("h4").text
    place = profInfo.find_all("div", {"class": "profile__info-section"})[0].find("p").text
    return {'Name': profInfo, 'Email': email, 'Social': vk, 'Rank': rank, 'Place': place}

opts = Options()
opts.headless = True
for i in range(1, 3):
    #38570
    browser = Firefox(options=opts)
    browser.get("https://leader-id.ru/users/?page={0}".format(i))
    element = browser.find_element_by_id("users-list").get_attribute("outerHTML")
    browser.close()
    findAllPersons(element)
