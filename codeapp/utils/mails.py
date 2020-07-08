from django.core.mail import send_mail
from ..secret import *

def send(subject, message, to, html = None, from_email = GMAIL_EMAIL) :
    if html is None :
        send_mail(subject, message, from_email, to, fail_silently=False)

    else :
        send_mail(subject, message, from_email, to, fail_silently=False, html_message=html)