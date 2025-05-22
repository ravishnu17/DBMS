from fastapi import APIRouter, Form, UploadFile, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import ValidationError
from random import randrange
from sqlalchemy.exc import SQLAlchemyError

from constant.constant import root_path, db_limit, login_otp_expire_minute
from settings.db import get_db
from settings.auth import authenticate, genToken, encrypt, verify
from settings.config import secret
from models.users import User, UserProfile, Role, Country, State, District
from schemas.users import (
    UserSchema, UserProfileSchema, UserRegisterSchema, RoleSchema, VerifyOtpSchema, CurUser,  CreateCountry,  CreateState, CreateDistrict,
    LocationResponseModel, ResponseSchema
)
from datetime import datetime, date, timedelta, timezone
import json, os, shutil

profile_path= os.path.join("files", "profile")
base_path= os.path.join(root_path, profile_path)
try:
    if os.path.exists(base_path) == False:
        os.makedirs(base_path)
except Exception as e:
    print("Error base file creation: ", e)

proile_url= lambda user_id : secret.profile_url + f"{user_id}/"+ str(datetime.timestamp(datetime.now()))

app = APIRouter(prefix="/user", tags=["Users"])

def verify_location(user_profile: UserProfileSchema, db: Session):
    if user_profile.native_country_id != None and not db.query(Country).filter(Country.id == user_profile.native_country_id).first():
        return ResponseSchema(status=False, details="Country not found")
    if user_profile.native_state_id != None and not db.query(State).filter(State.id == user_profile.native_state_id).first():
        return ResponseSchema(status=False, details="State not found")
    if user_profile.native_district_id != None and not db.query(District).filter(District.id == user_profile.native_district_id).first():
        return ResponseSchema(status=False, details="District not found")
    
    if not db.query(Country).filter(Country.id == user_profile.current_country_id).first():
        return ResponseSchema(status=False, details="Country not found")
    if not db.query(State).filter(State.id == user_profile.current_state_id).first():
        return ResponseSchema(status=False, details="State not found")
    if not db.query(District).filter(District.id == user_profile.current_district_id).first():
        return ResponseSchema(status=False, details="District not found")
    return None

@app.post("/register")
def register_user(user: UserRegisterSchema, db: Session= Depends(get_db)):
    user_data= UserSchema(**user.model_dump())
    user_profile= UserProfileSchema(**user.model_dump())
    del user_profile.photo
    # check mobile number
    if user_data.mobile_number.isdigit() == False:
        return ResponseSchema(status=False, details="Invalid mobile number")
    if db.query(User).filter(User.mobile_number == user_data.mobile_number).first():
        return ResponseSchema(status=False, details="Mobile number already exists")
    
    # check email
    if user_data.email:
        if db.query(User).filter(User.email == user_data.email).first():
            return ResponseSchema(status=False, details="Email already exists")
    
    verify_location_response= verify_location(user_profile, db)
    if verify_location_response:
        return verify_location_response
    if user_profile.aadhaar_number :
        if not user_profile.aadhaar_number.isdigit() or not len(user_profile.aadhaar_number) == 12:
            return ResponseSchema(status=False, details="Invalid Aadhaar number")
    if user.password:
        user.password= encrypt(user.password)
    db_data= User(**user_data.model_dump(), password= user.password if user.password else None)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    try:
        user_profile.user_id= db_data.id
        today= date.today()
        user_profile.age= today.year - user_profile.date_of_birth.year - ((today.month, today.day) < (user_profile.date_of_birth.month, user_profile.date_of_birth.day))
        db.add(UserProfile(**user_profile.model_dump()))
        db.commit()
    except SQLAlchemyError as e:
        db.query(User).filter(User.id == db_data.id).delete()
        db.commit()
        return ResponseSchema(status=False, details="Something went wrong")

    return ResponseSchema(status=True, details="User registered successfully")

@app.post("/get_login_otp")
def login_otp(mobile_code: str, mobile_no: str, db: Session= Depends(get_db)):
    user_obj= db.query(User).filter(User.mobile_code == mobile_code, User.mobile_number == mobile_no)
    user= user_obj.first()
    if not user:
        return ResponseSchema(status=False, details="User not found")
    otp= randrange(100000, 999999)
    user_obj.update({"otp": otp, "otp_expires_at": datetime.now(timezone.utc) + timedelta(minutes=login_otp_expire_minute)}, synchronize_session=False)
    db.commit()
    return { "status": True, "details": "OTP sent successfully", "otp": otp }

