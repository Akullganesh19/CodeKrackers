from fastapi import APIRouter
from backend.api.v1.endpoints import (
    login,
    users,
    threats,
    legal,
    analytics,
    detection,
    honeypot,
    honeypot_traps,
    honeypot_root,
    canary,
    model_guard,
    zk_privacy,
    blacklist,
    export,
    intel,
    spam,
    childlock,
    enclave,
)

api_router = APIRouter()

api_router.include_router(login.router, tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(threats.router, prefix="/threats", tags=["threats"])
api_router.include_router(detection.router, prefix="/detect", tags=["detection"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(legal.router, prefix="/legal", tags=["legal"])
api_router.include_router(honeypot.router, prefix="/honeypot", tags=["honeypot"])
api_router.include_router(honeypot_traps.router, tags=["honeypot-traps"])
api_router.include_router(blacklist.router, prefix="/blacklist", tags=["blacklist"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(intel.router, prefix="/intel", tags=["intelligence"])
api_router.include_router(spam.router, prefix="/spam", tags=["spam-shield"])
api_router.include_router(childlock.router, prefix="/childlock", tags=["child-lock"])
api_router.include_router(canary.router, prefix="/canary", tags=["canary"])
api_router.include_router(honeypot_root.router, tags=["honeypot-root"])
api_router.include_router(model_guard.router, prefix="/models", tags=["model-security"])
api_router.include_router(zk_privacy.router, prefix="/zk", tags=["zero-knowledge-privacy"])
api_router.include_router(enclave.router, prefix="/enclave", tags=["nitro-enclaves"])
