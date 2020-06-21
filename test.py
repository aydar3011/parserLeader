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
    browser1.quit()
    return tmp


def findAllPersons(text):
    home = "https://leader-id.ru"
    soup = BeautifulSoup(text)
    row = soup.find("div", {"class": "row"})
    persons = row.find_all("div", {"class": "col-sm-5"})
    for person in persons:
        hrefA = person.find("a", {"class": "participant__photo"}).get("href")
        elementUser = openBrowser(home + hrefA)
        leaderInfo = parsPerson(elementUser)
        if leaderInfo == -1:
            print('did not find contacts')
        elif leaderInfo == -2:
            print('did not find tags and career info')
        else:
            with open("people.csv", "a", encoding="utf-8") as f:
                writer = csv.DictWriter(f, delimiter=';', fieldnames=fieldnames)
                writer.writerow(leaderInfo)



def parsPerson(text):
    soup = BeautifulSoup(text)
    name = soup.find("h2", {"class": "profile__name"}).text
    print('entered the page of ' + name)
    userId = soup.find("div", {"class": "profile__id"}).text
    wrapperContent = soup.find("div", {"class": "wrapper__content"})
    profileContent = wrapperContent.find("div", {"class": "section--white"}).find("div", {"class": "profile__content"})
    profInfo = profileContent.find("div", {"class": "profile__info"})
    vk = fb = email = workorganization = innovationsineconomy = informationexchange = projectmanagement = restcomp = allcompetencies = ''
    try:
        socials = profInfo.find_all("div", {"class": "profile__info-section"})[1]
        contactsfrommb2 = socials.find_all("p", {"class": "mb-2"})
        # массив информации полученной из блока mb-2 где перемешанные контакты и адрес
        print('contactsfrommb2')
        for l in contactsfrommb2:
            l = l.text
            if l.find('@') != -1:
                email = l
                print('found email ' + email + ' ' + l)
            elif l.find('vk.com') != -1:
                vk = l
                print('found vk ' + vk + ' ' + l)
            elif l.find('г.') != -1:
                place = l
                print('found place ' + place + ' ' + l)
        atags = socials.find_all("a")
        # находим всё с тегами а
        print('atags')
        for m in atags:
            m = m.get("href") if m.get("href") else ''
            if m.find('vk.com') != -1:
                vk = m
                print('found vk ' + vk + ' ' + l)
            elif m.find('facebook.com') != -1:
                fb = m
                print('found fb ' + fb + ' ' + l)
    except:
        try:
            vk = socials.find("a", {"class": "socials__item--vk"}).get("href").text
            print('found vk ' + vk)
        except:
            try:
                fb = socials.find("a", {"class": "socials__item--fb"}).get("href").text
                print('found fb ' + fb)
            except:
                return -1
    if not vk:
        if not fb:
            if not email:
                return -1
    try:
        competencies = profInfo.find_all("div", {"class": "profile__section"})[3].find("div", {"id": "yw0"})
        workorganization = competencies.find("tspan", {"dy": "3.50406715380043"}).text
        innovationsineconomy = competencies.find("tspan", {"dy": "3.4970423910003205"}).text
        informationexchange = competencies.find("tspan", {"dy": "3.5040671538004347"}).text
        projectmanagement = competencies.find("tspan", {"dy": "3.50174877272633"}).text
        restcomp = competencies.find("tspan", {"dy": "3.493813887905276"}).text
        allcompetencies = competencies.find("tspan", {"dy": "24.5"}).text
    except:
        workorganization = innovationsineconomy = informationexchange = projectmanagement = restcomp = allcompetencies = 'no competencies found'
    try:
        tags = profInfo.find_all("div", {"class": "profile__section"})[2].find_all("div",
                                                                                   {"class": "timeline__item-dscr"})
        alltags = ",".join(tags)
    except:
        alltags = ''

    try:
        profession = profInfo.find_all("div", {"class": "profile__info-section"})[0].find("h4").text
        company = profInfo.find_all("div", {"class": "profile__info-section"})[0].find("p").text
        listOfCareer = profileContent.find("div", {"class": "profile__section"}).find_all("li", {
            "class": "timeline__item"})
        career = []
        allCompanies = []
        for data in listOfCareer:
            prof = data.find("h4", {"class": "timeline__item-header"}).text
            companynew = data.find("p", {"class": "timeline__item-dscr"}).find("a").text
            allCompanies.append(companynew)
            career.append(prof)
        careers = ", ".join(np.unique(career))
        companies = ", ".join(np.unique(allCompanies))
    except:
        return -2
    print('this user is acceptable')

    return {'ID': userId,
            'Name': name,
            'Email': email,
            'VK': vk,
            'Facebook': fb,
            'Current Profession': profession,
            'Current company': company,
            'Old professions': careers,
            'Old companies': companies,
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

#parsPerson(openBrowser('https://leader-id.ru/261299/'))
fieldnames = ['ID', 'Name', 'Email', 'VK', 'Facebook', 'Current Profession', 'Current company', 'Old professions',
            'Old companies', 'Place', 'Work organization competency', 'Innovation in economics', 'Information exchange and communication',
              'Project management', 'Rest competencies', 'All competencies', 'Tags', 'Age']

with open("people.csv", "w", encoding='utf-8') as f:
    writer = csv.DictWriter(f, delimiter=';', fieldnames=fieldnames)
    writer.writeheader()

for i in range(20, 31):  # перебираем возраст пользователей
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
            for k in range(1, currentpage + 1):
                browser = Firefox(options=opts)
                browser.get("https://leader-id.ru/users/?age={0}-{0}&page={1}".format(i, k))
                element = browser.find_element_by_id("users-list").get_attribute("outerHTML")
                browser.quit()
                findAllPersons(element)
        except:
            findAllPersons(element)


