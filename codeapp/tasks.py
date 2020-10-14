from time import sleep
from celery import shared_task
import requests
import datetime
from .models import Contests
import logging,traceback
logger = logging.getLogger('django')
from django.db.models import Max

@shared_task
def createDBInitial():
    logger.info('Appending initial data in Contest DB...')

    dateNow = datetime.datetime.now()
    format_iso_now = dateNow.isoformat()
    formatedDate = (str(format_iso_now).split('.'))[0]

    ninetyDaysFromNow = later = dateNow + datetime.timedelta(days=90)
    format_later_iso = ninetyDaysFromNow.isoformat()
    formattedNinetyDays = (str(format_later_iso).split('.'))[0]

    extraQueries = '?start__gte='+formatedDate+'&end__lte='+formattedNinetyDays+'&order_by=start'
    url = 'https://clist.by/api/v1/json/contest/'+extraQueries
    response = requests.get(url,headers={"Authorization": "ApiKey yasharma:b5113e149225b28fea57608b9c41005e5b34c939"})

    contestProviderList = {'codingcompetitions.withgoogle.com','atcoder.jp','codechef.com','kaggle.com',
    'topcoder.com','codeforces.com','hackerearth.com','ctftime.org','leetcode.com','codeforces.com/gyms','hackerrank.com'}
    try:
        for i in response.json()['objects']:
            duration = i['duration']
            end = datetime.datetime.strptime(i['end'].split('T')[0]+' '+i['end'].split('T')[1], '%Y-%m-%d %H:%M:%S')
            event = i['event']
            href = i['href']
            icon = i['resource']['icon']
            name = i['resource']['name']
            start = datetime.datetime.strptime(i['start'].split('T')[0]+' '+i['start'].split('T')[1], '%Y-%m-%d %H:%M:%S')
            
            if name in contestProviderList:
                try:
                    Contests.objects.create(
                    duration = duration,
                    end = end,
                    event = event,
                    href = href,
                    icon = icon,
                    name = name,
                    start = start
                    )
                except Exception as e:
                    logger.exception(e)
                sleep(1)
    except Exception as e:
        logger.info(e)
    logger.info('Initial data append success!')

@shared_task
def updateDBWithNewData():
    logger.info('Deleting previous waste data...')
    Contests.objects.filter(start__lt=datetime.datetime.now()).delete()
    sleep(1)

    logger.info('Now updating the data with new data in next 12 hours span...')
    
    # Ignore
    # Get the largest start value
    # max_date_time = Contests.objects.latest('start')
    # max_date_time = Contests.objects.aggregate(Max('start'))['start__max']
    # logger.info(max_date_time)
    # format_iso_now = max_date_time.isoformat()
    # formatedDate = ((str(format_iso_now).split('.'))[0]).split('+')[0]
    # logger.info('x')
    # logger.info(formatedDate)

    dateNow = datetime.datetime.now() + datetime.timedelta(days=90)
    format_iso_now = dateNow.isoformat()
    formatedDate = (str(format_iso_now).split('.'))[0]
    logger.info(formatedDate)

    oneDayFromNow = dateNow + datetime.timedelta(days=1)
    format_later_iso = oneDayFromNow.isoformat()
    formattedNinetyDays = (str(format_later_iso).split('.'))[0]
    logger.info(formattedNinetyDays)

    extraQueries = '?start__gte='+formatedDate+'&end__lte='+formattedNinetyDays+'&order_by=start'
    url = 'https://clist.by/api/v1/json/contest/'+extraQueries
    response = requests.get(url,headers={"Authorization": "ApiKey yasharma:b5113e149225b28fea57608b9c41005e5b34c939"})

    contestProviderList = {'codingcompetitions.withgoogle.com','atcoder.jp','codechef.com','kaggle.com',
    'topcoder.com','codeforces.com','hackerearth.com','ctftime.org','leetcode.com','codeforces.com/gyms','hackerrank.com'}
    
    try:
        for i in response.json()['objects']:
            duration = i['duration']
            end = datetime.datetime.strptime(i['end'].split('T')[0]+' '+i['end'].split('T')[1], '%Y-%m-%d %H:%M:%S')
            event = i['event']
            href = i['href']
            icon = i['resource']['icon']
            name = i['resource']['name']
            start = datetime.datetime.strptime(i['start'].split('T')[0]+' '+i['start'].split('T')[1], '%Y-%m-%d %H:%M:%S')
            
            if name in contestProviderList:
                try:
                    Contests.objects.create(
                    duration = duration,
                    end = end,
                    event = event,
                    href = href,
                    icon = icon,
                    name = name,
                    start = start
                    )
                except Exception as e:
                    logger.exception(e)
                sleep(1)
    except:
        logger.info('Key Error. The response doesn\'t contain much objects.')
    logger.info('Updation success!')


if not Contests.objects.all():
    logger.info('Run for the first time to populate DB...')
    createDBInitial()

while True:
    oneDay = 24*60*60
    sleep(oneDay)
    updateDBWithNewData()