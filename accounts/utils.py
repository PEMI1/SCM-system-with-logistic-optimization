#this file contains helper functions
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


#function to detect user role and passing their respective url
def detectUser(user):
    if user.role == 1:
        redirecturl = 'vendorDashboard'
        return redirecturl
    elif user.role ==2 :
        redirecturl = 'custDashboard'
        return redirecturl
    elif user.role == None and user.is_superadmin:
        redirecturl = '/admin'
        return redirecturl


#encode user's pk, generate token using the user, then send email using email template and when user clicks activation link set the user's is_active=true 
def send_verification_email(request, user, mail_subject, email_template):
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    # mail_subject = 'Please activate your account'
    #message = render_to_string('accounts/emails/account_verification_email.html',{
    message = render_to_string(email_template,{
        'user': user,
        'domain':current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token' : default_token_generator.make_token(user),
    }) 
    to_email = user.email
    mail = EmailMessage(mail_subject, message,from_email, to=[to_email])
    mail.send()
    
    


# def send_password_reset_email(request, user):
#     from_email = settings.DEFAULT_FROM_EMAIL
#     current_site = get_current_site(request)
#     mail_subject = 'Reset Your Password'
#     message = render_to_string('accounts/emails/reset_password_email.html',{
#         'user': user,
#         'domain':current_site,
#         'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#         'token' : default_token_generator.make_token(user),
#     }) 
#     to_email = user.email
#     mail = EmailMessage(mail_subject, message,from_email, to=[to_email])
#     mail.send()
    


#approval notification for vendor
def send_notification(mail_subject, mail_template, context):
    from_email= settings.DEFAULT_FROM_EMAIL
    message = render_to_string(mail_template, context)
    to_email = context['user'].email  # we are accessing the user from the context
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    mail.send()
