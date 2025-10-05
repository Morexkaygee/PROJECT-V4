from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.attendance import Attendance
from typing import Dict, List
import statistics


class PerformanceMetrics:
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_biometric_metrics(self, session_id: int = None) -> Dict:
        """Calculate FAR, FRR, and EER for biometric performance"""
        query = self.db.query(Attendance)
        if session_id:
            query = query.filter(Attendance.session_id == session_id)
        
        attendances = query.all()
        
        # Separate authorized vs unauthorized attempts
        accepted = [a for a in attendances if a.verification_status == 'accepted']
        rejected_face = [a for a in attendances if a.verification_status == 'rejected_face']
        rejected_gps = [a for a in attendances if a.verification_status == 'rejected_gps']
        
        total_attempts = len(attendances)
        if total_attempts == 0:
            return {"FAR": 0, "FRR": 0, "EER": 0, "total_attempts": 0}
        
        # Calculate FAR (False Acceptance Rate)
        # Assuming rejected attempts were unauthorized
        unauthorized_accepted = len([a for a in rejected_face + rejected_gps if a.present])
        total_unauthorized = len(rejected_face) + len(rejected_gps)
        FAR = (unauthorized_accepted / total_unauthorized * 100) if total_unauthorized > 0 else 0
        
        # Calculate FRR (False Rejection Rate)
        # Assuming accepted attempts were authorized
        authorized_rejected = len([a for a in accepted if not a.present])
        total_authorized = len(accepted)
        FRR = (authorized_rejected / total_authorized * 100) if total_authorized > 0 else 0
        
        # EER is typically where FAR = FRR
        EER = (FAR + FRR) / 2
        
        return {
            "FAR": round(FAR, 2),
            "FRR": round(FRR, 2), 
            "EER": round(EER, 2),
            "total_attempts": total_attempts,
            "accepted": len(accepted),
            "rejected": len(rejected_face) + len(rejected_gps)
        }
    
    def calculate_system_efficiency(self, session_id: int = None) -> Dict:
        """Calculate GPS accuracy and latency metrics"""
        query = self.db.query(Attendance).filter(Attendance.gps_accuracy_meters.isnot(None))
        if session_id:
            query = query.filter(Attendance.session_id == session_id)
        
        attendances = query.all()
        
        if not attendances:
            return {"CEP": 0, "avg_latency_ms": 0, "samples": 0}
        
        # Calculate CEP (Circular Error Probability) - 50th percentile of GPS accuracy
        gps_accuracies = [a.gps_accuracy_meters for a in attendances if a.gps_accuracy_meters]
        CEP = statistics.median(gps_accuracies) if gps_accuracies else 0
        
        # Calculate average latency
        latencies = [a.processing_time_ms for a in attendances if a.processing_time_ms]
        avg_latency = statistics.mean(latencies) if latencies else 0
        
        return {
            "CEP": round(CEP, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "max_latency_ms": max(latencies) if latencies else 0,
            "min_latency_ms": min(latencies) if latencies else 0,
            "samples": len(attendances)
        }
    
    def get_security_analysis(self, session_id: int = None) -> Dict:
        """Analyze security robustness against spoofing attempts"""
        query = self.db.query(Attendance)
        if session_id:
            query = query.filter(Attendance.session_id == session_id)
        
        total = query.count()
        gps_rejected = query.filter(Attendance.verification_status == 'rejected_gps').count()
        face_rejected = query.filter(Attendance.verification_status == 'rejected_face').count()
        accepted = query.filter(Attendance.verification_status == 'accepted').count()
        
        return {
            "total_attempts": total,
            "gps_spoofing_blocked": gps_rejected,
            "face_spoofing_blocked": face_rejected,
            "successful_verifications": accepted,
            "security_effectiveness": round((gps_rejected + face_rejected) / total * 100, 2) if total > 0 else 0
        }
    
    def generate_performance_report(self, session_id: int = None) -> Dict:
        """Generate comprehensive performance report"""
        return {
            "biometric_metrics": self.calculate_biometric_metrics(session_id),
            "system_efficiency": self.calculate_system_efficiency(session_id),
            "security_analysis": self.get_security_analysis(session_id)
        }