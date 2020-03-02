"""
homeyess/website/decorators.py
"""
from .models import Profile

def is_user_type(user, user_type):
    if not user.is_authenticated:
        return False
    profile = Profile.objects.get(user=user)
    if profile.user_type == user_type:
        return True
    return False

def is_homeless(user):
    return is_user_type(user, 'H')

def is_company(user):
    return is_user_type(user, 'C')

def is_volunteer(user):
    return is_user_type(user, 'V')
