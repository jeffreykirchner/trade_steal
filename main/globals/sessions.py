'''
gloabal functions related to parameter sets
'''

from django.db import models
from django.utils.translation import gettext_lazy as _

import main

class ContainerTypes(models.TextChoices):
    '''
    subject types
    '''
    HOUSE = 'House', _('House')
    FIELD = 'Field', _('Field')