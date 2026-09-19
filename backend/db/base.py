# Import all models here so that Base has them before being
# imported by Alembic
from backend.db.base_class import Base  # noqa
from backend.models.orm import User  # noqa
from backend.models.orm import Threat  # noqa
from backend.models.orm import Evidence, FIR  # noqa
from backend.models.orm import AuditLog  # noqa
from backend.models.orm import Blacklist  # noqa
from backend.models.orm import UserConsent, DeviceInfo, PhoneLookup  # noqa
from backend.models.orm import SpamReport, SpamFilter, SpamLog  # noqa
from backend.models.orm import ChildProfile, ChildActivityLog  # noqa
from backend.models.orm import CanaryTrap  # noqa
from backend.models.orm import HoneypotSession  # noqa
