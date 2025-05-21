from pydantic import BaseModel
from enum import Enum
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

#  --------- View Schemas -------

class ViewServiceSchema(ServiceSchema):
    id: int
    status: Optional[ServiceStatusEnum]= None

    class Config:
        from_attributes = True

class ViewCategorySchema(CategorySchema):
    id: int
    services: Optional[ViewServiceSchema] = None

    class Config:
        from_attributes = True

schema= Union[ViewCategorySchema, ViewServiceSchema]

class ResponseSchema(ResponseModel):
    data: Optional[Union[schema, List[schema]]] = None