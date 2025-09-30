"""
Analytics endpoints
"""

from fastapi import APIRouter
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_metrics(tenant_id: str, days: int = 7):
    """Get dashboard metrics"""
    return {
        "period": f"Last {days} days",
        "metrics": {
            "total_conversations": 1247,
            "active_conversations": 127,
            "sla_compliance": 94.2,
            "avg_response_time_seconds": 1.8,
            "customer_satisfaction": 4.7,
            "resolution_rate": 95.3
        },
        "trends": {
            "conversations": [120, 145, 132, 156, 142, 138, 127],
            "satisfaction": [4.5, 4.6, 4.7, 4.7, 4.8, 4.7, 4.7]
        },
        "channel_distribution": {
            "whatsapp": 45,
            "email": 30,
            "slack": 25
        }
    }