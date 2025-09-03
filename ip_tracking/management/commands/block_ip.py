from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from ip_tracking.models import BlockedIP
import ipaddress

class Command(BaseCommand):
    help = 'Add IP addresses to the blocklist'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'ip_addresses',
            nargs='+',
            type=str,
            help='IP addresses to block (space separated)'
        )
        parser.add_argument(
            '--reason',
            type=str,
            help='Reason for blocking the IP address(es)'
        )
    
    def handle(self, *args, **options):
        ip_addresses = options['ip_addresses']
        reason = options['reason']
        
        blocked_count = 0
        skipped_count = 0
        
        for ip_str in ip_addresses:
            try:
                # Validate IP address format
                ipaddress.ip_address(ip_str)
                
                # Create blocked IP entry
                blocked_ip, created = BlockedIP.objects.get_or_create(
                    ip_address=ip_str,
                    defaults={'reason': reason}
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully blocked IP: {ip_str}')
                    )
                    blocked_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f'IP already blocked: {ip_str}')
                    )
                    skipped_count += 1
                    
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(f'Invalid IP address format: {ip_str}')
                )
                skipped_count += 1
            except IntegrityError:
                self.stdout.write(
                    self.style.WARNING(f'IP already blocked: {ip_str}')
                )
                skipped_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error blocking IP {ip_str}: {e}')
                )
                skipped_count += 1
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nBlocking complete: {blocked_count} IPs blocked, '
                f'{skipped_count} IPs skipped'
            )
        )
        