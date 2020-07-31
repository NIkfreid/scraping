import os
import sys
import django
import datetime

proj = os.path.dirname(os.path.abspath("manage.py"))
sys.path.append(os.path.dirname(os.path.abspath("manage.py")))
print(proj)
os.environ["DJANGO_SETTINGS_MODULE"] = "scraping.settings"

django.setup()
from django.contrib.auth import get_user_model
# from django.db import DatabaseError
from django.core.mail import EmailMultiAlternatives
from scraper.models import Vacancy, Error, Url, City, Language
from scraping.settings import EMAIL_HOST_USER

from django.utils import timezone
import pytz
timezone.now()


today = datetime.date.today()
empty = "<h3>Sorry, today vacancies not find</h3>"
subject = f"Рассылка вакансий на {today}"
text_content = "Рассылка вакансий"
from_email = EMAIL_HOST_USER

User = get_user_model()
qs = User.objects.filter(send_email=True).values("city", "language", "email")
users_dict = {}
for i in qs:
    users_dict.setdefault((i['city'], i['language']), [])
    users_dict[(i['city'], i['language'])].append(i['email'])

if users_dict:
    params = {'city_id__in': [], 'language_id__in': []}
    for pair in users_dict.keys():
        params['city_id__in'].append(pair[0])
        params['language_id__in'].append(pair[1])
    qs = Vacancy.objects.filter(**params).values()
    vacancies = {}
    for i in qs:
        vacancies.setdefault((i['city_id'], i['language_id']), [])
        vacancies[(i['city_id'], i['language_id'])].append(i)
    for keys, emails in users_dict.items():
        rows = vacancies.get(keys, [])[:10]
        html = ""
        for row in rows:
            html += f'<h4><a href="{row["url"]}">{row["title"]}</a></h4>'
            html += f'<p>{row["description"]}</p>'
            html += f'<p>{row["company"]}</p><br><hr>'
        _html = html if html else empty
        for email in emails:
            to = email
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html, "text/html")
            msg.send()

qs = Error.objects.filter()
subject = ''
text_content = ''
to = "niknn_85@mail.ru"
_html = ""
if qs.exists():
    error = qs.first()
    data = error.data.get('errors', [])
    print(data)
    for i in data:
        _html += f'<p><a href="{i["url"]}">{i["error_name"]}</a></p>'
    subject = "error_test"
    text_content = ""
    data = error.data.get('user_data', [])
    if data:
        _html += '<hr>'
        for i in data:
            _html += f'<p>City: {i["city"]}, Language: {i["language"]}</p>'
        subject = "Заявки"
        text_content = "Заявки пользователей"


qs = Url.objects.all().values("city", "language")
urls_dict = {(i['city'], i['language']): True for i in qs}
urls_msg = ''
for keys in users_dict.keys():
    if keys not in urls_dict:
         urls_msg = f'<p>Для города -{keys[0]} и яп - {keys[1]} нет урлов</p>'
if urls_msg:
    subject += " Not find urls"
    _html += urls_msg


if subject:
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(_html, "text/html")
    msg.send()