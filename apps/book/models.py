"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth, T, session
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()

db.define_table(
    'contact',
    Field('first_name'),
    Field('last_name'),
    Field('created_by', 'reference auth_user', default=lambda: auth.user_id),
    Field('user_email',  default=get_user_email),
    Field('creation_date', 'datetime', default=get_time),
)
db.contact.id.readable = db.contact.id.writable = False 
db.contact.user_email.readable = db.contact.user_email.writable = False 
db.contact.created_by.readable = db.contact.created_by.writable = False; 
db.contact.creation_date.readable = db.contact.creation_date.writable = False; 

db.define_table(
    'phone',
    Field('contact_id', 'reference contact'),
    Field('phone_number', default=""),
    Field('purpose', default=""),
    Field('user_email',  default=get_user_email),
    Field('creation_date', 'datetime', default=get_time),
)
db.phone.id.readable = False 
db.phone.contact_id.readable = db.phone.contact_id.writable = False 
db.phone.user_email.readable = db.phone.user_email.writable = False 
db.phone.creation_date.readable = db.phone.creation_date.writable = False 

### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later

db.commit()
