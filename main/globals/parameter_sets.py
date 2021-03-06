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
    ONE = 'One', _('One')
    TWO = 'Two', _('Two')
    THREE = 'Three', _('Three')
    FOUR = 'Four', _('Four')

class AvatarModes(models.TextChoices):
    '''
    avatar asignment modes
    '''
    NONE = 'None', _('None')
    PRE_ASSIGNED = 'Pre-Assigned', _('Pre-Assigned')
    SUBJECT_SELECT = 'Subject Select', _('Subject Select')
    BEST_MATCH = 'Best Match', _('Best Match')
