import socket
from django.conf import settings
from .models import RequestLog

class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Get the client IP address
        ip_address = self.get_client_ip(request)
        
        # Process the request
        response = self.get_response(request)
        
        # Log the request after processing
        self.log_request(ip_address, request.path)
        
        return response
    
    def get_client_ip(self, request):
        """
        Get the client's real IP address, handling proxy headers
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Validate IP format
        try:
            if ':' in ip:  # IPv6
                socket.inet_pton(socket.AF_INET6, ip)
            else:  # IPv4
                socket.inet_pton(socket.AF_INET, ip)
            return ip
        except (socket.error, OSError):
            return request.META.get('REMOTE_ADDR', '0.0.0.0')
    
    def log_request(self, ip_address, path):
        """
        Log the request to the database
        """
        try:
            RequestLog.objects.create(
                ip_address=ip_address,
                path=path
            )
        except Exception as e:
            if settings.DEBUG:
                print(f"Error logging request: {e}")
