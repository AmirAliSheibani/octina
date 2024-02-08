from home.form import EmailSendingForm


def email_form_context(request):
    email_form = EmailSendingForm(request.POST or None)

    if request.method == 'POST' and email_form.is_valid():
        email = email_form.save(commit=False)
        if not request.user.is_anonymous:
            email.user = request.user
        email.save()
    else:
        if request.user.is_authenticated and request.user.email:
            initial_data = {'email': request.user.email}
            email_form = EmailSendingForm(request.POST or None, initial=initial_data)

    context = {'email_form': email_form}
    return context