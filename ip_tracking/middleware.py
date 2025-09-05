import socket
from django.conf import settings
from django.http import HttpResponseForbidden
from .models import RequestLog, BlockedIP
from .geolocation import geolocation_service

class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Get the client IP address
        ip_address = self.get_client_ip(request)
        
        # Check if IP is blocked before processing the request
        if self.is_ip_blocked(ip_address):
            return HttpResponseForbidden("IP address blocked")
        
        # Process the request
        response = self.get_response(request)
        
        # Log the request after processing (with geolocation)
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
    
    def is_ip_blocked(self, ip_address):
        """
        Check if the IP address is in the blocklist
        """
        return BlockedIP.objects.filter(ip_address=ip_address).exists()
    
    def log_request(self, ip_address, path):
        """
        Log the request to the database with geolocation data
        """
        try:
            # Get geolocation data
            geolocation_data = geolocation_service.get_geolocation(ip_address)
            
            # Extract location information
            country = None
            city = None
            region = None
            
            if geolocation_data and not geolocation_data.get('error'):
                country = geolocation_data.get('country')
                city = geolocation_data.get('city')
                region = geolocation_data.get('region')
            
            RequestLog.objects.create(
                ip_address=ip_address,
                path=path,
                country=country,
                city=city,
                region=region
            )
        except Exception as e:
            if settings.DEBUG:
                print(f"Error logging request: {e}")
                