@app.post("/login")
def login( data:OAuth2PasswordRequestForm=Depends(), db: Session= Depends(get_db)):
    user= db.query(User).filter(User.email == data.username).first()
    if not user:
        return ResponseSchema(status=False, details="User not found")
    if not verify(data.password, user.password):
        return ResponseSchema(status=False, details="Invalid credentials")

    token= genToken(CurUser(user_id= user.id, role_id= user.role_id, name= user.name, email= user.email).model_dump())
    return { "status": True, "details": "Login successful", "access_token": token, "token_type": "bearer" }

@app.post("/mobile_login")
def mobile_login(data:VerifyOtpSchema, db: Session= Depends(get_db)):
    user= db.query(User).filter(User.mobile_number == data.mobile_number, User.mobile_code == data.mobile_code).first()
    if not user:
        return ResponseSchema(status=False, details="User not found")
    if not user.otp:
        return ResponseSchema(status=False, details="OTP not sent")

    if int(user.otp) != int(data.otp):
        return ResponseSchema(status=False, details="Invalid credentials")
    if user.otp_expires_at < datetime.now(timezone.utc):
        return ResponseSchema(status=False, details="OTP expired")
    db.query(User).filter(User.id == user.id).update({"otp": None, "otp_expires_at": None}, synchronize_session=False)
    db.commit()
    token= genToken(CurUser(user_id= user.id, role_id= user.role_id, name= user.name, email= user.email).model_dump())
    return { "status": True, "details": "Login successful", "access_token": token, "token_type": "bearer" }

