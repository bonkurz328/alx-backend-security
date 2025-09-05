from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited

@require_http_methods(["GET", "POST"])
@ratelimit(key='ip', rate='5/m', method=['GET', 'POST'], block=True)
def sensitive_view(request):
    """
    A sensitive view that should be rate limited
    """
    if request.method == 'POST':
        # Simulate login processing
        return JsonResponse({
            'status': 'success', 
            'message': 'Request processed successfully',
            'ip': request.META.get('REMOTE_ADDR')
        })
    
    return JsonResponse({
        'status': 'info',
        'message': 'This is a sensitive endpoint. Please be gentle with your requests.',
        'rate_limit': '5 requests per minute for anonymous users'
    })

@require_http_methods(["GET", "POST"])
@ratelimit(key='user', rate='10/m', method=['GET', 'POST'], block=True)
def authenticated_sensitive_view(request):
    """
    A sensitive view for authenticated users with higher rate limit
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error',
            'message': 'Authentication required'
        }, status=401)
    
    if request.method == 'POST':
        # Simulate sensitive operation for authenticated users
        return JsonResponse({
            'status': 'success', 
            'message': 'Authenticated request processed successfully',
            'user': request.user.username,
            'ip': request.META.get('REMOTE_ADDR')
        })
    
    return JsonResponse({
        'status': 'info',
        'message': 'This is a sensitive endpoint for authenticated users.',
        'rate_limit': '10 requests per minute for authenticated users',
        'user': request.user.username
    })

def rate_limit_exceeded(request, exception):
    """
    Custom view for when rate limit is exceeded
    """
    if isinstance(exception, Ratelimited):
        return JsonResponse({
            'status': 'error',
            'message': 'Rate limit exceeded. Please try again later.',
            'retry_after': getattr(exception, 'retry_after', None),
            'limit': getattr(exception, 'limit', None),
            'timeframe': getattr(exception, 'timeframe', None)
        }, status=429)
    
    return JsonResponse({
        'status': 'error',
        'message': 'An error occurred'
    }, status=500)
    