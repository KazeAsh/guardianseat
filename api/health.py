from fastapi import APIRouter, HTTPException
from datetime import datetime
import psutil
import os

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """Comprehensive health check endpoint for CI/CD and monitoring"""
    try:
        # Basic system checks
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Application-specific checks
        data_dirs = [
            'data/raw/mmwave',
            'data/processed', 
            'outputs/visualizations'
        ]
        
        directory_status = {}
        for dir_path in data_dirs:
            directory_status[dir_path] = os.path.exists(dir_path)
        
        health_status = {
            "status": "healthy",
            "service": "GuardianSensor API",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "uptime_seconds": psutil.boot_time()
            },
            "directories": directory_status,
            "environment": os.getenv('ENVIRONMENT', 'development')
        }
        
        # Add warning if disk space is low
        if disk.percent > 90:
            health_status["status"] = "degraded"
            health_status["warning"] = "Low disk space"
        
        return health_status
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@router.get("/health/ready")
async def readiness_probe():
    """Kubernetes readiness probe endpoint"""
    # Check if application is ready to receive traffic
    # Add your readiness checks here (database connections, etc.)
    return {"status": "ready"}

@router.get("/health/live")
async def liveness_probe():
    """Kubernetes liveness probe endpoint"""
    # Simple check if application is running
    return {"status": "alive"}