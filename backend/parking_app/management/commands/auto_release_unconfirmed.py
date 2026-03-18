"""
Management command to auto-release parking slots after 30-minute grace period.
Runs every minute to check for expired confirmation deadlines.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from parking_app.models import Assignment, Notification, NoShowTracking


class Command(BaseCommand):
    help = 'Auto-release parking slots if confirmation deadline expires (30-minute grace period)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Print detailed information about released assignments'
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        now = timezone.now()
        
        # Find all active, unconfirmed assignments past their deadline
        expired_assignments = Assignment.objects.filter(
            status='active',
            is_confirmed=False,
            confirmation_deadline__lt=now
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
                
                # Mark assignment as no-show
                assignment.status = 'no_show'
                assignment.save()
                
                # Record no-show
                NoShowTracking.objects.create(
                    user=assignment.user,
                    assignment=assignment,
                    was_notified=False,
                    reason='Did not confirm arrival within 30-minute grace period'
                )
                
                # Get total no-shows for this user
                total_no_shows = NoShowTracking.objects.filter(
                    user=assignment.user
                ).count()
                
                # Create notification
                priority = 'high' if total_no_shows >= 3 else 'medium'
                
                Notification.objects.create(
                    user=assignment.user,
                    title='Parking Slot Auto-Released (No Confirmation)',
                    message=(
                        f'You did not confirm your arrival within the 30-minute grace period '
                        f'for {assignment.schedule.title}. '
                        f'Your parking slot ({assignment.parking_slot.slot_number}) has been released. '
                        f'This is your {total_no_shows} no-show incident. '
                        f'Repeated no-shows may affect your parking privileges.'
                    ),
                    notification_type='alert',
                    priority=priority,
                    related_assignment=assignment
                )
                
                released_count += 1
                
                if verbose:
                    self.stdout.write(
                        f'✓ Auto-released no-show for {assignment.user.username} '
                        f'(Schedule: {assignment.schedule.title}, '
                        f'Total no-shows: {total_no_shows})'
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
                    f'✗ Error processing assignment {assignment.id}: {str(e)}'
                )
        
        # Summary
        if released_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Successfully auto-released {released_count} expired assignments'
                )
            )
        else:
            if verbose:
                self.stdout.write(
                    self.style.SUCCESS(
                        '\n✓ No expired assignments to release'
                    )
                )
