from django.core.management.base import BaseCommand, CommandError
from propylon_document_manager.users.models import User
from django.contrib.auth.hashers import make_password

users = [
    'bill',
    'steve'
]

class Command(BaseCommand):
    help = "Load basic file version fixtures"

    def handle(self, *args, **options):
        for user in users:
            User.objects.create(
                name=user,
                email="{}@example.com".format(user),
                password=make_password('password'),
                is_staff=True,
            )

        self.stdout.write(
            self.style.SUCCESS('Successfully created %s file versions' % len(users))
        )
