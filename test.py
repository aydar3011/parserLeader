import re
import csv
import numpy as np
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup


def openBrowser(url):
    opts = Options()
    opts.headless = True
    browser1 = Firefox(options=opts)
    browser1.get(url)
    tmp = browser1.find_element_by_class_name("wrapper").get_attribute("outerHTML")
    findAllPersons(tmp)
    browser1.quit()
    return tmp


def findAllPersons(text):
    home = "https://leader-id.ru"
    file = open("people.csv", "w", encoding='utf-8')
    fieldnames = ['ID', 'Name', 'Email', 'VK', 'Facebook', 'Profession', 'Company', 'Career', 'Place', 'Work organization competency', 'Innovation in economics', 'Information exchange and communication', 'Project management', 'Rest competencies', 'All competencies', 'Tags', 'Age']
    writer = csv.DictWriter(file, delimiter=';', fieldnames=fieldnames)
    writer.writeheader()
    soup = BeautifulSoup(text)
    row = soup.find("div", {"class": "row"})
    persons = row.find_all("div", {"class": "col-sm-5"})
    for person in persons:
        hrefA = person.find("a", {"class": "participant__photo"}).get("href")
        elementUser = openBrowser(home + hrefA)
        leaderInfo = parsPerson(elementUser)
        if leaderInfo == -1:
            print ('did not find contacts')
        elif leaderInfo == -2:
            print ('did not find tags and career info')
        else:
            writer.writerow(leaderInfo)


def parsPerson(text):
    soup = BeautifulSoup(text)
    name = soup.find("h2", {"class": "profile__name"}).text
    print('entered the page of '+name)
    userId = soup.find("div", {"class": "profile__id"}).text
    wrapperContent = soup.find("div", {"class": "wrapper__content"})
    profileContent = wrapperContent.find("div", {"class": "section--white"}).find("div", {"class": "profile__content"})
    profInfo = profileContent.find("div", {"class": "profile__info"})
    vk = fb = email = workorganization = innovationsineconomy = informationexchange = projectmanagement = restcomp = allcompetencies = 'none'
    try:
        #print('trying to find an email')
        email = profInfo.find_all("div", {"class": "profile__info-section"})[1].find("p").text
        re.search(r'@', email)
        #print('found an email')
    except:
        try:
            print('trying to find a vk')
            socials = profInfo.find_all("div", {"class": "profile__info-section"})[1].find("div", {"class": "socials"})
            vk = socials.find("a", {"class": "socials__item--vk"}).get("href").text
        except:
            try:
                fb = socials.find("a", {"class": "socials__item--fb"}).get("href").text
            except:
                return -1
    try:
        competencies = profInfo.find_all("div", {"class": "profile__section"})[3].find("div", {"id": "yw0"})
        workorganization = competencies.find("tspan", {"dy": "3.50406715380043"})
        innovationsineconomy = competencies.find("tspan", {"dy": "3.4970423910003205"})
        informationexchange = competencies.find("tspan", {"dy": "3.5040671538004347"})
        projectmanagement = competencies.find("tspan", {"dy": "3.50174877272633"})
        restcomp = competencies.find("tspan", {"dy": "3.493813887905276"})
        allcompetencies = competencies.find("tspan", {"dy": "24.5"})
    except:
        workorganization = innovationsineconomy = informationexchange = projectmanagement = restcomp = allcompetencies ='no competencies found'
    try:
        tags = profInfo.find_all("div", {"class": "profile__section"})[2].find_all("div", {"class": "timeline__item-dscr"}).text
        alltags = ",".join(tags)
        profession = profInfo.find_all("div", {"class": "profile__info-section"})[0].find("h4").text
        company = profInfo.find_all("div", {"class": "profile__info-section"})[0].find("p").text
        career = profileContent.find("div", {"class": "profile__section"})[0].find_all("h4", {"class": "timeline__item-dscr"}).find(a).text
        careers = ",".join(np.unique(career))
    except:
        return -2
    try:
        place = profInfo.find_all("div", {"class": "profile__info-section"})[0].find("p").text
    except:
        place = 'no location'


    print('this user is acceptable')
    return {'ID': userId,
            'Name': name,
            'Email': email,
            'VK': vk,
            'Facebook': fb,
            'Profession': profession,
            'Company': company,
            'Career': careers,
            'Place': place,
            'Work organization competency': workorganization,
            'Innovation in economics': innovationsineconomy,
            'Information exchange and communication': informationexchange,
            'Project management': projectmanagement,
            'Rest competencies': restcomp,
            'All competencies': allcompetencies,
            'Tags': alltags,
            'Age': i}


opts = Options()
opts.headless = True

for i in range(0, 25):  #перебираем возраст пользователей
    # 38570 страниц всего
    browser = Firefox(options=opts)
    browser.get("https://leader-id.ru/users/?age={0}-{0}&page=100000".format(i))
    element = browser.find_element_by_id("users-list").get_attribute("outerHTML")
    soup = BeautifulSoup(element)
    browser.quit()
    try:
        existcheck = soup.find("span", {"class": "empty"}).text
    except:
        try:
            currentpage = soup.find("li", {"class": "pagination__item--active"}).find("a").text
            currentpage = int(currentpage)
            for k in range(1, currentpage+1):
                browser = Firefox(options=opts)
                browser.get("https://leader-id.ru/users/?age={0}-{0}&page={1}".format(i, k))
                element = browser.find_element_by_id("users-list").get_attribute("outerHTML")
                browser.quit()
                findAllPersons(element)
        except:
            findAllPersons(element)
