'''
build test
'''

import logging

from django.test import TestCase

import main

class TestSubjectConsumer(TestCase):
    fixtures = ['auth_user.json', 'main.json']

    user = None

    def setUp(self):
        logger = logging.getLogger(__name__)
    
    def test_move_goods(self):
        '''
        '''
        session = main.models.Session.objects.first()
        session.start_experiment()