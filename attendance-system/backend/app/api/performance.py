from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.performance_metrics import PerformanceMetrics
from typing import Optional

router = APIRouter()


@router.get("/metrics")
def get_performance_metrics(
    session_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get comprehensive performance metrics for the attendance system"""
    try:
        metrics_service = PerformanceMetrics(db)
        report = metrics_service.generate_performance_report(session_id)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/biometric")
def get_biometric_metrics(
    session_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get biometric performance metrics (FAR, FRR, EER)"""
    try:
        metrics_service = PerformanceMetrics(db)
        return metrics_service.calculate_biometric_metrics(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/efficiency")
def get_system_efficiency(
    session_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get system efficiency metrics (GPS accuracy, latency)"""
    try:
        metrics_service = PerformanceMetrics(db)
        return metrics_service.calculate_system_efficiency(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/security")
def get_security_analysis(
    session_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get security robustness analysis"""
    try:
        metrics_service = PerformanceMetrics(db)
        return metrics_service.get_security_analysis(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))