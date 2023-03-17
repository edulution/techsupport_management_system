from django.contrib import admin
from allauth.account.adapter import get_adapter
from allauth.account.admin import EmailAddressAdmin
from allauth.account.models import EmailAddress
from allauth.socialaccount.admin import SocialAccountAdmin
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
