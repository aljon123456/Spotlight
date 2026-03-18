"""
Management command to auto-release expired parking assignments.
Run periodically (via cron or Celery) to handle no-shows and expired assignments.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from parking_app.models import Assignment, Notification
from django.db.models import Q


class Command(BaseCommand):
    help = 'Release expired parking assignments and mark them as completed'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Print detailed information about released assignments'
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        now = timezone.now()
        
        # Find all active assignments that have passed their end time
        expired_assignments = Assignment.objects.filter(
            status='active',
            end_datetime__lt=now
        )
        
        released_count = 0
        
        for assignment in expired_assignments:
            try:
                # Release the parking slot
                if assignment.parking_slot:
                    assignment.parking_slot.status = 'available'
                    assignment.parking_slot.save()
                    
                    if verbose:
                        self.stdout.write(
                            f'✓ Released slot {assignment.parking_slot.slot_number} '
                            f'from lot {assignment.parking_slot.parking_lot.name}'
                        )
                
                # Mark assignment as completed
                assignment.status = 'completed'
                assignment.save()
                
                # Create notification for user
                Notification.objects.create(
                    user=assignment.user,
                    title='Parking Assignment Completed',
                    message=(
                        f'Your parking assignment for {assignment.schedule.title} '
                        f'has been completed and the slot has been released.'
                    ),
                    notification_type='change',
                    priority='medium',
                    related_assignment=assignment
                )
                
                released_count += 1
                
                if verbose:
                    self.stdout.write(
                        f'✓ Completed assignment for {assignment.user.username} '
                        f'(Schedule: {assignment.schedule.title})'
                    )
                    
            except Exception as e:
                self.stderr.write(
                    f'✗ Error processing assignment {assignment.id}: {str(e)}'
                )
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully released {released_count} expired assignments'
            )
        )
