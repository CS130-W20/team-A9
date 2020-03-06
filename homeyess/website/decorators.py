"""
homeyess/website/decorators.py
"""
from .models import Profile

def is_user_type(user, user_type):
    """checks whether the user is of the type user_type

    :param user: the user to check
    :type user: User
    :param user_type: the type of user ('V', 'H', 'C')
    :type user_type: string
    :return: whether the user is of the type user_type
    :rtype: boolean
    """
    if not user.is_authenticated:
        return False
    profile = Profile.objects.get(user=user)
    if profile.user_type == user_type:
        return True
    return False

def is_homeless(user):
    """checks whether the user is a homeless user

    :param user: the user to check
    :type user: User
    :return: whether the user is a homeless user
    :rtype: boolean
    """
    return is_user_type(user, 'H')

def is_company(user):
    """checks whether the user is a company

    :param user: the user to check
    :type user: User
    :return: whether the user is a company
    :rtype: boolean
    """
    return is_user_type(user, 'C')

def is_volunteer(user):
    """checks whether the user is a volunteer

    :param user: the user to check
    :type user: User
    :return: whether the user is a volunteer
    :rtype: boolean
    """
    return is_user_type(user, 'V')
