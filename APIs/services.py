from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from models.service import Category, Service, HelpRequest, CategoryTypeEnum, ServiceStatusEnum
from schemas.services import ResponseSchema, CategorySchema, ServiceSchema
from schemas.users import CurUser
from settings.auth import authenticate, adminAuthenticate
from settings.db import get_db

from constant.constant import db_limit

category_router = APIRouter(
    prefix="/category",
    tags=["Category"],
)

@category_router.get("")
def read_categories(skip: int = 0, limit: int = db_limit, search: str = None, type_: CategoryTypeEnum = None, available: bool = None, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    categories = db.query(Category).options(joinedload(Category.services))
    if search:
        categories = categories.filter(Category.name.ilike(f"%{search}%"))
    if available != None:
        categories = categories.filter(Category.available == available)
    if type_:
        categories = categories.filter(Category.type == type_)

    categories= categories.order_by(Category.name.asc())

    if limit:
        categories = categories.limit(limit).offset(skip)
    total_count = categories.count()
    categories = categories.all()
    for category in categories:
        if category.services:
            category.services = category.services if category.services.requested_user_id == curr_user.user_id else None
    return ResponseSchema(status=True,details="Categories fetched", data=categories, total_count=total_count)

@category_router.post("")
def create_category(category: CategorySchema, db: Session = Depends(get_db), curr_user: CurUser = Depends(adminAuthenticate)):
    existing_category = db.query(Category).filter(Category.name == category.name).first()
    if existing_category:
        return ResponseSchema(status=False, details="Category already exists")
    category = Category(**category.model_dump(), created_by=curr_user.user_id, updated_by= curr_user.user_id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return ResponseSchema(status=True, details="Category created successfully", data=category)

@category_router.put("/{category_id}")
def update_category(category_id: int, category: CategorySchema, db: Session = Depends(get_db), curr_user: CurUser = Depends(adminAuthenticate)):
    existing_category = db.query(Category).get(category_id)
    if existing_category is None:
        return ResponseSchema(status=False, details="Category not found")
    if db.query(Category).filter(Category.name == category.name, Category.id != category_id).first():
        return ResponseSchema(status=False, details="Category with this name already exists")
    for key, value in category.model_dump().items():
        setattr(existing_category, key, value)
    db.commit()
    
    return ResponseSchema(status=True, details="Category updated successfully")

@category_router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), curr_user: CurUser = Depends(adminAuthenticate)):
    existing_category = db.query(Category).filter(Category.id == category_id)
    if not existing_category.first():
        return ResponseSchema(status=False, details="Category not found")
    # check if this category is used in any service
    if db.query(Service).filter(Service.category_id == category_id).first():
        return ResponseSchema(status=False, details="Category have service requests, cannot be deleted")
    # check if this category is used in any help request
    if db.query(HelpRequest).filter(HelpRequest.category_id == category_id).first():
        return ResponseSchema(status=False, details="Category have help requests, cannot be deleted")
    existing_category.delete(synchronize_session=False)
    db.commit()
    
    return ResponseSchema(status=True, details="Category deleted successfully")

# -------------- Service APIs --------------

service_router = APIRouter(
    prefix="/service",
    tags=["Service"],
)

@service_router.get("_requests")
def read_services(skip: int = 0, limit: int = db_limit, search: str = None, category_id: int = None, status: ServiceStatusEnum = None, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    services = db.query(Service)
    if search:
        services = services.filter(Service.description.ilike(f"%{search}%"))
    if category_id:
        services = services.filter(Service.category_id == category_id)
    if status:
        services = services.filter(Service.status == status)
    if limit:
        services = services.limit(limit).offset(skip)
    total_count = services.count()
    services = services.offset(skip).limit(limit).all()
    return ResponseSchema(status=True, details="Services request fetched", data=services, total_count=total_count)

@service_router.get("_my_requests")
def read_my_services(category_id: int=None, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    services = db.query(Service).filter(Service.requested_user_id == curr_user.user_id)
    if category_id:
        services = services.filter(Service.category_id == category_id)

    return ResponseSchema(status=True, details="Services request fetched", data=services.first())

@service_router.post("")
def create_service(service: ServiceSchema, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    service.requested_user_id = curr_user.user_id
    service = Service(**service.model_dump())
    # check this user already has a service request
    existing_service = db.query(Service).filter(Service.requested_user_id == curr_user.user_id, Service.category_id == service.category_id).first()
    if existing_service:
        return ResponseSchema(status=False, details="You already have a service request for this category")
    db.add(service)
    db.commit()
    db.refresh(service)
    return ResponseSchema(status=True, details="Service request created successfully", data=service)

@service_router.put("/{service_id}")
def update_service(service_id: int, service: ServiceSchema, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    del service.requested_user_id
    existing_service = db.query(Service).get(service_id)
    if existing_service is None:
        return ResponseSchema(status=False, details="Service request not found")
    
    for key, value in service.model_dump().items():
        if value is not None:
            setattr(existing_service, key, value)
    db.commit()
    
    return ResponseSchema(status=True, details="Service request updated successfully")

# update status
@service_router.put("/{service_id}/status")
def update_service_status(service_id: int, status: ServiceStatusEnum, db: Session = Depends(get_db), curr_user: CurUser = Depends(adminAuthenticate)):
    existing_service = db.query(Service).get(service_id)
    if existing_service is None:
        return ResponseSchema(status=False, details="Service request not found")
    
    existing_service.status = status
    db.commit()
    
    return ResponseSchema(status=True, details="Service request status updated successfully")

@service_router.delete("/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    existing_service = db.query(Service).filter(Service.id == service_id)
    if not existing_service.first():
        return ResponseSchema(status=False, details="Service request not found")
    existing_service.delete(synchronize_session=False)
    db.commit()
    
    return ResponseSchema(status=True, details="Service request deleted successfully")