'''
build test
'''
from copy import deepcopy
from decimal import  Decimal

import logging

from django.test import TestCase

from main.globals import PeriodPhase
from main.globals import ExperimentPhase
from main.globals import ChatTypes

from main.consumers import take_move_goods
from main.consumers import take_chat
from main.consumers import take_production_time
from main.consumers import take_name
from main.consumers import take_avatar
from main.consumers import take_avatar
from main.consumers import take_next_instruction
from main.consumers import take_finish_instructions

import main

class TestSubjectConsumer(TestCase):
    fixtures = ['auth_user.json', 'main.json']

    user = None

    def setUp(self):
        logger = logging.getLogger(__name__)
    
    def test_next_instruction(self):
        '''
        take next instruction
        '''

        v_forward = {'direction': 1}
        v_back = {'direction': -1}

        session = main.models.Session.objects.first()
        session_player_1 = session.session_players.get(player_number=1)

        #go back from page one
        result = take_next_instruction(session.id, session_player_1.id, v_back)
        self.assertEqual("success", result["value"])
        session_player_1 = session.session_players.get(player_number=1)
        self.assertEqual(1, session_player_1.current_instruction)

        #go forward from page one
        result = take_next_instruction(session.id, session_player_1.id, v_forward)
        self.assertEqual("success", result["value"])
        session_player_1 = session.session_players.get(player_number=1)
        self.assertEqual(2, session_player_1.current_instruction)

        #go forward from last pasge
        session_player_1.current_instruction = session.parameter_set.instruction_set.instructions.all().count()
        session_player_1.save()
        result = take_next_instruction(session.id, session_player_1.id, v_forward)
        self.assertEqual("success", result["value"])
        session_player_1 = session.session_players.get(player_number=1)
        self.assertEqual(session.parameter_set.instruction_set.instructions.all().count(), session_player_1.current_instruction)

        #junk
        result = take_next_instruction(session.id, session_player_1.id, {})
        self.assertEqual("fail", result["value"]) 
        self.assertEqual("Instruction Error.", result["message"])   

    def test_finish_instructions(self):
        '''
        test subject finished with instructions
        '''

        v = {}

        session = main.models.Session.objects.first()
        session_player_1 = session.session_players.get(player_number=1)

        result = take_finish_instructions(session.id, session_player_1.id, v)
        self.assertEqual("success", result["value"])
        session_player_1 = session.session_players.get(player_number=1)
        self.assertEqual(True, session_player_1.instructions_finished)
    
    def test_avatar_choice(self):
        '''
        test avatar choice grid
        '''

        logger = logging.getLogger(__name__)
        session = main.models.Session.objects.first()
        session_player_1 = session.session_players.get(player_number=1)
        session_player_2 = session.session_players.get(player_number=2)

        v = {'row': 3, 'col': 5}

        #session not finished
        result = take_avatar(session.id, session_player_1.id, v)
        self.assertEqual("fail", result["value"])
        self.assertEqual("Session not started.", result["message"])

        session.start_experiment()

        session_player_2 = session.session_players.get(player_number=2)
        self.assertEqual(None, session_player_2.avatar)

        #session started
        result = take_avatar(session.id, session_player_1.id, v)
        self.assertEqual("success", result["value"])
        session_player_1 = session.session_players.get(player_number=1)
        self.assertEqual(session_player_1.avatar,
                         session.parameter_set.parameter_set_avatars_a.get(grid_location_row=v['row'], grid_location_col=v['col']).avatar)

        #blank choice
        v1 = deepcopy(v)
        v1['row'] = 2
        result = take_avatar(session.id, session_player_2.id, v1)
        self.assertEqual("fail", result["value"])
        self.assertEqual("Avatar is blank.", result["message"])
        session_player_2 = session.session_players.get(player_number=2)
        self.assertEqual(None, session_player_2.avatar)

        #junk
        result = take_avatar(session.id, session_player_2.id, {})
        self.assertEqual("fail", result["value"])
        self.assertEqual("Avatar choice error.", result["message"])
        session_player_2 = session.session_players.get(player_number=2)
        self.assertEqual(None, session_player_2.avatar)

    def test_name(self):
        '''
        test name and id entrys
        '''

        logger = logging.getLogger(__name__)
        session = main.models.Session.objects.first()
        session_player_1 = session.session_players.get(player_number=1)
        session_player_2 = session.session_players.get(player_number=2)
        session_player_3 = session.session_players.get(player_number=3)

        v = {'formData': [{'name': 'name', 'value': 'joe is the name'}, {'name': 'student_id', 'value': '123456789'}]}
        
        #session not finished
        result = take_name(session.id, session_player_1.id, v)
        self.assertEqual("fail", result["value"])
        self.assertEqual("Session not complete.", result["errors"]["name"][0])
        session_player_1 = session.session_players.get(player_number=1)
        self.assertEqual("", session_player_1.name)

        session.finished = True
        session.save()

        #session finished
        result = take_name(session.id, session_player_1.id, v)
        self.assertEqual("success", result["value"])
        session_player_1 = session.session_players.get(player_number=1)
        self.assertEqual("Joe Is The Name", session_player_1.name)

        #no name
        v1 = deepcopy(v)
        v1["formData"][0]['value'] = ""

        result = take_name(session.id, session_player_2.id, v1)
        self.assertEqual("fail", result["value"])
        self.assertEqual("This field is required.", result["errors"]["name"][0])
        session_player_2 = session.session_players.get(player_number=2)
        self.assertEqual("", session_player_2.name)

        #blank name
        v1 = deepcopy(v)
        v1["formData"][0]['value'] = "  "

        result = take_name(session.id, session_player_2.id, v1)
        self.assertEqual("fail", result["value"])
        self.assertEqual("This field is required.", result["errors"]["name"][0])
        session_player_2 = session.session_players.get(player_number=2)
        self.assertEqual("", session_player_2.name)

        #junk
        result = take_name(session.id, session_player_2.id, {})
        self.assertEqual("fail", result["value"])
        self.assertEqual("Invalid Entry.", result["errors"]["name"][0])
        session_player_2 = session.session_players.get(player_number=2)
        self.assertEqual("", session_player_2.name)
    
    def test_production(self):
        '''
        test production
        '''

        logger = logging.getLogger(__name__)

        session = main.models.Session.objects.first()
        session_player_1 = session.session_players.get(player_number=1)

        session.current_experiment_phase = ExperimentPhase.RUN
        session.save()

        v = {'production_slider_one': 31, 'production_slider_two': 69}

        #try valid values period one during production
        result = take_production_time(session.id, session_player_1.id, v)
        self.assertEqual("success", result["value"])
        
        #no updates during production phase
        session.current_period = 2
        session.save()

        result = take_production_time(session.id, session_player_1.id, v)
        self.assertEqual("fail", result["value"])
        self.assertEqual("Not updates during production.", result["message"])

        #valid values during trade after period 1
        session.current_period_phase = PeriodPhase.TRADE
        session.save()

        result = take_production_time(session.id, session_player_1.id, v)
        self.assertEqual("success", result["value"])

        #values not equal to 100
        v1 = deepcopy(v)
        v1['production_slider_one'] = 33
        result = take_production_time(session.id, session_player_1.id, v1)
        self.assertEqual("fail", result["value"])
        self.assertEqual("Invalid values.", result["message"])

        #values not equal to 100
        v1 = deepcopy(v)
        v1['production_slider_one'] = -100
        v1['production_slider_two'] = 200
        result = take_production_time(session.id, session_player_1.id, v1)
        self.assertEqual("fail", result["value"])
        self.assertEqual("Invalid values.", result["message"])

        #junk
        v1 = deepcopy(v)
        v1['production_slider_one'] = "a"
        v1['production_slider_two'] = 100
        result = take_production_time(session.id, session_player_1.id, v1)
        self.assertEqual("fail", result["value"])
        self.assertEqual("Invalid values.", result["message"])

        v1 = deepcopy(v)
        v1['production_slider_one'] = 50.5
        v1['production_slider_two'] = 49.5
        result = take_production_time(session.id, session_player_1.id, v1)
        self.assertEqual("fail", result["value"])
        self.assertEqual("Invalid values.", result["message"])

    def test_chat(self):
        '''
        test chat
        '''

        logger = logging.getLogger(__name__)

        session = main.models.Session.objects.first()
        session_player_1 = session.session_players.get(player_number=1)
        session_player_2 = session.session_players.get(player_number=2)
        session_player_3 = session.session_players.get(player_number=3)
        session_player_9 = session.session_players.get(player_number=9)

        v_all = {'recipients': 'all', 'text': 'asdf'}
        v_one_to_two = {'recipients': session_player_2.id, 'text': 'zxcvb'}

        #check started
        result = take_chat(session.id, session_player_1.id, v_all)
        self.assertEqual("fail", result["value"])
        self.assertEqual("Session not started.", result["result"]["message"])

        session.start_experiment()

        #check session running
        result = take_chat(session.id, session_player_1.id, v_all)
        self.assertEqual("fail", result["value"])
        self.assertEqual("Session not running.", result["result"]["message"])

        session.current_experiment_phase = ExperimentPhase.RUN
        session.save()

        #check private chat
        result = take_chat(session.id, session_player_1.id, v_one_to_two)
        self.assertEqual("success", result["value"])
        session_player_chat = main.models.SessionPlayerChat.objects.get(id=result["result"]["chat_for_subject"]["id"])
        self.assertEqual(v_one_to_two["text"], session_player_chat.text)
        self.assertEqual(ChatTypes.INDIVIDUAL, session_player_chat.chat_type)
        self.assertEqual(session_player_1.id, session_player_chat.session_player.id)
        self.assertIn(session_player_2, session_player_chat.session_player_recipients.all())
        self.assertNotIn(session_player_3, session_player_chat.session_player_recipients.all())

        session.parameter_set.private_chat = False
        session.parameter_set.save()

        result = take_chat(session.id, session_player_1.id, v_one_to_two)
        self.assertEqual("fail", result["value"])
        self.assertEqual("Private chat not allowed.", result["result"]["message"])

        #check public chat
        session.parameter_set.private_chat = True
        session.parameter_set.save()

        result = take_chat(session.id, session_player_2.id, v_all)
        self.assertEqual("success", result["value"])
        session_player_chat = main.models.SessionPlayerChat.objects.get(id=result["result"]["chat_for_subject"]["id"])
        self.assertEqual(v_all["text"], session_player_chat.text)
        self.assertEqual(ChatTypes.ALL, session_player_chat.chat_type)
        self.assertEqual(session_player_2.id, session_player_chat.session_player.id)
        self.assertIn(session_player_1, session_player_chat.session_player_recipients.all())
        self.assertNotIn(session_player_3, session_player_chat.session_player_recipients.all())

        #advance period and update groups
        session.current_period = 14
        session.save()

        result = take_chat(session.id, session_player_2.id, v_all)
        self.assertEqual("success", result["value"])
        session_player_chat = main.models.SessionPlayerChat.objects.get(id=result["result"]["chat_for_subject"]["id"])
        self.assertEqual(v_all["text"], session_player_chat.text)
        self.assertEqual(ChatTypes.ALL, session_player_chat.chat_type)
        self.assertEqual(session_player_2.id, session_player_chat.session_player.id)
        self.assertIn(session_player_1, session_player_chat.session_player_recipients.all())
        self.assertIn(session_player_3, session_player_chat.session_player_recipients.all())
        self.assertNotIn(session_player_9, session_player_chat.session_player_recipients.all())

        #junk
        result = take_chat(session.id, session_player_2.id, {})
        self.assertEqual("fail", result["value"])
        self.assertEqual("Invalid chat.", result["result"]["message"])

    def test_move_goods(self):
        '''
        test move goods
        '''

        logger = logging.getLogger(__name__)

        session = main.models.Session.objects.first()
        session_player_1 = session.session_players.get(player_number=1)
        session_player_2 = session.session_players.get(player_number=2)

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
        session_player_1 = session.session_players.get(player_number=1)
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
        session_player_1 = session.session_players.get(player_number=1)
        session_player_2 = session.session_players.get(player_number=2)
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
        session_player_1 = session.session_players.get(player_number=1)
        session_player_2 = session.session_players.get(player_number=2)
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

