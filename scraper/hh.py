
import requests
from bs4 import BeautifulSoup
import json
from us_agent import choice_useragent
from scraper.models import City, Vacancy, Language

def get_html(url, header):
    errors_request = []
    if url:
        response = requests.get(url, headers=header)
        print(response.status_code)
        if response.status_code == 200:
            html = response.text
            return html
        else:
            print("Error")
            errors_request.append({"url": url, "error_name": "Page do not response"})

def get_hh(html, city = None, language = None):
    soup = BeautifulSoup(html, "lxml")

    vacances = soup.find("div", class_="vacancy-serp").find_all("div", class_="vacancy-serp-item")

    # print(soup)
    print(len(vacances))
    data_vacance = []
    errors = []
    if vacances:
        for vacance in vacances:
            try:
                url = vacance.find("div", class_="vacancy-serp-item__info").find("a")["href"]
            except:
                url = "not finded"
            try:
                title = vacance.find("div", class_="vacancy-serp-item__info").find("a").text
            except:
                title = "not finded"
            try:
                company = vacance.find("div", class_="vacancy-serp-item__meta-info").find("a").text
            except:
                company = "not finded"
            try:
                description = vacance.find("div", class_="g-user-content").text
            except:
                description = "not finded"
            data = {"url": url, "title": title, "company": company,
                    "description": description, 'city_id': city, 'language_id': language}

            data_vacance.append(data)
    else:
        errors.append({"url": "https://hh.ru", "error_name": "Div do not exists"})

    return data_vacance, errors

    # print(url)
    # print(title)
    # print(company)
    # print(description)


def get_jooble(html, city = None, language = None):
    soup = BeautifulSoup(html, "lxml")
    #try:
    vacances = soup.find("div", id="main_cont").find_all("div", class_="result saved paddings")
    #except:
       # print("Error")
    # print(soup)
    print(len(vacances))
    data_vacance = []
    errors =[]
    if vacances:
        for vacance in vacances:
            try:
                url = vacance.find("div", class_="left-static-block").find("a")["href"]
            except:
                url = "not finded"
            try:
                title = vacance.find("div", class_="left-static-block").find("a").text
            except:
                title = "not finded"
            try:
                company = vacance.find("div", class_="left-static-block").find("span", class_="gray_text company-name").text
            except:
                company = "not finded"
            try:
                description = vacance.find("div", class_="left-static-block").find("div", class_="desc").text
            except:
                description = "not finded"
            data = {"url": url, "title": title, "company": company, "description": description,
                    'city_id': city, 'language_id': language}

            data_vacance.append(data)
            #print(url)
            #print(title)
            #print(company)
            #print(description)
    else:
        errors.append({"url":"https://ru.jooble.org", "error_name": "Div do not exists"})

    return data_vacance, errors


def get_indeed(html, city = None, language = None):
    soup = BeautifulSoup(html, "lxml")

    table = soup.find("table", attrs={"id" : "pageContent"}).find("td", attrs={"id":"resultsCol"})
    vacances = table.find_all("div", class_ = "jobsearch-SerpJobCard unifiedRow row result")
    #print(table)
    print(len(vacances))
    data_vacance = []
    errors = []
    if not table:
        errors.append({"url":"https://ru.indeed.com", "title": "not find table"})
        return errors
    if vacances:
        for vacance in vacances:
            try:
                url = "https://ru.indeed.com" + vacance.find("a")["href"]
            except:
                url = "not finded"
            try:
                title = vacance.find("a").text
            except:
                title = "not finded"
            try:
                company = vacance.find("span", class_="company").text
            except:
                company = "not finded"
            try:
                description = vacance.find("div", class_="summary").text
            except:
                description = "not finded"
            data = {"url": url, "title": title, "company": company, "description": description,
                    'city_id': city, 'language_id': language}

            data_vacance.append(data)
            #print(url)
            #print(title)
            #print(company)
            #print(description)
    else:
        errors.append({"url":"https://ru.indeed.com", "error_name": "Div do not exists"})

    return data_vacance, errors






def main():
    user_ag = choice_useragent()
    try:
        header = {"User-Agent": user_ag}
    except:
        header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3"}
    print(header)
    url_jooble = "https://ru.jooble.org/%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%B0-python/%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0?date=0"
    url_hh = "https://hh.ru/search/vacancy?search_period=1&clusters=true&area=1&text=Python+moscow&enable_snippets=true"
    #html = get_html(url_hh, header)
    url_indeed = "https://ru.indeed.com/jobs?q=python&l=%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0&sort=date"
    #html_jooble = get_html(url_jooble, header)
    html_indeed = get_html(url_indeed, header)
    vacances_indeed = get_indeed(html_indeed)
    #print(vacances_indeed)
    #vacances_jooble = get_jooble(html_jooble)
    #vacances = get_hh(html)
    #print(vacances_jooble)
 #   with open("vacance_jooble.json", "w", encoding="utf8") as f:
  #      json.dump(vacances_jooble, f)
    with open("../../vac_indeed.txt", "w", encoding ="utf8") as f:
        f.write("{}".format(vacances_indeed))
    #return vacances_jooble


if __name__ == '__main__':
    main()
