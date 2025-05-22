from sqlalchemy import Column, Integer, String, Enum as SqlEnum, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship, backref
import enum
from .users import Base, BaseModel

class CategoryTypeEnum(enum.Enum):
    SERVICE = "SERVICE"
    ISSUE = "ISSUE"
    HELP = "HELP"
    BOTH = "BOTH"

category_type_sql_enum = SqlEnum(CategoryTypeEnum, name="category_type")

class ServiceStatusEnum(enum.Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"

service_status_sql_enum = SqlEnum(ServiceStatusEnum, name="service_status")

class RSVPStatusEnum(enum.Enum):
    YES = "YES"
    NO = "NO"
    MAYBE = "MAYBE"

RSVP_status_sql_enum = SqlEnum(RSVPStatusEnum, name="rsvp_status")

class HelpRequestStatusEnum(enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"

help_request_status_sql_enum = SqlEnum(HelpRequestStatusEnum, name="help_request_status")

class ReminderTypeEnum(enum.Enum):
    _30_MIN = "30_MIN"
    _1_HR = "1_HR"
    _2_HR = "2_HR"
    _1_DAY = "1_DAY"

reminder_type_sql_enum = SqlEnum(ReminderTypeEnum, name="reminder_type")

class Category(BaseModel):
    __tablename__ = "tbl_category"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, nullable=False, index=True)
    type = Column(category_type_sql_enum, nullable=False)
    available = Column(Boolean, nullable=False)
class Service(BaseModel):
    __tablename__ = "tbl_service"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    category_id = Column(Integer, ForeignKey("tbl_category.id", name="tbl_service_category_id_fkey", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    status= Column(service_status_sql_enum, nullable=True)
    requested_user_id = Column(Integer, ForeignKey("tbl_user.id", name="tbl_service_requested_user_id_fkey"), nullable=False)

    category = relationship("Category", backref=backref("services", uselist=False))

class Event(BaseModel):
    __tablename__ = "tbl_event"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    all_day = Column(Boolean, nullable=True)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=True)
    location = Column(String, nullable=False)
    max_participants = Column(Integer, nullable=True)


class EventRSVP(Base):
    __tablename__ = "tbl_event_rsvp"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("tbl_user.id", name="tbl_event_rsvp_user_id_fkey", ondelete="CASCADE"), nullable=False)
    event_id = Column(Integer, ForeignKey("tbl_event.id", name="tbl_event_rsvp_event_id_fkey", ondelete="CASCADE"), nullable=False)
    status = Column(RSVP_status_sql_enum, nullable=False)
    created_at = Column(DateTime, nullable=False)
    status_updated_at = Column(DateTime, nullable=True)

    event = relationship("Event", backref="rsvp", foreign_keys=[event_id])
    user = relationship("User", backref="event_rsvps", foreign_keys=[user_id])

class HelpRequest(Base):
    __tablename__ = "tbl_help_request"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("tbl_user.id", name="tbl_help_request_user_id_fkey", ondelete="CASCADE"), nullable=False)
    assigned_staff_id = Column(Integer, ForeignKey("tbl_user.id", name="tbl_help_request_assigned_staff_id_fkey", ondelete="SET NULL"), nullable=True)
    category_id = Column(Integer, ForeignKey("tbl_category.id", name="tbl_help_request_category_id_fkey", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(help_request_status_sql_enum, nullable=False)
    created_at = Column(DateTime, nullable=False)
    request_closed_at = Column(DateTime, nullable=True)

class Notification(Base):
    __tablename__ = "tbl_notification"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("tbl_user.id", name="tbl_notification_user_id_fkey", ondelete="CASCADE"), nullable=True)  # Null = broadcast
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    language = Column(String, nullable=True)
    sent_at = Column(DateTime, nullable=False)
class NotificationReminder(Base):
    __tablename__ = "tbl_notification_reminder"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    event_id = Column(Integer, ForeignKey("tbl_event.id", name="tbl_notification_reminder_event_id_fkey", ondelete="CASCADE"), nullable=False)
    reminder_type = Column(reminder_type_sql_enum, nullable=False)
    message = Column(Text, nullable=False)
    sent_status = Column(Boolean, nullable=False, default=False)
    scheduled_time = Column(DateTime, nullable=False)

class MeetingLog(Base):
    __tablename__ = "tbl_meeting_log"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("tbl_user.id", name="tbl_meeting_log_user_id_fkey", ondelete="CASCADE"), nullable=False)
    admin_id = Column(Integer, ForeignKey("tbl_user.id", name="tbl_meeting_log_admin_id_fkey", ondelete="CASCADE"), nullable=False)
    notes = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
