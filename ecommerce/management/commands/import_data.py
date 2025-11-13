"""
Management command to import data from GitHub or local file.
Usage: python manage.py import_data [--url URL] [--file FILE]
"""
import os
import tempfile
import urllib.request
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Import data from GitHub URL or local file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            help='URL to download data.json from (e.g., GitHub raw URL)',
            default='https://raw.githubusercontent.com/uigeadall/marbaras123/newone/data.json'
        )
        parser.add_argument(
            '--file',
            type=str,
            help='Local file path to data.json',
        )

    def handle(self, *args, **options):
        url = options.get('url')
        file_path = options.get('file')

        if file_path:
            # Use local file
            if not os.path.exists(file_path):
                self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
                return
            
            self.stdout.write(self.style.SUCCESS(f'Importing data from local file: {file_path}'))
            call_command('loaddata', file_path)
            self.stdout.write(self.style.SUCCESS('✅ Data imported successfully!'))
            
        elif url:
            # Download from URL
            self.stdout.write(self.style.WARNING(f'Downloading data from: {url}'))
            
            try:
                # Create temporary file
                with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.json') as tmp_file:
                    tmp_path = tmp_file.name
                    
                    # Download file
                    with urllib.request.urlopen(url) as response:
                        data = response.read()
                        tmp_file.write(data)
                    
                    self.stdout.write(self.style.SUCCESS(f'✅ Downloaded {len(data)} bytes'))
                    self.stdout.write(self.style.WARNING(f'Importing data from temporary file...'))
                    
                    # Import data
                    call_command('loaddata', tmp_path)
                    
                    # Clean up
                    os.unlink(tmp_path)
                    
                    self.stdout.write(self.style.SUCCESS('✅ Data imported successfully!'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error importing data: {e}'))
                if 'tmp_path' in locals():
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
        else:
            # Try local data.json
            local_file = 'data.json'
            if os.path.exists(local_file):
                self.stdout.write(self.style.SUCCESS(f'Importing data from local file: {local_file}'))
                call_command('loaddata', local_file)
                self.stdout.write(self.style.SUCCESS('✅ Data imported successfully!'))
            else:
                self.stdout.write(self.style.ERROR('No file or URL provided, and data.json not found locally'))

