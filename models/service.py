from sqlalchemy import Column, Integer, String, Enum as SqlEnum, ForeignKey, Text, Boolean, DateTime
import enum
from .users import Base, BaseModel

class CategoryTypeEnum(enum.Enum):
    SERVICE = "Service"
    ISSUE = "Issue"
    BOTH = "Both"

class Category(BaseModel):
    __tablename__ = "tbl_category"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, nullable=False, index=True)
    type = Column(SqlEnum(CategoryTypeEnum, name="category_type"), nullable=False)

class Service(BaseModel):
    __tablename__ = "tbl_service"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("tbl_category.id"), nullable=False, index=True)
    description = Column(Text, nullable=True)
    available = Column(Boolean, nullable=False)

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

class RSVPStatusEnum(enum.Enum):
    YES = "Yes"
    NO = "No"
    MAYBE = "Maybe"

class EventRSVP(Base):
    __tablename__ = "tbl_event_rsvp"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("tbl_user.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("tbl_event.id"), nullable=False)
    status = Column(SqlEnum(RSVPStatusEnum, name="rsvp_status"), nullable=False)
    created_at = Column(DateTime, nullable=False)
    status_updated_at = Column(DateTime, nullable=True)

class HelpRequestStatusEnum(enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    CLOSED = "Closed"

class HelpRequest(Base):
    __tablename__ = "tbl_help_request"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("tbl_user.id"), nullable=False)
    assigned_staff_id = Column(Integer, ForeignKey("tbl_user.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("tbl_category.id"), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SqlEnum(HelpRequestStatusEnum, name="help_request_status"), nullable=False)
    created_at = Column(DateTime, nullable=False)
    request_closed_at = Column(DateTime, nullable=True)

class Notification(Base):
    __tablename__ = "tbl_notification"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("tbl_user.id"), nullable=True)  # Null = broadcast
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    language = Column(String, nullable=True)
    sent_at = Column(DateTime, nullable=False)

class ReminderTypeEnum(enum.Enum):
    _30_MIN = "30_min"
    _1_HR = "1_hr"
    _2_HR = "2_hr"
    _1_DAY = "1_day"

class NotificationReminder(Base):
    __tablename__ = "tbl_notification_reminder"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    event_id = Column(Integer, ForeignKey("tbl_event.id"), nullable=False)
    reminder_type = Column(SqlEnum(ReminderTypeEnum, name="reminder_type"), nullable=False)
    message = Column(Text, nullable=False)
    sent_status = Column(Boolean, nullable=False, default=False)
    scheduled_time = Column(DateTime, nullable=False)

class MeetingLog(Base):
    __tablename__ = "tbl_meeting_log"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("tbl_user.id"), nullable=False)
    admin_id = Column(Integer, ForeignKey("tbl_user.id"), nullable=False)
    notes = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