# get current User
@app.get("/me")
def get_current_user(db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    user = db.query(User).filter(User.id == curr_user.user_id).first()
    if not user:
        return ResponseSchema(status=False, details="User not found")
    if user.profile.photo:
        user.profile.photo= proile_url(user.id)
        user.native_country= user.profile.native_country
        user.current_country= user.profile.current_country
        user.native_state= user.profile.native_state
        user.current_state= user.profile.current_state
        user.native_district= user.profile.native_district
        user.current_district= user.profile.current_district

    data= {**user.__dict__, **user.profile.__dict__, "role": user.role}
    return ResponseSchema(status=True, details="User found", data=data)

#list users
@app.get("")
def list_users( skip: int = 0, limit: int = db_limit, search: Optional[str] = None, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    query = db.query(User).filter(User.id != secret.s_admin_id)
    if search:
        query = query.filter(or_(User.name.ilike(f"%{search}%"), User.email.ilike(f"%{search}%"), User.mobile_number.ilike(f"%{search}%")))
    query= query.order_by(User.name.asc())
    if limit:
        query= query.limit(limit).offset(skip)
    total= query.count()
    result= query.all()
    data= []
    for user in result:
        if user.profile and user.profile.photo:
            user.profile.photo= proile_url(user.id)
            
        user.profile.photo= proile_url(user.id)
        user.native_country= user.profile.native_country
        user.current_country= user.profile.current_country
        user.native_state= user.profile.native_state
        user.current_state= user.profile.current_state
        user.native_district= user.profile.native_district
        user.current_district= user.profile.current_district
        data.append({**user.__dict__, **user.profile.__dict__, "role": user.role})
        
    # return {"status": True, "details": "Users fetched", "data": data, "total_count": total}
    return ResponseSchema(status=True, details="Users fetched", data=data, total_count=total)

@app.put("/update/{user_id}")
def update_user(user_id: int, user: str= Form(...), profile:UploadFile= None, db: Session= Depends(get_db)):
    db_user_obj= db.query(User).filter(User.id == user_id)
    if not db_user_obj.first():
        return ResponseSchema(status=False, details="User not found")
    db_user_profile_obj= db.query(UserProfile).filter(UserProfile.user_id == user_id)

    try:
        user= json.loads(user)
        user_data= UserSchema(**user)
        user_profile= UserProfileSchema(**user)
        user_profile.user_id= user_id
        del user_profile.photo, user_profile.age, 

        # check mobile number
        if db.query(User).filter(User.id != user_id, User.mobile_number == user_data.mobile_number).first():
            return ResponseSchema(status=False, details="Mobile number already exists")
        # check email
        if user_data.email:
            if db.query(User).filter(User.email == user_data.email, User.id != user_id).first():
                return ResponseSchema(status=False, details="Email already exists")
        
        verify_location_response= verify_location(user_profile, db)
        if verify_location_response:
            return verify_location_response
        
        if user_profile.aadhaar_number :
            if not user_profile.aadhaar_number.isdigit() or not len(user_profile.aadhaar_number) == 12:
                return ResponseSchema(status=False, details="Invalid Aadhaar number")
        else:
            user_profile.aadhaar_number= None
        
        db_user_obj.update(user_data.model_dump(), synchronize_session=False)

        if profile:
            if os.path.exists(base_path) == False:
                os.makedirs(base_path)
            filename= f"{user_data.name}_{user_id}.{profile.filename.split('.')[-1]}"
            with open(os.path.join(base_path, filename), "wb") as f:
                shutil.copyfileobj(profile.file, f)
            user_profile.photo= os.path.join(profile_path, filename)

        today= date.today()
        user_profile.age= today.year - user_profile.date_of_birth.year - ((today.month, today.day) < (user_profile.date_of_birth.month, user_profile.date_of_birth.day))
        
        db_user_profile_obj.update(user_profile.model_dump(), synchronize_session=False)
        db.commit()
    except ValidationError as e:
        return ResponseSchema(status=False, details=e.errors())
    except Exception as e:
        print(e)
        return ResponseSchema(status=False, details="Invalid data")
    return ResponseSchema(status=True, details="User updated successfully")

# delete user
@app.delete("/delete/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    db_user_obj= db.query(User).filter(User.id == user_id)
    if not db_user_obj.first():
        return ResponseSchema(status=False, details="User not found")
    db_user_obj.delete()
    db.commit()
    return ResponseSchema(status=True, details="User deleted successfully")

# view profile
@app.get("/profile/{user_id}/{timestamp}")
def view_profile(user_id: int, timestamp: str, db: Session = Depends(get_db)):
    user= db.query(User).filter(User.id == user_id).first()
    if not user:
        return ResponseSchema(status=False, details="User not found")
    user_profile= db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not user_profile or user_profile.photo == None:
        return ResponseSchema(status=False, details="User profile not found")
    file_name= user_profile.photo.split("/")[-1]
    if not os.path.exists(os.path.join(base_path, file_name)):
        return ResponseSchema(status=False, details="File not found")

    return FileResponse(user_profile.photo, headers={"Content-Disposition": f"inline; filename={file_name}"}, media_type="image/jpeg", filename=f"{user.name}_{user_id}.jpg")


# -------- ROLE --------

# Create Role(s)
@app.post("/role")
def create_roles(roles: List[RoleSchema], db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    role_objs = []
    for role_data in roles:
        if db.query(Role).filter(Role.name == role_data.name).first():
            continue  # Skip duplicates
        role_obj = Role(name=role_data.name, is_default=role_data.is_default, created_by=curr_user.user_id)
        db.add(role_obj)
        db.commit()
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
    query= query.order_by(Role.name.asc())
    
    if limit:
        query= query.limit(limit).offset(skip)
    total= query.count()
    return ResponseSchema(status=True, details="Roles fetched", data=query.all(), total_count=total)

# Update Role
@app.put("/role/{role_id}")
def update_role(role_id: int, role_data: RoleSchema, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    role_obj = db.query(Role).filter(Role.id == role_id)
    if not role_obj.first():
        raise HTTPException(status_code=404, detail="Role not found")
    
    role_obj.update(role_data.model_dump(), synchronize_session=False)
    db.commit()

    return ResponseSchema(status=True, details="Role updated")

# Delete Role
@app.delete("/role/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    role_obj = db.query(Role).filter(Role.id == role_id).first()
    if not role_obj:
        raise HTTPException(status_code=404, detail="Role not found")
    db.delete(role_obj)
    db.commit()
    return {"status": True, "details": "Role deleted successfully"}


# -------- COUNTRY --------
@app.post("/country")
def create_countries(payload: List[CreateCountry], db: Session = Depends(get_db), curr_user:CurUser= Depends(authenticate)):
    countries = [Country(**p.model_dump()) for p in payload]
    db.add_all(countries)
    db.commit()
    return LocationResponseModel(status=True, details="Countries created")


@app.get("/country")
def list_countries( db: Session = Depends(get_db), skip: int = 0, limit: int = db_limit, search: Optional[str] = None):
    query = db.query(Country)
    if search:
        query = query.filter(Country.name.ilike(f"%{search}%"))
    total = query.count()
    query= query.order_by(Country.name.asc())
    if limit > 0:
        query = query.offset(skip).limit(limit)
    result = query.all()
    return LocationResponseModel(status=True, details="Countries fetched", data=result, total_count=total)

# update country
@app.put("/country/{country_id}")
def update_country(country_id: int, country_data: CreateCountry, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    country_obj = db.query(Country).filter(Country.id == country_id)
    if not country_obj.first():
        return ResponseSchema(status=False, details="Country not found")
    
    country_obj.update(country_data.model_dump(), synchronize_session=False)
    db.commit()

    return ResponseSchema(status=True, details="Country updated")

# delete country
@app.delete("/country/{country_id}")
def delete_country(country_id: int, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    country_obj = db.query(Country).filter(Country.id == country_id).first()
    if not country_obj:
        return ResponseSchema(status=False, details="Country not found")
    db.delete(country_obj)
    db.commit()
    return {"status": True, "details": "Country deleted successfully"}

# -------- STATE --------
@app.post("/state", response_model=LocationResponseModel)
def create_states(payload: List[CreateState], db: Session = Depends(get_db)):
    states = [State(**p.model_dump()) for p in payload]
    db.add_all(states)
    db.commit()
    return LocationResponseModel(status=True, details="States created")

@app.get("/state")
def list_states( skip: int = 0, limit: int = db_limit, country_id: int = None, db: Session = Depends(get_db), search: Optional[str] = None):
    query = db.query(State)
    if search:
        query = query.filter(State.name.ilike(f"%{search}%"))
    if country_id:
        query = query.filter(State.country_id == country_id)
    total = query.count()
    query= query.order_by(State.name.asc())
    if limit > 0:
        query = query.offset(skip).limit(limit)
    result = query.all()
    return LocationResponseModel(status=True, details="States fetched", data=result, total_count=total)

# update state
@app.put("/state/{state_id}")
def update_state(state_id: int, state_data: CreateState, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    state_obj = db.query(State).filter(State.id == state_id)
    if not state_obj.first():
        return ResponseSchema(status=False, details="State not found")
    
    state_obj.update(state_data.model_dump(), synchronize_session=False)
    db.commit()

    return ResponseSchema(status=True, details="State updated")

# delete state
@app.delete("/state/{state_id}")
def delete_state(state_id: int, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    state_obj = db.query(State).filter(State.id == state_id).first()
    if not state_obj:
        return ResponseSchema(status=False, details="State not found")
    db.delete(state_obj)
    db.commit()
    return {"status": True, "details": "State deleted successfully"}

# -------- DISTRICT --------
@app.post("/district")
def create_districts(payload: List[CreateDistrict], db: Session = Depends(get_db)):
    districts = [District(**p.model_dump()) for p in payload]
    db.add_all(districts)
    db.commit()
    return LocationResponseModel(status=True, details="Districts created")

@app.get("/district")
def list_districts( skip: int = 0, limit: int = db_limit, state_id: int = None, db: Session = Depends(get_db), search: Optional[str] = None):
    query = db.query(District)
    if search:
        query = query.filter(District.name.ilike(f"%{search}%"))
    if state_id:
        query = query.filter(District.state_id == state_id)
    total = query.count()
    query= query.order_by(District.name.asc())
    if limit > 0:
        query = query.offset(skip).limit(limit)
    result = query.all()
    return LocationResponseModel(status=True, details="Districts fetched", data=result, total_count=total)

# update district
@app.put("/district/{district_id}")
def update_district(district_id: int, district_data: CreateDistrict, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    district_obj = db.query(District).filter(District.id == district_id)
    if not district_obj.first():
        return ResponseSchema(status=False, details="District not found")
    
    district_obj.update(district_data.model_dump(), synchronize_session=False)
    db.commit()

    return ResponseSchema(status=True, details="District updated")

# delete district
@app.delete("/district/{district_id}")
def delete_district(district_id: int, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):    
    district_obj = db.query(District).filter(District.id == district_id).first()
    if not district_obj:
        return ResponseSchema(status=False, details="District not found")
    db.delete(district_obj)
    db.commit()
    return {"status": True, "details": "District deleted successfully"}