import requests
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import IPGeolocationCache

class GeolocationService:
    def __init__(self):
        self.api_key = getattr(settings, 'IPINFO_API_KEY', None)
        self.base_url = "https://ipinfo.io"
    
    def get_geolocation(self, ip_address):
        """
        Get geolocation data for an IP address with caching
        """
        # Check cache first
        cached_data = self._get_cached_geolocation(ip_address)
        if cached_data:
            return cached_data
        
        # If not cached, fetch from API
        geolocation_data = self._fetch_from_api(ip_address)
        
        # Cache the result
        if geolocation_data and not geolocation_data.get('error'):
            self._cache_geolocation(ip_address, geolocation_data)
        
        return geolocation_data
    
    def _get_cached_geolocation(self, ip_address):
        """
        Get cached geolocation data if it exists and is not expired
        """
        try:
            cache_entry = IPGeolocationCache.objects.get(
                ip_address=ip_address,
                expires_at__gt=timezone.now()
            )
            return {
                'ip': ip_address,
                'country': cache_entry.country,
                'city': cache_entry.city,
                'region': cache_entry.region,
                'org': cache_entry.org,
                'postal': cache_entry.postal,
                'timezone': cache_entry.timezone,
                'cached': True
            }
        except IPGeolocationCache.DoesNotExist:
            return None
    
    def _cache_geolocation(self, ip_address, geolocation_data):
        """
        Cache geolocation data for 24 hours
        """
        try:
            IPGeolocationCache.objects.update_or_create(
                ip_address=ip_address,
                defaults={
                    'country': geolocation_data.get('country'),
                    'city': geolocation_data.get('city'),
                    'region': geolocation_data.get('region'),
                    'org': geolocation_data.get('org'),
                    'postal': geolocation_data.get('postal'),
                    'timezone': geolocation_data.get('timezone'),
                    'expires_at': timezone.now() + timedelta(hours=24)
                }
            )
        except Exception as e:
            # Log error but don't break the application
            pass
    
    def _fetch_from_api(self, ip_address):
        """
        Fetch geolocation data from ipinfo.io API
        """
        try:
            url = f"{self.base_url}/{ip_address}/json"
            if self.api_key:
                url += f"?token={self.api_key}"
            
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            return response.json()
        except requests.RequestException as e:
            return {'error': str(e)}
        except Exception as e:
            return {'error': 'Unknown error occurred'}

# Create a global instance
geolocation_service = GeolocationService()
