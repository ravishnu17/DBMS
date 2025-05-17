from fastapi import APIRouter, Form, UploadFile, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import ValidationError

from constant.constant import root_path, db_limit
from settings.db import get_db
from settings.auth import authenticate, genToken, encrypt, verify
from settings.config import secret
from models.users import User, UserProfile, Role, Country, State, District
from schemas.users import (
    UserSchema, UserProfileSchema, RoleSchema, RoleView, CurUser,  CreateCountry, ViewCountry,  CreateState, ViewState, CreateDistrict, ViewDistrict,
    LocationResponseModel, ResponseSchema
)
from datetime import datetime, date
import json, os, shutil

profile_path= os.path.join("files", "profile")
base_path= os.path.join(root_path, profile_path)
try:
    if os.path.exists(base_path) == False:
        os.makedirs(base_path)
except Exception as e:
    print("Error base file creation: ", e)

app = APIRouter(prefix="/user", tags=["Users"])

@app.post("/register")
def register_user(user: str= Form(...), profile:UploadFile= None, db: Session= Depends(get_db)):
    try:
        user= json.loads(user)
        user_data= UserSchema(**user)
        user_profile= UserProfileSchema(**user)
        # return {"status": True, "details": "User created", "data": user_data, "profile": user_profile}
        # check mobile number
        if db.query(User).filter(User.mobile_number == user_data.mobile_number).first():
            return ResponseSchema(status=False, details="Mobile number already exists")
        # check email
        if db.query(User).filter(User.email == user_data.email).first():
            return ResponseSchema(status=False, details="Email already exists")
        
        if user_profile.native_country_id and not db.query(Country).filter(Country.id == user_profile.native_country_id).first():
            return ResponseSchema(status=False, details="Country not found")
        if user_profile.native_state_id and not db.query(State).filter(State.id == user_profile.native_state_id).first():
            return ResponseSchema(status=False, details="State not found")
        if user_profile.native_district_id and not db.query(District).filter(District.id == user_profile.native_district_id).first():
            return ResponseSchema(status=False, details="District not found")
        
        if not db.query(Country).filter(Country.id == user_profile.current_country_id).first():
            return ResponseSchema(status=False, details="Country not found")
        if not db.query(State).filter(State.id == user_profile.current_state_id).first():
            return ResponseSchema(status=False, details="State not found")
        if not db.query(District).filter(District.id == user_profile.current_district_id).first():
            return ResponseSchema(status=False, details="District not found")
        if user_profile.aadhaar_number and not user_profile.aadhaar_number.isdigit() or not len(user_profile.aadhaar_number) == 12:
            return ResponseSchema(status=False, details="Invalid Aadhaar number")
        user_data.password= encrypt(user_data.password)
        db_data= User(**user_data.model_dump())
        db.add(db_data)
        db.commit()
        db.refresh(db_data)
        user_profile.user_id= db_data.id
        if profile:
            if os.path.exists(base_path) == False:
                os.makedirs(base_path)
            filename= f"{user_data.name}_{db_data.id}.{profile.filename.split('.')[-1]}"
            with open(os.path.join(base_path, filename), "wb") as f:
                shutil.copyfileobj(profile.file, f)
            user_profile.photo= os.path.join(profile_path, filename)

        today= date.today()
        user_profile.age= today.year - user_profile.date_of_birth.year - ((today.month, today.day) < (user_profile.date_of_birth.month, user_profile.date_of_birth.day))
        db.add(UserProfile(**user_profile.model_dump()))
        db.commit()
    except ValidationError as e:
        return ResponseSchema(status=False, details=e.errors())
    except Exception as e:
        print(e)
        return ResponseSchema(status=False, details="Invalid data")
    return ResponseSchema(status=True, details="User registered successfully")

@app.post("/login")
def login(data:OAuth2PasswordRequestForm=Depends(), db: Session= Depends(get_db)):
    user= db.query(User).filter(User.email == data.username).first()
    if not user:
        return ResponseSchema(status=False, details="User not found")
    if not verify(data.password, user.password):
        return ResponseSchema(status=False, details="Invalid credentials")
    token= genToken(CurUser(user_id= user.id, role_id= user.role_id, name= user.name, email= user.email).model_dump())
    return { "status": True, "details": "Login successful", "access_token": token, "token_type": "bearer" }

