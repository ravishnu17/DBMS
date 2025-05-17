from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, BigInteger, Date, LargeBinary, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from settings.db import Base

# meta data without foreign key
class MetaData(Base):
    __abstract__ = True
    
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_by= Column(Integer, nullable=True)
    updated_at= Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    updated_by= Column(Integer, nullable=True)

# meta data with foreign key
class BaseModel(Base):
    __abstract__ = True

    active= Column(Boolean, nullable=False, server_default='True')
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_by= Column(Integer, ForeignKey("tbl_user.id", ondelete="SET NULL"), nullable=True, index= True)
    updated_at= Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    updated_by= Column(Integer, ForeignKey("tbl_user.id", ondelete="SET NULL"), nullable=True, index= True)


# role module features
class Role(MetaData):
    __tablename__ = 'tbl_role'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    is_default = Column(Boolean, nullable=False, server_default='False')

class Country(MetaData):
    __tablename__ = "tbl_country"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, nullable=False, index=True)


class State(MetaData):
    __tablename__ = "tbl_state"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, nullable=False, index=True)
    country_id = Column(Integer, ForeignKey("tbl_country.id"), nullable=False)

class District(MetaData):
    __tablename__ = "tbl_district"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, nullable=False, index=True)
    state_id = Column(Integer, ForeignKey("tbl_state.id"), nullable=False)

class User(MetaData):
    __tablename__ = "tbl_user"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    role_id = Column(Integer, ForeignKey('tbl_role.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    mobile_code = Column(String, nullable=False)
    mobile_number = Column(String, nullable=False, index=True, unique=True)
    email = Column(String, unique=True, index=True, nullable=True)
    otp_verified = Column(Boolean, nullable=False, default=False) # mobile otp verification
    password= Column(Text, nullable=True) # for admin
    otp= Column(BigInteger, nullable=True) # for migrant login
    otp_expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

class UserProfile(BaseModel):
    __tablename__ = "tbl_user_profile"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("tbl_user.id"), nullable=False)

    photo = Column(Text, nullable=True)
    date_of_birth = Column(Date, nullable=False)
    age = Column(Integer, nullable=True)  # Can be auto-calculated in app logic
    aadhaar_number = Column(String, nullable=True, index=True)

    native_address_line = Column(Text, nullable=True, index=True)
    native_district_id = Column(Integer, ForeignKey("tbl_district.id"), nullable=True, index=True)
    native_state_id = Column(Integer, ForeignKey("tbl_state.id"), nullable=True, index=True)
    native_country_id = Column(Integer, ForeignKey("tbl_country.id"), nullable=True, index=True)

    current_address_line = Column(Text, nullable=False, index=True)
    current_district_id = Column(Integer, ForeignKey("tbl_district.id"), nullable=False, index=True)
    current_state_id = Column(Integer, ForeignKey("tbl_state.id"), nullable=False, index=True)
    current_country_id = Column(Integer, ForeignKey("tbl_country.id"), nullable=False, index=True)

    skills = Column(Text, nullable=True)
    job_type = Column(String, nullable=True)
    language_pref = Column(String, nullable=True)