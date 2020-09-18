activate_this = 'home/ubuntu/gunviolence_env/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
 
#flaskapp.wsgi
import sys
sys.path.insert(0, '/var/www/html/GunViolenceStats')
 
from app import app as application

