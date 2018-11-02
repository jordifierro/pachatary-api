from django.template.loader import get_template
from django.core import mail
from django.conf import settings


class MailerService:

    PUBLIC_EMAIL_CONFIRMATION_PATH = '/redirects/people/me/email-confirmation'
    PUBLIC_LOGIN_EMAIL_PATH = '/redirects/people/me/login'

    def send_ask_confirmation_mail(self, confirmation_token, email, username):
        url = '{}{}?token={}'.format(settings.PUBLIC_DOMAIN,
                                     MailerService.PUBLIC_EMAIL_CONFIRMATION_PATH, confirmation_token)

        context_params = {'username': username, 'confirmation_url': url}
        plain_text_message = get_template('ask_confirmation_email.txt').render(context_params)
        html_message = get_template('ask_confirmation_email.html').render(context_params)

        subject, origin_email, target_email = 'Pachatary account confirmation', settings.EMAIL_HOST_ORIGIN, email

        mail.send_mail(subject,
                       plain_text_message,
                       origin_email, [target_email, ],
                       html_message=html_message,
                       fail_silently=False)

    def send_login_mail(self, login_token, email, username):
        url = '{}{}?token={}'.format(settings.PUBLIC_DOMAIN, MailerService.PUBLIC_LOGIN_EMAIL_PATH, login_token)

        context_params = {'username': username, 'login_url': url}
        plain_text_message = get_template('login_email.txt').render(context_params)
        html_message = get_template('login_email.html').render(context_params)

        subject, origin_email, target_email = 'Pachatary login', settings.EMAIL_HOST_ORIGIN, email

        mail.send_mail(subject,
                       plain_text_message,
                       origin_email, [target_email, ],
                       html_message=html_message,
                       fail_silently=False)
