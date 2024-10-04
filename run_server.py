import os
import sys

# Include your Django project's path
sys.path.append(os.path.join(os.path.dirname(__file__), 'path_to_your_project'))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'election.settings')

# Import Django's execute_from_command_line
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    execute_from_command_line(sys.argv)
