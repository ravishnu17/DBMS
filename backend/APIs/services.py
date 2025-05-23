from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone
from models.service import Category, Service, HelpRequest, CategoryTypeEnum, ServiceStatusEnum, Event, EventRSVP, RSVPStatusEnum
from schemas.services import ResponseSchema, CategorySchema, ServiceSchema, EventSchema
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
            is_requested = filter(lambda x: x.requested_user_id == curr_user.user_id, category.services)
            is_requested =  list(is_requested) if is_requested else None
            category.requested = is_requested[0] if is_requested else None
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
    existing_obj = db.query(Category).filter(Category.id == category_id)
    existing_category = existing_obj.first()
    if existing_category is None:
        return ResponseSchema(status=False, details="Category not found")
    if db.query(Category).filter(Category.name == category.name, Category.id != category_id).first():
        return ResponseSchema(status=False, details="Category with this name already exists")
    existing_category.updated_by = curr_user.user_id
    existing_obj.update(category.model_dump(), synchronize_session=False)
    db.commit()
    
    return ResponseSchema(status=True, details="Category updated successfully")

@category_router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), curr_user: CurUser = Depends(adminAuthenticate)):
    existing_category = db.query(Category).filter(Category.id == category_id)
    if not existing_category.first():
        return ResponseSchema(status=False, details="Category not found")
    # check if this category is used in any service
    if db.query(Service).filter(Service.category_id == category_id).first():
        return ResponseSchema(status=False, details="Category has service requests, cannot be deleted")
    # check if this category is used in any help request
    if db.query(HelpRequest).filter(HelpRequest.category_id == category_id).first():
        return ResponseSchema(status=False, details="Category has help requests, cannot be deleted")
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
    services = services.all()
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
    service = Service(**service.model_dump(), created_by=curr_user.user_id, updated_by= curr_user.user_id)
    # check this user already has a service request
    existing_service = db.query(Service).filter(Service.requested_user_id == curr_user.user_id, Service.category_id == service.category_id).first()
    if existing_service:
        return ResponseSchema(status=False, details="You already have a service request for this category")
    db.add(service)
    db.commit()
    db.refresh(service)
    return ResponseSchema(status=True, details="Service request created successfully", data=service)

# update service description
@service_router.put("/{service_id}")
def update_service(service_id: int, service: ServiceSchema, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    del service.requested_user_id, service.category_id
    existing_service = db.query(Service).get(service_id)
    if existing_service is None:
        return ResponseSchema(status=False, details="Service request not found")
    
    existing_service.description = service.description
    existing_service.updated_by = curr_user.user_id
    db.commit()
    
    return ResponseSchema(status=True, details="Service request updated successfully")

# update status
@service_router.put("/{service_id}/status")
def update_service_status(service_id: int, status: ServiceStatusEnum, db: Session = Depends(get_db), curr_user: CurUser = Depends(adminAuthenticate)):
    existing_service = db.query(Service).get(service_id)
    if existing_service is None:
        return ResponseSchema(status=False, details="Service request not found")
    
    existing_service.status = status
    existing_service.updated_by = curr_user.user_id
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


# --------------- Events APIs --------------

event_router = APIRouter(
    prefix="/event",
    tags=["Event"],
)

@event_router.get("")
def read_events(skip: int = 0, limit: int = db_limit, search: str = None, all_events: bool = None, start_date: datetime = None, end_date: datetime = None, is_upcoming: bool = None, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    events = db.query(Event)
    if search:
        events = events.filter(Event.title.ilike(f"%{search}%"))
    if all_events:
        events = events.filter(Event.all_day == all_events)
    if start_date:
        events = events.filter(Event.start_datetime >= start_date)
    if end_date:
        events = events.filter(Event.end_datetime <= end_date)
    if is_upcoming:
        events = events.filter(Event.start_datetime >= datetime.now(timezone.utc))
    if limit:
        events = events.limit(limit).offset(skip)
    total_count = events.count()
    events = events.all()
    for event in events:
        event.registered_count= len(event.rsvp)
        event.is_registered= event.rsvp.user_id == curr_user.user_id if event.rsvp else None
    return ResponseSchema(status=True, details="Events fetched", data=events, total_count=total_count)

@event_router.post("")
def create_event(event: EventSchema, db: Session = Depends(get_db), curr_user: CurUser = Depends(adminAuthenticate)):
    event.start_datetime= event.start_datetime.replace(tzinfo=timezone.utc)
    if event.end_datetime:
        event.end_datetime= event.end_datetime.replace(tzinfo=timezone.utc)
    else:
        event.end_datetime= None
    if event.all_day:
        event.end_datetime= event.start_datetime.replace(tzinfo=timezone.utc).replace(hour=23, minute=59, second=59)

    if event.end_datetime and event.start_datetime > event.end_datetime:
        return ResponseSchema(status=False, details="End date should be greater than start date")
    # check if same event name and start time exists
    existing_event = db.query(Event).filter(Event.title == event.title, Event.start_datetime == event.start_datetime).first()
    if existing_event:
        return ResponseSchema(status=False, details="Event with same name and start time already exists")
    event = Event(**event.model_dump(), created_by=curr_user.user_id, updated_by= curr_user.user_id)
    db.add(event)
    db.commit()
    db.refresh(event)
    return ResponseSchema(status=True, details="Event created successfully", data=event)

@event_router.put("/{event_id}")
def update_event(event_id: int, event: EventSchema, db: Session = Depends(get_db), curr_user: CurUser = Depends(adminAuthenticate)):
    existing_event = db.query(Event).get(event_id)
    if existing_event is None:
        return ResponseSchema(status=False, details="Event not found")
    if event.start_datetime != existing_event.start_datetime:
        event.start_datetime= event.start_datetime.replace(tzinfo=timezone.utc)
    if event.end_datetime:
        event.end_datetime= event.end_datetime.replace(tzinfo=timezone.utc) if event.end_datetime != existing_event.end_datetime else existing_event.end_datetime
    # check if same event name and start time exists
    is_any_other_event = db.query(Event).filter(Event.title == event.title, Event.start_datetime == event.start_datetime, Event.id != event_id).first()
    if is_any_other_event:
        return ResponseSchema(status=False, details="Event with same name and start time already exists")
    for key, value in event.model_dump().items():
        if value is not None:
            setattr(existing_event, key, value)
    existing_event.updated_by = curr_user.user_id
    db.commit()
    
    return ResponseSchema(status=True, details="Event updated successfully")

@event_router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db), curr_user: CurUser = Depends(adminAuthenticate)):
    existing_event = db.query(Event).filter(Event.id == event_id)
    if not existing_event.first():
        return ResponseSchema(status=False, details="Event not found")
    existing_event.delete(synchronize_session=False)
    db.commit()
    
    return ResponseSchema(status=True, details="Event deleted successfully")

