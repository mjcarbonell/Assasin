import os 
import json 
from py4web import action, request, abort, redirect, URL
from .common import db, session, T, cache, auth, logger, Field
from .models import get_user_email
from .settings import APP_FOLDER 
from py4web.utils.url_signer import URLSigner
from py4web.utils.form import Form, FormStyleBulma

url_signer = URLSigner(session)

# filename = os.path.join(APP_FOLDER, "data", "table.json")

@action('index') # fixtures/index  
@action.uses('index.html', db, auth.user, url_signer) # PAGE BASE HTML NAME 
def index():
    # rows = db(db.contact.user_email == get_user_email()).select()
    rows = db(
            (db.contact.user_email == get_user_email()) &
            (db.phone.contact_id == db.contact.id) 
              ).select() 
    # print("NEWWW")
    contacts = []
    phones = []
    for row in rows: 
        if (row.contact not in contacts):
            contacts.append(row.contact)
        phones.append(row.phone)

    # print("LISTSSSSSS")
    # print(contacts)
    # print(phones)


    return dict(contacts=contacts, phones=phones, url_signer=url_signer)

@action('add', method=["GET", "POST"])
@action.uses('add.html', url_signer, db, session, auth.user)
def add():

    form = Form(db.contact, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        contact = db(
            (db.contact.user_email == get_user_email()) & 
            (db.contact.first_name == form.vars["first_name"]) & 
            (db.contact.last_name == form.vars["last_name"])
                     ).select().first()
        # print(form.vars["first_name"])
        # INSERTING PHONE NUMBER AT SPECIFIC FIRST AND LAST NAME CONTACT GIVEN BY FORM 
        db.phone.insert(
            contact_id= contact.id,
            user_email=get_user_email()
        )
        redirect(URL('index'))
    return dict(form=form)

@action('edit_contact/<contact_id:int>', method=["GET", "POST"])
@action.uses('edit_contact.html', url_signer, db, session, auth.user, url_signer.verify())
def edit_contact(contact_id=None):
    assert contact_id is not None
    p = db.contact[contact_id]
    if p is None:
        redirect(URL('index'))
    if p.user_email != get_user_email():
        redirect(URL('index'))
    form = Form(db.contact, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('index'))
    return dict(form=form)

@action('delete_contact/<contact_id:int>')
@action.uses(db, session, auth.user, url_signer.verify())
def delete_contact(contact_id=None):
    assert contact_id is not None
    db(db.contact.id == contact_id).delete()
    redirect(URL('index'))

        

@action('edit_phone/<contact_id:int>', method=["GET", "POST"])
@action.uses('edit_phone.html', db, url_signer, session, auth.user, url_signer.verify())
def edit_phone(contact_id=None):
    # print("CONTACT ID")
    # print(contact_id)
    rows = db(
            # (db.contact.user_email == get_user_email()) &
            (db.phone.contact_id == contact_id) 
              ).select() 
    return dict(rows=rows, contact_id=contact_id, url_signer=url_signer)

@action('edit_number/<phone_id:int>', method=["GET", "POST"])
@action.uses('edit_number.html', db, url_signer, session, auth.user, url_signer.verify())
def edit_number(phone_id=None):
    assert phone_id is not None
    p = db.phone[phone_id]
    if p is None:
        redirect(URL('edit_phone', p.contact_id, signer=url_signer))
    if p.user_email != get_user_email():
        redirect(URL('edit_phone', p.contact_id, signer=url_signer))
    form = Form(db.phone, record=p, deletable=False, cs4rf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('edit_phone', p.contact_id, signer=url_signer))
    return dict(form=form)



@action('delete_number/<phone_id:int>')
@action.uses(db, session, auth.user, url_signer.verify())
def delete_number(phone_id=None):
    assert phone_id is not None
    p = db.phone[phone_id]
    contact_id = p.contact_id
    phones = db(
        (db.phone.user_email == get_user_email()) & 
        (db.phone.contact_id == contact_id)
    ).select()
    print("PHONESSSS")
    print(len(phones))
    if(len(phones) > 1):
        db(db.phone.id == phone_id).delete()
        redirect(URL('edit_phone', contact_id, signer=url_signer))
    else: 
        redirect(URL('edit_phone', contact_id, signer=url_signer))

@action('add_number/<contact_id:int>', method=["GET", "POST"])
@action.uses('add_number.html', db, session, auth.user, url_signer.verify())
def add_number(contact_id=None):
    assert contact_id is not None 
    
    form = Form([
        Field('phone_number', type='string', style='width: 50%;'),
        Field('purpose', type='string', style='width: 50%;')
    ], csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        db.phone.insert(
            contact_id=contact_id,
            phone_number=form.vars["phone_number"],
            purpose=form.vars["purpose"],
            user_email=get_user_email()
        )
        # form.vars["contact_id"] = contact_id
        redirect(URL('edit_phone', contact_id, signer=url_signer))
    return dict(form=form)



