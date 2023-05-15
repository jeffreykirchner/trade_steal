# trade_steal
Web version of the Exchange and Specialization experiment.  https://papers.ssrn.com/sol3/papers.cfm?abstract_id=930078

Setup Guide:
https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04

local_settings.py:
    Copy local_settings_sample.py to local_settings.py
    local_settings.py is used for local development and will be excluded from the repo.
    Update the DATABASES section of this file with the info from your locally run instance of Postgresql.
    Update the CHANNEL_LAYERS layers section of this file with the info from your locally run instance of Redis. 

Update Python installers:
	sudo add-apt-repository ppa:deadsnakes/ppa
	sudo apt update 
	sudo apt install python3.11
	sudo apt-get install python3.11-distutils

Activate virtual environment and install requirments:
    virtualenv --python=python3.11 _trade_steal_env
    source _trade_steal_env/bin/activate
    pip install -U -r requirements.txt

Setup Environment:
sh setup.sh

Run Environment:
python manage.py runserver
