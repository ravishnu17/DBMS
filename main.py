from fastapi import FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from settings.db import session_local, engine
from models.users import Role, User, UserProfile, Country, State, District
from schemas.users import UserSchema, UserProfileSchema
from settings.config import secret
from settings.auth import encrypt
from APIs import users
from datetime import datetime, date
import json

today = date.today()

def initial_load():
    db:Session= session_local()
    initial_data={}
    with open('constant/initial.json', 'rb') as file:
        initial_data= json.load(file)
    try:
        if inspect(engine).has_table('tbl_role'):
            if db.query(Role).count() == 0:
                for role in initial_data['roles']:
                    db.add(Role(name=role, is_default= True))
                db.commit()
                print('\n----- Role data loaded! -----')
        if inspect(engine).has_table('tbl_country'):
            if db.query(Country).count() == 0:
                for country in initial_data['country']:
                    db.add(Country(name=country))
                db.commit()
                print('\n----- Country data loaded! -----')
        if inspect(engine).has_table('tbl_state'):
            if db.query(State).count() == 0:
                for state in initial_data['states']:
                    db.add(State(name=state['name'], country_id=state['country_id']))
                db.commit()
                print('\n----- State data loaded! -----')
        if inspect(engine).has_table('tbl_district'):
            if db.query(District).count() == 0:
                for district in initial_data['districts']:
                    db.add(District(name=district['name'], state_id=district['state_id']))
                db.commit()
                print('\n----- District data loaded! -----')
        if inspect(engine).has_table('tbl_user'):
            if db.query(User).count() == 0:
                temp= initial_data['admin']
                user= UserSchema(**temp)
                password= encrypt(secret.s_key)
                user_profile= UserProfileSchema(**temp)
                user_profile.user_id= secret.s_admin_id
                dob = datetime.strptime(temp['date_of_birth'], '%Y-%m-%d').date()
                today= date.today()
                user_profile.age= today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                db.add(User(**user.model_dump(), password=password, role_id= secret.s_admin_role))
                db.add(UserProfile(**user_profile.model_dump()))
                db.commit()
                print('\n----- User data loaded! -----')
        db.close()
    except Exception as e:
        print('\n----- Connection failed! ERROR : ', e)

app = FastAPI(
    title="dbms API",
    version="1.0",
    on_startup=[initial_load]
)

@app.get('/')
def root():
    return {"message": "dbms API service is started"}

# include api routes with main app
app.include_router(users.app)

