from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admin_users.admin_id"), nullable=False, index=True)
    action = Column(String, nullable=False, index=True)  # update_status, create_admin, delete_admin
    resource_type = Column(String, nullable=False)  # application, admin_user
    resource_id = Column(Integer, nullable=False)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    admin_user = relationship("AdminUser", back_populates="audit_logs")