# -------- ROLE --------

# Create Role(s)
@app.post("/role", response_model=List[RoleView])
def create_roles(roles: List[RoleSchema], db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    role_objs = []
    for role_data in roles:
        if db.query(Role).filter(Role.name == role_data.name).first():
            continue  # Skip duplicates
        role_obj = Role(name=role_data.name, is_default=role_data.is_default, created_by=curr_user.user_id)
        db.add(role_obj)
        db.refresh(role_obj)
        role_objs.append(role_obj)
    db.commit()
    return ResponseSchema(status=True, details="Roles created", data=role_objs)

# View Roles
@app.get("/role")
def list_roles( skip: int = 0, limit: int = db_limit, search: Optional[str] = None, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    query = db.query(Role).filter(Role.id != secret.s_admin_role)
    if search:
        query = query.filter(Role.name.ilike(f"%{search}%"))
    if limit:
        query= query.limit(limit).offset(skip)
    total= query.count()
    return ResponseSchema(status=True, details="Roles fetched", data=query.all(), total_count=total)

# Update Role
@app.put("/{role_id}", response_model=RoleView)
def update_role(role_id: int, role_data: RoleSchema, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    role_obj = db.query(Role).filter(Role.id == role_id)
    if not role_obj.first():
        raise HTTPException(status_code=404, detail="Role not found")
    
    role_obj.update(role_data.model_dump(), synchronize_session=False)
    db.commit()

    return ResponseSchema(status=True, details="Role updated")

# Delete Role
@app.delete("/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    role_obj = db.query(Role).filter(Role.id == role_id).first()
    if not role_obj:
        raise HTTPException(status_code=404, detail="Role not found")
    db.delete(role_obj)
    db.commit()
    return {"status": True, "details": "Role deleted successfully"}


# -------- COUNTRY --------
@app.post("/country", response_model=LocationResponseModel)
def create_countries(payload: List[CreateCountry], db: Session = Depends(get_db), curr_user:CurUser= Depends(authenticate)):
    countries = [Country(**p.dict()) for p in payload]
    db.add_all(countries)
    db.commit()
    return LocationResponseModel(status=True, details="Countries created", total_count=len(countries))


@app.get("/countries", response_model=LocationResponseModel)
def list_countries(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = Query(None)
):
    query = db.query(Country)
    if search:
        query = query.filter(Country.name.ilike(f"%{search}%"))
    total = query.count()
    if limit > 0:
        query = query.offset(skip).limit(limit)
    result = query.all()
    return LocationResponseModel(status=True, details="Countries fetched", data=result, total_count=total)


# -------- STATE --------
@app.post("/state", response_model=LocationResponseModel)
def create_states(payload: List[CreateState], db: Session = Depends(get_db)):
    states = [State(**p.dict()) for p in payload]
    db.add_all(states)
    db.commit()
    return LocationResponseModel(status=True, details="States created", total_count=len(states))


@app.get("/states", response_model=LocationResponseModel)
def list_states(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = Query(None)
):
    query = db.query(State)
    if search:
        query = query.filter(State.name.ilike(f"%{search}%"))
    total = query.count()
    if limit > 0:
        query = query.offset(skip).limit(limit)
    result = query.all()
    return LocationResponseModel(status=True, details="States fetched", data=result, total_count=total)


# -------- DISTRICT --------
@app.post("/district", response_model=LocationResponseModel)
def create_districts(payload: List[CreateDistrict], db: Session = Depends(get_db)):
    districts = [District(**p.dict()) for p in payload]
    db.add_all(districts)
    db.commit()
    return LocationResponseModel(status=True, details="Districts created", total_count=len(districts))


@app.get("/districts", response_model=LocationResponseModel)
def list_districts(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = Query(None)
):
    query = db.query(District)
    if search:
        query = query.filter(District.name.ilike(f"%{search}%"))
    total = query.count()
    if limit > 0:
        query = query.offset(skip).limit(limit)
    result = query.all()
    return LocationResponseModel(status=True, details="Districts fetched", data=result, total_count=total)
