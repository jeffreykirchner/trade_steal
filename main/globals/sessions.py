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

class ChatTypes(models.TextChoices):
    '''
    chat types
    '''
    ALL = 'All', _('All')
    INDIVIDUAL = 'Individual', _('Individual')

class PeriodPhase(models.TextChoices):
    '''
    period phases
    '''
    PRODUCTION = 'Production', _('Production')
    TRADE = 'Trade', _('Trade')

class ExperimentPhase(models.TextChoices):
    '''
    avatar asignment modes
    '''
    SELECTION = 'Selection', _('Selection')
    INSTRUCTIONS = 'Instructions', _('Instructions')
    RUN = 'Run', _('Run')
    DONE = 'Done', _('Done')
