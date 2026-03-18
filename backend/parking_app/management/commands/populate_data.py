"""
Management command to populate sample campus and building data.
Usage: python manage.py populate_data
"""
from django.core.management.base import BaseCommand
from parking_app.models import Campus, Building, ParkingLot, ParkingSlot


class Command(BaseCommand):
    help = 'Populate the database with sample campus and building data'

    def handle(self, *args, **options):
        # Create Holy Angel University Campus
        campus, created = Campus.objects.get_or_create(
            name='Holy Angel University',
            defaults={
                'location': 'Angeles City, Pampanga, Philippines',
                'city': 'Angeles City',
                'state': 'Pampanga',
                'zip_code': '2000',
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created campus: {campus.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Campus already exists: {campus.name}')
            )

        # Define buildings for Holy Angel University
        buildings_data = [
            {
                'name': 'Main Academic Building',
                'building_code': 'MAB',
                'description': 'Primary academic and administrative building'
            },
            {
                'name': 'Engineering Building',
                'building_code': 'ENG',
                'description': 'Engineering and technology programs'
            },
            {
                'name': 'Science Building',
                'building_code': 'SCI',
                'description': 'Sciences and laboratory facilities'
            },
            {
                'name': 'College of Business',
                'building_code': 'COB',
                'description': 'Business administration and economics'
            },
            {
                'name': 'Student Center',
                'building_code': 'SC',
                'description': 'Student activities and services'
            },
            {
                'name': 'Library Building',
                'building_code': 'LIB',
                'description': 'Main library and research center'
            },
        ]

        # Create buildings
        for building_info in buildings_data:
            building, created = Building.objects.get_or_create(
                campus=campus,
                code=building_info['building_code'],
                defaults={
                    'name': building_info['name'],
                    'description': building_info['description'],
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Created building: {building.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  Building already exists: {building.name}')
                )

        # Create parking lots
        self.stdout.write('\nCreating parking lots...')
        parking_lots_data = [
            {
                'name': 'Main Parking Garage',
                'surface_type': 'garage',
                'total_slots': 150,
                'building_code': 'MAB',
            },
            {
                'name': 'North Covered Parking',
                'surface_type': 'covered',
                'total_slots': 75,
                'building_code': 'ENG',
            },
            {
                'name': 'South Outdoor Parking',
                'surface_type': 'outdoor',
                'total_slots': 100,
                'building_code': 'SCI',
            },
            {
                'name': 'Student Lot A',
                'surface_type': 'outdoor',
                'total_slots': 60,
                'building_code': 'SC',
            },
            {
                'name': 'Staff Parking',
                'surface_type': 'covered',
                'total_slots': 40,
                'building_code': 'COB',
            },
        ]

        for lot_info in parking_lots_data:
            # Get the nearest building
            building = Building.objects.filter(
                campus=campus,
                code=lot_info['building_code']
            ).first()

            parking_lot, created = ParkingLot.objects.get_or_create(
                campus=campus,
                name=lot_info['name'],
                defaults={
                    'surface_type': lot_info['surface_type'],
                    'total_slots': lot_info['total_slots'],
                    'available_slots': lot_info['total_slots'],
                    'nearest_building': building,
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Created parking lot: {parking_lot.name} ({lot_info["total_slots"]} slots)')
                )

                # Create individual parking slots
                for i in range(lot_info['total_slots']):
                    slot_type = 'handicap' if i < 3 else 'premium' if i < 8 else 'regular'
                    slot_number = f"{lot_info['name'][:3].upper()}-{i+1:03d}"

                    ParkingSlot.objects.get_or_create(
                        parking_lot=parking_lot,
                        slot_number=slot_number,
                        defaults={
                            'slot_type': slot_type,
                            'status': 'available',
                        }
                    )
                self.stdout.write(f'    ✓ Created {lot_info["total_slots"]} parking slots')
            else:
                self.stdout.write(
                    self.style.WARNING(f'  Parking lot already exists: {parking_lot.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('\n✓ Data population completed successfully!')
        )
        self.stdout.write(
            self.style.SUCCESS('You can now create schedules and assign parking.')
        )
