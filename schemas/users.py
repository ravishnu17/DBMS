from pydantic import BaseModel, EmailStr
from typing import Optional, List, Union
from datetime import date

class RoleSchema(BaseModel):
    name: str
    is_default: Optional[bool] = False

class RoleView(BaseModel):
    id: int
    name: str
    is_default: bool

    class Config:
        from_attributes = True
        
class CurUser(BaseModel):
    user_id:int
    role_id:int
    name:str
    email:Optional[EmailStr]=None    

class UserSchema(BaseModel):
    # role_id: int= 3
    name: str
    mobile_code: str
    mobile_number: str
    email: Optional[EmailStr] = None
    # password: Optional[str]= None

    class Config:
        from_attributes = True

class UserProfileSchema(BaseModel):
    user_id: Optional[int] = None
    date_of_birth: date
    photo: Optional[str] = None
    age: Optional[int] = None
    aadhaar_number: Optional[str] = None
    native_address_line: Optional[str] = None
    native_district_id: Optional[int] = None
    native_state_id: Optional[int] = None
    native_country_id: Optional[int] = None
    current_address_line: str
    current_district_id: int
    current_state_id: int
    current_country_id: int

    skills: Optional[str] = None
    job_type: Optional[str] = None
    language_pref: Optional[str] = None

class UserRegisterSchema(UserSchema, UserProfileSchema):
    pass


class UserView(UserProfileSchema):
    id: int
    name: str
    email: Optional[EmailStr] = None
    mobile_number: str
    mobile_code: str
    role_id: int
    role: RoleView
    class Config:
        from_attributes = True

class VerifyOtpSchema(BaseModel):
    mobile_code: str
    mobile_number: str
    otp: int

class ResponseModel(BaseModel):
    status: bool
    details: Union[str, dict, list]
    total_count: int = 0


# ----- Country Schemas -----
class CountryBase(BaseModel):
    name: str

class CreateCountry(CountryBase):
    pass

class ViewCountry(CountryBase):
    id: int
    class Config:
        from_attributes = True


# ----- State Schemas -----
class StateBase(BaseModel):
    name: str
    country_id: int

class CreateState(StateBase):
    pass

class ViewState(StateBase):
    id: int
    class Config:
        from_attributes = True


# ----- District Schemas -----
class DistrictBase(BaseModel):
    name: str
    state_id: int

class CreateDistrict(DistrictBase):
    pass

class ViewDistrict(DistrictBase):
    id: int
    class Config:
        from_attributes = True


# ----- Combined Location Response -----
LocationSchema = Union[ViewCountry, ViewState, ViewDistrict]

class LocationResponseModel(ResponseModel):
    data: Optional[Union[LocationSchema, List[LocationSchema]]] = None

schema= Union[UserView]

class ResponseSchema(ResponseModel):
    data: Optional[Union[schema, List[schema]]] = None