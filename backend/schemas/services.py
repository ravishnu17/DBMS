from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, Union, List

from .users import ResponseModel
from models.service import CategoryTypeEnum, ServiceStatusEnum

class CategorySchema(BaseModel):
    name: str
    type: CategoryTypeEnum
    available: bool= True

    class Config:
        from_attributes = True


class ServiceSchema(BaseModel):
    category_id: int
    description: str
    requested_user_id: Optional[int] = None

    class Config:
        from_attributes = True

class EventSchema(BaseModel):
    title: str
    description: Optional[str] = None
    all_day: Optional[bool] = None
    start_datetime: datetime
    end_datetime: Optional[datetime] = None
    location: str
    max_participants: Optional[int] = None
    class Config:
        from_attributes = True

class EventRSVPSchema(BaseModel):
    event_id: int
    user_id: int
    status: Optional[str] = None
    class Config:
        from_attributes = True

#  --------- View Schemas -------

class ViewServiceSchema(ServiceSchema):
    id: int
    status: Optional[ServiceStatusEnum]= None

    class Config:
        from_attributes = True

class ViewCategorySchema(CategorySchema):
    id: int
    requested: Optional[ViewServiceSchema] = None

    class Config:
        from_attributes = True

class ViewEventSchema(EventSchema):
    id: int
    registered_count: Optional[int] = 0
    # rsvp: Optional[EventRSVPSchema] = None
    class Config:
        from_attributes = True

class ViewEventRSVPSchema(EventRSVPSchema):
    id: int

schema= Union[ViewCategorySchema, ViewServiceSchema, ViewEventSchema, ViewEventRSVPSchema]

class ResponseSchema(ResponseModel):
    data: Optional[Union[schema, List[schema]]] = None