'''
gloabal functions related to parameter sets
'''

from django.db import models
from django.utils.translation import gettext_lazy as _

import main

class SubjectType(models.TextChoices):
    '''
    subject types
    '''
    BLUE = 'Blue', _('Blue')
    RED = 'Red', _('Red')
