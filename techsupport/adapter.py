from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        return ACCOUNTS_SOCIAL_LOGIN_REDIRECT_URL

    def get_login_form(self, request):
        form = super().get_login_form(request)
        form.fields['login'].widget.attrs.update({'class': 'form-control'})
        form.fields['password'].widget.attrs.update({'class': 'form-control'})
        return form

    def get_login_context_data(self, request, **kwargs):
        context = super().get_login_context_data(request, **kwargs)
        context['site_name'] = 'Edulution Technical Support'
        context['site_url'] = 'https://www.edulution.org'
        context['extra_css'] = 'css/allauth.css'
        return context
