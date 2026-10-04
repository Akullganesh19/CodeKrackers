import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .tasks import (
    record_daily_safety_scores,
    restore_user_safety_scores,
    verify_all_evidence_chains,
)

logger = logging.getLogger(__name__)

# Initialize the AsyncIOScheduler which works natively with FastAPI's event loop
scheduler = AsyncIOScheduler()


def setup_scheduler():
    """
    Configures the scheduler to run forensic audits.
    The integrity check is scheduled for 00:00 (midnight) daily.
    """
    scheduler.add_job(
        verify_all_evidence_chains,
        CronTrigger(hour=0, minute=0),
        id="daily_integrity_audit",
        replace_existing=True,
        misfire_grace_time=3600,  # Allow the job to run up to an hour late if the server was down
    )

    scheduler.add_job(
        record_daily_safety_scores,
        CronTrigger(hour=23, minute=59),  # Run just before midnight
        id="daily_score_snapshot",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    scheduler.add_job(
        restore_user_safety_scores,
        CronTrigger(hour=1, minute=0),  # Run at 1 AM daily
        id="daily_score_restoration",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    scheduler.start()
    logger.info("VSDP Scheduler started: Daily integrity audit scheduled for midnight.")
