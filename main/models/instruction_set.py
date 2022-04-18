'''
instruction set
'''

#import logging

from django.db import models

import main

class InstructionSet(models.Model):
    '''
    instruction set model
    '''

    label = models.CharField(max_length = 100, default="Name Here", verbose_name="Label")                 #label text

    action_page_production = models.IntegerField(verbose_name='Required Action: Production', default=2)   #production page action
    action_page_move = models.IntegerField(verbose_name='Required Action: Move', default=3)               #move page action
    action_page_chat = models.IntegerField(verbose_name='Required Action: Chat', default=4)               #chat page action

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.label}"

    class Meta:
        
        verbose_name = 'Instruction Set'
        verbose_name_plural = 'Instruction Sets'
        ordering = ['label']
        constraints = [
            models.UniqueConstraint(fields=['label', ], name='unique_instruction_set'),
        ]

    def copy_pages(self, i_set):
        '''
        copy instruction pages
        '''
        
        #session player periods
        instructions = []

        for i in i_set.all():
            instructions.append(main.models.Instruction(instruction_set=self, text_html=i.text_html, page_number=i.page_number))
        
        main.models.Instruction.objects.bulk_create(instructions)
        
    #return json object of class
    def json(self):
        '''
        json object of model
        '''

        return{
            "id" : self.id,         

            "label" : self.label,

            "action_page_production" : self.action_page_production,
            "action_page_move" : self.action_page_move,
            "action_page_chat" : self.action_page_chat,

            "instructions" : [i.json() for i in self.instructions.all()],
        }
    
    #return json object of class
    def json_min(self):
        '''
        json object of model
        '''

        return{
            "id" : self.id,         

            "label" : self.label,
        }
        