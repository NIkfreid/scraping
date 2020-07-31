import os
import sys

import asyncio
import datetime as dt
proj = os.path.dirname(os.path.abspath("manage.py"))
sys.path.append(os.path.dirname(os.path.abspath("manage.py")))
print(proj)
os.environ["DJANGO_SETTINGS_MODULE"] = "scraping.settings"
import django

django.setup()
from django.contrib.auth import get_user_model
from django.db import DatabaseError

from us_agent import choice_useragent

from scraper.models import Vacancy,  Error, Url
from scraper.hh import get_html, get_indeed, get_jooble, get_hh


def head():
    user_ag = choice_useragent()
    try:
        header = {"User-Agent": user_ag}
    except:
        header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3"}
    return header


def hh(url, city=None, language=None):
    header = head()
    #url = "https://hh.ru/search/vacancy?search_period=1&clusters=true&area=1&text={0}+{1}&enable_snippets=true".format(
        #ci, la)
    html = get_html(url, header)
    vacances_hh, errors_hh = get_hh(html, city, language)
    print(url)
    return vacances_hh, errors_hh


def jooble(url, city=None, language=None):
    header = head()
    #url = "https://ru.jooble.org/%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%B0-{1}/{0}?date=0".format(la, ci)
    html = get_html(url, header)
    vacances_jooble, errors_jooble = get_jooble(html, city, language)
    print(url)
    return vacances_jooble, errors_jooble


def indeed(url, city=None, language=None):
    header = head()
    #url = "https://ru.indeed.com/jobs?q={1}&l={0}&sort=date".format(la, ci)
    html = get_html(url, header)
    vacances_indeed, errors_indeed = get_indeed(html, city, language)
    print(url)
    return vacances_indeed, errors_indeed


User = get_user_model()

parsers = ((hh, "hh"), (jooble, "jooble"), (indeed, "indeed"))


def get_setngs():
    qs = User.objects.filter(send_email=True).values()
    setngs = set((q["city_id"], q["language_id"]) for q in qs)
    return setngs


def get_urls(setngs):
    qs = Url.objects.all().values()
    url_dict = {(q["city_id"], q["language_id"]): q["url_data"] for q in qs}
    urls = []
    for pair in setngs:
        if pair in url_dict:
            #print(pair)
            tmp = {}
            try:
                tmp["city"] = pair[0]
                tmp["language"] = pair[1]
                tmp["url_data"] = url_dict[pair]
                urls.append(tmp)
            except:
                continue

    #print(urls)
    return urls


vacs, errors = [], []

#settings = get_details()
#ci, la = get_list_urls(settings)

settings = get_setngs()
urls = get_urls(settings)

async def main(value):
    func, url, city, language = value
    vac, err = await loop.run_in_executor(None, func, url, city, language)
    errors.extend(err)
    vacs.extend(vac)


import time

start = time.time()
loop = asyncio.get_event_loop()
tmp_tasks = [(func, data['url_data'][key], data['city'], data['language'])
             for data in urls
             for func, key in parsers]

tasks = asyncio.wait([loop.create_task(main(f)) for f in tmp_tasks])
loop.run_until_complete(tasks)
loop.close()

#for data in urls:
#    for func, key in parsers:
#        url = data["url_data"]
#        v, e = func(url, city=data['city'], language=data['language'])
#        vacs += v
#        errors += e





#vacs, errors = work(settings)
print(time.time() - start)
for vacancy in vacs:
    v = Vacancy(**vacancy)
    print(vacancy)
    try:
        v.save()
    except DatabaseError:
        pass

if errors:
    qs = Error.objects.filter(timestamp=dt.date.today())
    if qs.exists:
        err = qs.first()
        err.data.update({'errors': errors})
        err.save()
    else:
        er = Error(data=f'errors: {errors}').save()
print(time.time() - start)
# city = City.objects.filter(slug="moscow").first()
# language = Language.objects.filter(slug="python").first()
# vacs_hh, er_hh = hh()
# vacs_jooble, er_job = jooble()
# vacs_indeed, er_ind = indeed()
# vacs = vacs_hh + vacs_jooble + vacs_indeed
# errs = er_hh + er_job + er_ind


# print(vacs)
# print(errs)
# print(er_hh)
# with open("../vacs_hh.txt", "w", encoding="utf8") as f:
#    f.write("{}".format(vacs_hh))

# print(er_job)
# with open("../vacs_jooble.txt", "w", encoding="utf8") as f:
#    f.write("{}".format(vacs_jooble))

# print(er_ind)
# with open("../vacs_indeed.txt", "w", encoding="utf8") as f:
#   f.write("{}".format(vacs_indeed))

#   with open("vacance_jooble.json", "w", encoding="utf8") as f:
#      json.dump(vacances_jooble, f)

# return vacances_jooble
def get_details():
    qs = User.objects.filter(send_email=True).values_list('language', 'city')
    details = set((q[0], q[1]) for q in qs)
    return details


def get_list_urls(details):
    urls = []

    for pair in details:
        ci = City.objects.get(id=pair[1])
        la = Language.objects.get(id=pair[0])

        # for url in urls_lst:
        # tmp = {}
        # tmp["city"] = pair[1]
        # tmp["language"] = pair[0]
        # tmp["url_data"] = url.format(ci, la)
        # urls.append(tmp)
    # print(urls)
    return ci, la


urls_lst = ["https://ru.indeed.com/jobs?q={1}&l={0}&sort=date",
            "https://ru.jooble.org/%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%B0-{1}/{0}?date=0",
            "https://hh.ru/search/vacancy?search_period=1&clusters=true&area=1&text={0}+{1}&enable_snippets=true"]


def work(settings):
    vacs, errors = [], []
    for pair in settings:
        ci = City.objects.get(id=pair[1])
        la = Language.objects.get(id=pair[0])
        # vacs_jooble, er_job = jooble(city = pair[1], language = pair[0], la, ci)
        vacs_indeed, er_ind = indeed(la, ci, city=pair[1], language=pair[0])
        vacs_hh, er_hh = hh(ci, la, city=pair[1], language=pair[0])

        vacs = vacs_hh + vacs_indeed
        errs = er_hh + er_ind
    return vacs, errs