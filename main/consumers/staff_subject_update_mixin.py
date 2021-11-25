
import json
import logging
from asgiref.sync import sync_to_async

from django.core.serializers.json import DjangoJSONEncoder

import main

class StaffSubjectUpdateMixin():

    connection_type = None            #staff or subject
    connection_uuid = None            #uuid of connected object   
    session_id = None                 #id of session

    
