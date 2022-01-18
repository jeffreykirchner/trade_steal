'''
build test
'''
from copy import deepcopy
from decimal import  Decimal

import logging

from django.test import TestCase

from main.globals import  PeriodPhase
from main.globals import ExperimentPhase

from main.consumers import take_move_goods

import main

class TestSubjectConsumer(TestCase):
    fixtures = ['auth_user.json', 'main.json']

    user = None

    def setUp(self):
        logger = logging.getLogger(__name__)
    
    def test_move_goods(self):
        '''
        '''

        logger = logging.getLogger(__name__)

        session = main.models.Session.objects.first()
        session_player_1 = session.session_players.all()[0]
        session_player_2 = session.session_players.all()[1]


        v = {}
        v["sourceType"] = "field"
        v["sourceID"] =  session_player_1.id

        v["targetType"] = "house"
        v["targetID"] =  session_player_1.id

        v["formData"] = [{'name': 'transfer_good_one_amount_2g', 'value': '1'}, 
                         {'name': 'transfer_good_two_amount_2g', 'value': '2'}]

        #check session started
        result = take_move_goods(session.id, session_player_1.id, v)
        self.assertEqual("fail", result["value"])
        self.assertEqual("Session has not started.", result["errors"]["transfer_good_one_amount_2g"][0])

        session.start_experiment()

        session_player_1.good_one_field = Decimal('100')
        session_player_1.good_two_field =  Decimal('100')
        session_player_1.save()

        #check session is running
        result = take_move_goods(session.id, session_player_1.id, v)
        self.assertEqual("fail", result["value"])
        self.assertEqual("Session is not running.", result["errors"]["transfer_good_one_amount_2g"][0])

        session.current_experiment_phase = ExperimentPhase.RUN
        session.save()

        #check production phase    
        result = take_move_goods(session.id, session_player_1.id, v)
        self.assertEqual("fail", result["value"])
        self.assertEqual("No transfers during production phase.", result["errors"]["transfer_good_one_amount_2g"][0])

        session.current_period_phase = PeriodPhase.TRADE
        session.save()

        #check transfer works
        result = take_move_goods(session.id, session_player_1.id, v)
        self.assertEqual("success", result["value"])
        session_player_1 = session.session_players.all()[0]
        self.assertEqual(Decimal('99'), session_player_1.good_one_field)
        self.assertEqual(Decimal('98'), session_player_1.good_two_field)
        self.assertEqual(Decimal('1'), session_player_1.good_one_house)
        self.assertEqual(Decimal('2'), session_player_1.good_two_house)

        #check transfer to fields
        v1 = deepcopy(v)
        v1["targetType"] = "field"
        result = take_move_goods(session.id, session_player_1.id, v1)
        self.assertEqual("fail", result["value"])
        self.assertEqual("No transfers to fields.", result["errors"]["transfer_good_one_amount_2g"][0])

        #check stealing not allowed
        v1 = deepcopy(v)
        v1["sourceID"] = session_player_2.id
        result = take_move_goods(session.id, session_player_1.id, v1)
        self.assertEqual("fail", result["value"])
        self.assertEqual("Invalid source.", result["errors"]["transfer_good_one_amount_2g"][0])

        #check stealing allowed
        session.parameter_set.allow_stealing = True
        session.parameter_set.save()

        session_player_2 = session.session_players.all()[1]
        self.assertEqual(Decimal('0'), session_player_2.good_one_house)
        self.assertEqual(Decimal('0'), session_player_2.good_two_house)

        v1 = deepcopy(v)
        v1["targetID"] = session_player_2.id
        result = take_move_goods(session.id, session_player_2.id, v1)
        self.assertEqual("success", result["value"])
        session_player_1 = session.session_players.all()[0]
        session_player_2 = session.session_players.all()[1]
        self.assertEqual(Decimal('98'), session_player_1.good_one_field)
        self.assertEqual(Decimal('96'), session_player_1.good_two_field)
        self.assertEqual(Decimal('1'), session_player_2.good_one_house)
        self.assertEqual(Decimal('2'), session_player_2.good_two_house)

        session.parameter_set.allow_stealing = True
        session.parameter_set.save()

        #check move between houses
        v1 = deepcopy(v)
        v1["sourceID"] = session_player_1.id
        v1["targetID"] = session_player_2.id
        v1["sourceType"] = "house"
        v1["targetType"] = "house"
        result = take_move_goods(session.id, session_player_1.id, v1)
        self.assertEqual("success", result["value"])
        session_player_1 = session.session_players.all()[0]
        session_player_2 = session.session_players.all()[1]
        self.assertEqual(Decimal('0'), session_player_1.good_one_house)
        self.assertEqual(Decimal('0'), session_player_1.good_two_house)
        self.assertEqual(Decimal('2'), session_player_2.good_one_house)
        self.assertEqual(Decimal('4'), session_player_2.good_two_house)

        #check not enough good one on field
        v1 = deepcopy(v)
        v1["formData"][0]["value"] = 99
        result = take_move_goods(session.id, session_player_1.id, v1)
        self.assertEqual("fail", result["value"])
        self.assertEqual(f"Field does not have enough {session_player_1.parameter_set_player.good_one.label}.", result["errors"]["transfer_good_one_amount_2g"][0])

        #check not enough good two on field
        v1 = deepcopy(v)
        v1["formData"][1]["value"] = 99
        result = take_move_goods(session.id, session_player_1.id, v1)
        self.assertEqual("fail", result["value"])
        self.assertEqual(f"Field does not have enough {session_player_1.parameter_set_player.good_two.label}.", result["errors"]["transfer_good_two_amount_2g"][0])

        #check not enough good one on field
        v1 = deepcopy(v)
        v1["sourceID"] = session_player_2.id
        v1["targetID"] = session_player_1.id
        v1["sourceType"] = "house"
        v1["targetType"] = "house"
        v1["formData"][0]["value"] = 99
        result = take_move_goods(session.id, session_player_2.id, v1)
        self.assertEqual("fail", result["value"])
        self.assertEqual(f"House does not have enough {session_player_1.parameter_set_player.good_one.label}.", result["errors"]["transfer_good_one_amount_2g"][0])

        #check not enough good one on field
        v1 = deepcopy(v)
        v1["sourceID"] = session_player_2.id
        v1["targetID"] = session_player_1.id
        v1["sourceType"] = "house"
        v1["targetType"] = "house"
        v1["formData"][1]["value"] = 99
        result = take_move_goods(session.id, session_player_2.id, v1)
        self.assertEqual("fail", result["value"])
        self.assertEqual(f"House does not have enough {session_player_1.parameter_set_player.good_two.label}.", result["errors"]["transfer_good_two_amount_2g"][0])

        #check junk
        result = take_move_goods(session.id, session_player_2.id, {})
        self.assertEqual("fail", result["value"])
        self.assertEqual(f"Move failed.", result["errors"]["transfer_good_one_amount_2g"][0])

