# Standard Libary
from optparse import make_option

# Django
from django.core.management.base import (
    BaseCommand,
    CommandError,
)

# First-Party
from api.models import (
    Appearance,
    Contestant,
    Entry,
    Session,
    Song,
)


class Command(BaseCommand):
    help = "Command to denormalize names."

    option_list = BaseCommand.option_list + (
        make_option(
            "-s",
            "--session",
            dest="session",
            help="Specify session by UUID",
        ),
    )

    def handle(self, *args, **options):
        if options['session'] is None:
            raise CommandError("Option `--session=...` must be specified.")

        try:
            session = Session.objects.get(
                id=options['session'],
            )
        except Session.DoesNotExist:
            raise CommandError("Session does not exist.")

        items = Song.objects.filter(
            appearance__round__session=session,
        )
        for i in items:
            i.calculate()
            i.save()
        items = Appearance.objects.filter(
            round__session=session,
        )
        for i in items:
            i.calculate()
            i.save()
        items = Entry.objects.filter(
            session=session,
        )
        for i in items:
            i.calculate()
            i.save()
        items = Contestant.objects.filter(
            contest__session=session,
        )
        for i in items:
            i.calculate()
            i.save()
        return "Recalculated"
