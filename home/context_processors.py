from home.form import EmailSendingForm
from django.core.mail import send_mail



def email_form_context(request):
    # email_form = EmailSendingForm(request.POST or None)
    #
    # if request.method == 'POST' and email_form.is_valid():
    #     email = email_form.save(commit=False)
    #     if not request.user.is_anonymous:
    #         email.user = request.user
    #     email.save()
    #     send_mail(
    #         subject='That’s your subject',
    #         message = 'That’s your message body',
    #         from_email = 'octinaweb@gmail.com',
    #         recipient_list = [f'{email.email}'],
    #         fail_silently = False,
    #     )
    # else:
    #     if request.user.is_authenticated and request.user.email:
    #         initial_data = {'email': request.user.email}
    #         email_form = EmailSendingForm(request.POST or None, initial=initial_data)
    #
    # context = {'email_form': email_form}
    context = {}
    return context