# Registered Events
@event_router.get("/rsvp/{event_id}")
def read_rsvp(event_id: int, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    existing_event = db.query(Event).get(event_id)
    if existing_event is None:
        return ResponseSchema(status=False, details="Event not found")
    # check if user already registered for this event
    existing_rsvp = db.query(EventRSVP).filter(EventRSVP.event_id == event_id, EventRSVP.user_id == curr_user.user_id).first()
    if not existing_rsvp:
        return ResponseSchema(status=False, details="You have not registered for this event")
    
    return ResponseSchema(status=True, details="RSVP fetched successfully", data=existing_rsvp)

# Register RSVP
@event_router.post("/rsvp/{event_id}")
def register_rsvp(event_id: int, status: RSVPStatusEnum,  db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    existing_event = db.query(Event).get(event_id)
    if existing_event is None:
        return ResponseSchema(status=False, details="Event not found")
    # check if user already registered for this event
    existing_rsvp = db.query(EventRSVP).filter(EventRSVP.event_id == event_id, EventRSVP.user_id == curr_user.user_id).first()
    if existing_rsvp:
        return ResponseSchema(status=False, details="You have already registered for this event")
    rsvp = EventRSVP(user_id=curr_user.user_id, event_id=event_id, status=status, created_at=datetime.now(timezone.utc), status_updated_at=datetime.now(timezone.utc))
    db.add(rsvp)
    db.commit()
    db.refresh(rsvp)
    return ResponseSchema(status=True, details="RSVP registered successfully", data=rsvp)

# update RSVP status
@event_router.put("/rsvp/{event_id}")
def update_rsvp(event_id: int, status: RSVPStatusEnum, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    existing_event = db.query(Event).get(event_id)
    if existing_event is None:
        return ResponseSchema(status=False, details="Event not found")
    # check if user already registered for this event
    existing_rsvp = db.query(EventRSVP).filter(EventRSVP.event_id == event_id, EventRSVP.user_id == curr_user.user_id).first()
    if existing_rsvp is None:
        return ResponseSchema(status=False, details="You have not registered for this event")
    existing_rsvp.status = status
    existing_rsvp.status_updated_at = datetime.now(timezone.utc)
    db.commit()
    
    return ResponseSchema(status=True, details="RSVP updated successfully")

# delete RSVP
@event_router.delete("/rsvp/{event_id}")
def delete_rsvp(event_id: int, db: Session = Depends(get_db), curr_user: CurUser = Depends(authenticate)):
    existing_event = db.query(Event).get(event_id)
    if existing_event is None:
        return ResponseSchema(status=False, details="Event not found")
    # check if user already registered for this event
    existing_rsvp = db.query(EventRSVP).filter(EventRSVP.event_id == event_id, EventRSVP.user_id == curr_user.user_id)
    if not existing_rsvp.first():
        return ResponseSchema(status=False, details="You have not registered for this event")
    existing_rsvp.delete(synchronize_session=False)
    db.commit()
    
    return ResponseSchema(status=True, details="RSVP deleted successfully")

