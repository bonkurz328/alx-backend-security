from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from .models import RequestLog, SuspiciousIP

@shared_task
def detect_suspicious_ips():
    """
    Celery task to detect suspicious IPs hourly.
    Flags IPs exceeding 100 requests/hour or accessing sensitive paths.
    """
    one_hour_ago = timezone.now() - timedelta(hours=1)
    
    # Detect IPs with excessive requests (more than 100 requests/hour)
    excessive_requests_ips = detect_excessive_requests(one_hour_ago)
    
    # Detect IPs accessing sensitive paths
    sensitive_access_ips = detect_sensitive_access(one_hour_ago)
    
    return {
        'excessive_requests_detected': len(excessive_requests_ips),
        'sensitive_access_detected': len(sensitive_access_ips)
    }

def detect_excessive_requests(one_hour_ago):
    """
    Detect IPs making more than 100 requests in the last hour
    """
    # Get IPs with request counts exceeding threshold
    ip_counts = (
        RequestLog.objects
        .filter(timestamp__gte=one_hour_ago)
        .values('ip_address')
        .annotate(request_count=Count('id'))
        .filter(request_count__gt=100)
    )
    
    detected_ips = []
    for ip_data in ip_counts:
        ip_address = ip_data['ip_address']
        request_count = ip_data['request_count']
        reason = f"Excessive requests: {request_count} requests in the last hour"
        
        # Create or update SuspiciousIP record
        suspicious_ip, created = SuspiciousIP.objects.get_or_create(
            ip_address=ip_address,
            defaults={'reason': reason}
        )
        
        if not created:
            suspicious_ip.reason = reason
            suspicious_ip.update_detection_time()
        
        detected_ips.append(ip_address)
    
    return detected_ips

def detect_sensitive_access(one_hour_ago):
    """
    Detect IPs accessing sensitive paths (/admin, /login) in the last hour
    """
    sensitive_paths = ['/admin', '/login', '/admin/', '/login/']
    
    # Get unique IPs that accessed sensitive paths
    sensitive_access_ips = (
        RequestLog.objects
        .filter(
            timestamp__gte=one_hour_ago,
            path__in=sensitive_paths
        )
        .values('ip_address')
        .distinct()
    )
    
    detected_ips = []
    for ip_data in sensitive_access_ips:
        ip_address = ip_data['ip_address']
        reason = "Accessed sensitive path (/admin or /login)"
        
        # Create or update SuspiciousIP record
        suspicious_ip, created = SuspiciousIP.objects.get_or_create(
            ip_address=ip_address,
            defaults={'reason': reason}
        )
        
        if not created:
            suspicious_ip.reason = reason
            suspicious_ip.update_detection_time()
        
        detected_ips.append(ip_address)
    
    return detected_ips
    