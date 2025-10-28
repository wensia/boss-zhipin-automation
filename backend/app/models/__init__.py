"""
数据模型模块
"""
from app.models.candidate import (
    Candidate,
    CandidateCreate,
    CandidateRead,
    CandidateUpdate,
    CandidateStatus,
)
from app.models.greeting import (
    GreetingRecord,
    GreetingRecordCreate,
    GreetingRecordRead,
)
from app.models.automation_task import (
    AutomationTask,
    AutomationTaskCreate,
    AutomationTaskRead,
    AutomationTaskUpdate,
    TaskStatus,
)
from app.models.greeting_template import (
    GreetingTemplate,
    GreetingTemplateCreate,
    GreetingTemplateRead,
    GreetingTemplateUpdate,
)
from app.models.system_config import (
    SystemConfig,
    SystemConfigRead,
    SystemConfigUpdate,
)
from app.models.log_entry import (
    LogEntry,
    LogEntryCreate,
    LogEntryRead,
    LogLevel,
    LogAction,
)

__all__ = [
    # Candidate models
    "Candidate",
    "CandidateCreate",
    "CandidateRead",
    "CandidateUpdate",
    "CandidateStatus",
    # GreetingRecord models
    "GreetingRecord",
    "GreetingRecordCreate",
    "GreetingRecordRead",
    # AutomationTask models
    "AutomationTask",
    "AutomationTaskCreate",
    "AutomationTaskRead",
    "AutomationTaskUpdate",
    "TaskStatus",
    # GreetingTemplate models
    "GreetingTemplate",
    "GreetingTemplateCreate",
    "GreetingTemplateRead",
    "GreetingTemplateUpdate",
    # SystemConfig models
    "SystemConfig",
    "SystemConfigRead",
    "SystemConfigUpdate",
    # LogEntry models
    "LogEntry",
    "LogEntryCreate",
    "LogEntryRead",
    "LogLevel",
    "LogAction",
]
