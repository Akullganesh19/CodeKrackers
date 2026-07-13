# Import all models here so that Base has them before being
# imported by Alembic
from backend.db.base_class import Base  # noqa
from backend.models.user import User  # noqa
from backend.models.threat import Threat  # noqa
from backend.models.legal import Evidence, FIR  # noqa
from backend.models.audit import AuditLog  # noqa
from backend.models.blacklist import BlacklistEntry, ThreatIntelFeed  # noqa
from backend.models.intel import UserConsent, DeviceInfo, PhoneLookup  # noqa
from backend.models.spam import SpamReport, SpamFilter, SpamLog  # noqa
from backend.models.childlock import ChildProfile, ChildActivityLog  # noqa
from backend.models.canary import CanaryToken  # noqa
from backend.models.honeypot import HoneypotAccess  # noqa
