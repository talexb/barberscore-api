from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from apps.api.factories import (
    add_performers,
)

from apps.api.models import (
    Session,
)


class Command(BaseCommand):
    help = "Create sample session."

    def add_arguments(self, parser):
        parser.add_argument(
            'slug',
            type=str,
        )

        parser.add_argument(
            '--number',
            type=int,
        )

    def handle(self, *args, **options):
        try:
            session = Session.objects.get(
                slug=options['slug'],
            )
        except Session.DoesNotExist:
            raise CommandError("Session does not exist.")
        result = add_performers(session, options['number'])
        self.stdout.write("{0}".format(result))