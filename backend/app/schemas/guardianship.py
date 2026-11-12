from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class GuardianshipBase(BaseModel):
    relationship_type: str
    can_view_history: Optional[bool] = False
    can_manage_medications: Optional[bool] = False


class GuardianshipCreate(GuardianshipBase):
    """طلب وصاية: الصلاحيات هنا مجرد 'طلب' ولا تعمل إلا بعد الموافقة."""
    dependent_patient_id: int


class GuardianshipUpdate(BaseModel):
    """
    الوصي يعدّل relationship_type فقط.
    المريض (الموصى عليه) يعدّل can_view_history / can_manage_medications فقط.
    أي حقل غير مسموح للطرف يتم تجاهله، ولا يمكن تغيير status من هنا.
    """
    relationship_type: Optional[str] = None
    can_view_history: Optional[bool] = None
    can_manage_medications: Optional[bool] = None


class GuardianshipApprove(BaseModel):
    """عند الموافقة يمكن للمريض تحديد الصلاحيات (افتراضياً ما طلبه الوصي)."""
    can_view_history: Optional[bool] = None
    can_manage_medications: Optional[bool] = None


class GuardianshipResponse(GuardianshipBase):
    guardianship_id: int
    guardian_user_id: int
    dependent_patient_id: int
    status: str
    granted_at_utc: Optional[datetime] = None
    ended_at_utc: Optional[datetime] = None

    class Config:
        from_attributes = True
