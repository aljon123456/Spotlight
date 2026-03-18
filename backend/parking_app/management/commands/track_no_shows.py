"""
Management command to detect and track no-show incidents.
Run after release_expired_assignments to identify users who didn't show up.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from parking_app.models import Assignment, NoShowTracking, Notification


class Command(BaseCommand):
    help = 'Detect and track no-show parking assignments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--grace-period',
            type=int,
            default=0,
            help='Grace period in minutes after assignment end time (default: 0)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Print detailed information about detected no-shows'
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        grace_period = options.get('grace_period', 0)
        now = timezone.now()
        grace_datetime = now - timedelta(minutes=grace_period)
        
        # Find completed assignments that were auto-released
        # (indicates user didn't manually complete them)
        expired_completed = Assignment.objects.filter(
            status='completed',
            end_datetime__lt=grace_datetime,
            updated_at__gte=timezone.now() - timedelta(hours=1)  # Recently completed
        ).exclude(
            # Exclude if already tracked
            no_show_record__isnull=False
        )
        
        no_show_count = 0
        
        for assignment in expired_completed:
            try:
                # Create no-show record
                no_show = NoShowTracking.objects.create(
                    user=assignment.user,
                    assignment=assignment,
                    was_notified=False
                )
                
                # Get user's no-show count
                total_no_shows = NoShowTracking.objects.filter(
                    user=assignment.user
                ).count()
                
                # Create notification
                Notification.objects.create(
                    user=assignment.user,
                    title='No-Show Recorded',
                    message=(
                        f'You did not show up for your parking assignment '
                        f'for {assignment.schedule.title}. '
                        f'This is your {total_no_shows} no-show incident. '
                        f'Repeated no-shows may affect your parking privileges.'
                    ),
                    notification_type='alert',
                    priority='high' if total_no_shows >= 3 else 'medium',
                    related_assignment=assignment
                )
                
                # Update tracking
                no_show.was_notified = True
                no_show.save()
                
                no_show_count += 1
                
                if verbose:
                    self.stdout.write(
                        f'✓ Recorded no-show for {assignment.user.username} '
                        f'(Total no-shows: {total_no_shows})'
                    )
                
                # Warn if too many no-shows
                if total_no_shows >= 5:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ {assignment.user.username} has {total_no_shows} no-shows '
                            f'- Consider action'
                        )
                    )
                    
            except Exception as e:
                self.stderr.write(
                    f'✗ Error tracking no-show for assignment {assignment.id}: {str(e)}'
                )
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully tracked {no_show_count} no-show incidents'
            )
        )
