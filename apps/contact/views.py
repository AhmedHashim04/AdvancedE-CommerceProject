from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.utils.translation import gettext as _
from .forms import EmailForm


class SendEmailView(FormView):
    form_class = EmailForm
    template_name = "contact/contact.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        from_email = form.cleaned_data["from_email"]
        title = form.cleaned_data["title"]
        message = form.cleaned_data["message"]
        send_mail(title, message, from_email, [settings.DEFAULT_FROM_EMAIL])
        messages.success(
            self.request,
            f"{from_email} "+_("sent message and it's arrived to Organization Successfully"),
        )
        return super().form_valid(form)
