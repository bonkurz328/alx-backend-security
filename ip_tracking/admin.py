from django.contrib import admin
from .models import RequestLog, BlockedIP

@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'path', 'timestamp')
    list_filter = ('timestamp', 'path')
    search_fields = ('ip_address', 'path')
    readonly_fields = ('ip_address', 'path', 'timestamp')

@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'created_at', 'reason')
    list_filter = ('created_at',)
    search_fields = ('ip_address', 'reason')
    readonly_fields = ('created_at',)
    