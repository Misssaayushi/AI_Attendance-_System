from __future__ import annotations

from fastapi import APIRouter, Depends

from app.middleware.auth_deps import get_current_admin
from app.services import diagnostics_service
from app.utils import monitoring as monitoring_service
from app.utils.logger import logger
from app.utils.response import success

router = APIRouter(dependencies=[Depends(get_current_admin)])


@router.get("/readiness")
def backend_readiness():
    logger.info("event=diagnostics_readiness_request")
    data = diagnostics_service.get_backend_readiness_snapshot()
    return success(data=data, message="Backend Readiness Retrieved Successfully")


@router.get("/api-coverage")
def api_coverage_matrix():
    logger.info("event=diagnostics_api_coverage_request")
    data = diagnostics_service.get_api_coverage_matrix()
    return success(data=data, message="API Coverage Matrix Retrieved Successfully")


@router.get("/metrics")
def runtime_metrics():
    logger.info("event=diagnostics_runtime_metrics_request")
    data = monitoring_service.get_runtime_metrics()
    return success(data=data, message="Runtime Metrics Retrieved Successfully")


@router.get("/stability")
def stability_snapshot():
    logger.info("event=diagnostics_stability_snapshot_request")
    data = monitoring_service.get_stability_snapshot()
    return success(data=data, message="Stability Snapshot Retrieved Successfully")
