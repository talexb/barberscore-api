# Django
# Standard Libary
import json
from itertools import chain
from optparse import make_option

from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder

# First-Party
from api.factories import (
    AppearanceFactory,
    AssignmentFactory,
    AwardFactory,
    ChartFactory,
    ContestantFactory,
    ContestFactory,
    ConventionFactory,
    EntityFactory,
    EntryFactory,
    MemberFactory,
    OfficeFactory,
    OfficerFactory,
    PanelistFactory,
    ParticipantFactory,
    PersonFactory,
    RepertoryFactory,
    RoundFactory,
    ScoreFactory,
    SessionFactory,
    SlotFactory,
    SongFactory,
    UserFactory,
    VenueFactory,
)
from api.models import (
    Appearance,
    Assignment,
    Award,
    Chart,
    Contest,
    Contestant,
    Convention,
    Entity,
    Entry,
    Member,
    Office,
    Officer,
    Panelist,
    Participant,
    Person,
    Repertory,
    Round,
    Score,
    Session,
    Slot,
    Song,
    User,
    Venue,
)


class Command(BaseCommand):
    help="Command to seed convention."
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '-b',
            '--break',
            dest='breakpoint',
            default=None,
            help='Set breakpoint for database seed.',
        )

    def handle(self, *args, **options):
        # Create Admin
        admin=UserFactory(
            email='test@barberscore.com',
            password='password',
            is_staff=True,
            person=None,
        )
        # Create Core Persons
        drcj_person=PersonFactory(
            name='DRCJ Person',
            email='drcj@barberscore.com',
        )
        ca_person=PersonFactory(
            name='CA Person',
            email='ca@barberscore.com',
        )
        quartet_person=PersonFactory(
            name='Quartet Person',
            email='quartet@barberscore.com',
        )
        # Create Core Users
        drcj_user=UserFactory(
            email=drcj_person.email,
            person=drcj_person,
        )
        ca_user=UserFactory(
            email=ca_person.email,
            person=ca_person,
        )
        quartet_user=UserFactory(
            email=quartet_person.email,
            person=quartet_person,
        )
        # Create International and Districts
        bhs=EntityFactory(
            name='Barbershop Harmony Society',
            short_name='BHS',
            kind=Entity.KIND.international,
        )
        district=EntityFactory(
            name='BHS District',
            short_name='DIS',
            parent=bhs,
            kind=Entity.KIND.district,
        )
        affiliate=EntityFactory(
            name='INT Affiliate',
            short_name='INT',
            parent=bhs,
            kind=Entity.KIND.affiliate,
        )
        # Create Core Offices
        drcj_office=OfficeFactory(
            name='District Director C&J',
            short_name='DRCJ',
            is_cj=True,
            is_drcj=True,
        )
        ca_office=OfficeFactory(
            name='Contest Administrator',
            short_name='CA',
            is_cj=True,
            is_ca=True,
        )
        mus_office=OfficeFactory(
            name='Music Judge',
            short_name='MUS',
            is_cj=True,
        )
        per_office=OfficeFactory(
            name='Performance Judge',
            short_name='PER',
            is_cj=True,
        )
        sng_office=OfficeFactory(
            name='Singing Judge',
            short_name='SNG',
            is_cj=True,
        )
        quartet_office=OfficeFactory(
            name='Quartet Representative',
            short_name='QREP',
            is_rep=True,
        )
        # Create Core Officers
        drcj_officer=OfficerFactory(
            office=drcj_office,
            person=drcj_person,
            entity=bhs,
            status=Officer.STATUS.active,
        )
        ca_officer=OfficerFactory(
            office=ca_office,
            person=ca_person,
            entity=bhs,
            status=Officer.STATUS.active,
        )
        # Create Charts
        charts = ChartFactory.create_batch(
            size=300,
        )
        # Create Quartets
        quartets = EntityFactory.create_batch(
            size=50,
            kind=Entity.KIND.quartet,
        )
        for idx, quartet in enumerate(quartets):
            i = 1
            while i <= 4:
                if i==1 and idx==0:
                    person = quartet_person
                else:
                    person = PersonFactory()
                MemberFactory(
                    entity=quartet,
                    person=person,
                    part=i,
                    status=Member.STATUS.active,
                )
                OfficerFactory(
                    office=quartet_office,
                    entity=quartet,
                    person=person,
                    status=Member.STATUS.active,
                )
                i += 1
        # Create Judges
        mus_judges=OfficerFactory.create_batch(
            size=5,
            office=mus_office,
            entity=bhs,
            status=Officer.STATUS.active,
        )
        per_judges=OfficerFactory.create_batch(
            size=5,
            office=per_office,
            entity=bhs,
            status=Officer.STATUS.active,
        )
        sng_judges=OfficerFactory.create_batch(
            size=5,
            office=sng_office,
            entity=bhs,
            status=Officer.STATUS.active,
        )
        # Create International Convention
        convention=ConventionFactory(
            name='International Convention',
            entity=bhs,
        )
        # Add Assignments
        drcj_assignment=AssignmentFactory(
            category=Assignment.CATEGORY.drcj,
            person=drcj_person,
            convention=convention,
            status=Assignment.STATUS.confirmed,
        )
        ca_assignment=AssignmentFactory(
            category=Assignment.CATEGORY.ca,
            person=ca_person,
            convention=convention,
            status=Assignment.STATUS.confirmed,
        )
        for judge in mus_judges:
            AssignmentFactory(
                category=Assignment.CATEGORY.music,
                person=judge.person,
                convention=convention,
                status=Assignment.STATUS.confirmed,
            )
        for judge in per_judges:
            AssignmentFactory(
                category=Assignment.CATEGORY.performance,
                person=judge.person,
                convention=convention,
                status=Assignment.STATUS.confirmed,
            )
        for judge in sng_judges:
            AssignmentFactory(
                category=Assignment.CATEGORY.singing,
                person=judge.person,
                convention=convention,
                status=Assignment.STATUS.confirmed,
            )
        # Create Quartet Session
        quartet_session=SessionFactory(
            convention=convention,
            kind=Session.KIND.quartet,
        )
        quartet_award=AwardFactory(
            name='International Quartet Championship',
            entity=bhs,
        )
        # Add Quartet Contest
        quartet_contest = ContestFactory(
            session=quartet_session,
            award=quartet_award,
        )
        # Schedule Convention
        convention.schedule()
        convention.save()
        if options['breakpoint'] == 'convention_scheduled':
            return
        # Open the Session for Entries
        quartet_session.open()
        quartet_session.save()
        # Enter 50 Quartets at Random
        quartets = Entity.objects.filter(
            kind=Entity.KIND.quartet,
        ).order_by('?')[:50]
        # Add Repertories to Entered Quartets
        for quartet in quartets:
            i = 1
            charts = list(Chart.objects.order_by('?')[:6])
            while i <= 6:
                RepertoryFactory(
                    entity=quartet,
                    chart=charts.pop(),
                )
                i += 1
        # Create Quartet Entries
        for quartet in quartets:
            EntryFactory(
                session=quartet_session,
                entity=quartet,
                representing=district,
                is_evaluation=False,
                status=Entry.STATUS.accepted,
            )
        # Add Contest and Participants to Entries
        for entry in quartet_session.entries.all():
            ContestantFactory(
                entry=entry,
                contest=quartet_contest,
            )
            for member in entry.entity.members.all():
                ParticipantFactory(
                    entry=entry,
                    member=member,
                )
        # Close Session
        quartet_session.close()
        quartet_session.save()
        if options['breakpoint'] == 'session_closed':
            return

        # Draw Entries
        entries = quartet_session.entries.filter(
            is_mt=False,
            status=Entry.STATUS.accepted,
        ).order_by('?')
        mts = quartet_session.entries.filter(
            is_mt=True,
        ).order_by('?')
        i = 1 - mts.count()
        for entry in mts:
            entry.draw = i
            entry.save()
            i += 1
        for entry in entries:
            entry.draw = i
            entry.save()
            i += 1
        # Verify Session
        quartet_session.verify()
        quartet_session.save()
        if options['breakpoint'] == 'session_verified':
            return

        quartet_quarters = quartet_session.rounds.get(num=1)
        for assignment in convention.assignments.filter(
            category__gt=Panelist.CATEGORY.aca,
        ):
            PanelistFactory(
                kind=assignment.kind,
                category=assignment.category,
                round=quartet_quarters,
                person=assignment.person,
            )
        i = 1
        # for entry in quartet_session.entries.all().order_by('?'):
        #     slot = SlotFactory(
        #         num=i,
        #         round=quartet_quarters,
        #     )
        #     AppearanceFactory(
        #         round=quartet_quarters,
        #         entry=entry,
        #         slot=slot,
        #         num=i,
        #     )
        #     i += 1
        for appearance in quartet_quarters.appearances.all():
            i = 1
            while i <= 2:  # TODO constant
                song = SongFactory(
                    num=i,
                    appearance=appearance,
                )
                i += 1
                for panelist in quartet_quarters.panelists.all().order_by('kind'):
                    ScoreFactory(
                        category=panelist.category,
                        kind=panelist.kind,
                        song=song,
                        panelist=panelist,
                    )
