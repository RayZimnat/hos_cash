from django import template
from num2words import num2words

from django.contrib.auth.models import Group
from system.models import Dependant
from system.views import calculate_premium

register = template.Library()

@register.filter
def to_words(number):
    return num2words(number)

@register.filter
def daily_payout(dependant_id):
    dependant = Dependant.objects.get(id=dependant_id)

    if calculate_premium(dependant)['minor']:
        daily_payout = dependant.plan.minor_payout
    else:
        daily_payout = dependant.plan.adult_payout

    return daily_payout

@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return group in user.groups.all()
