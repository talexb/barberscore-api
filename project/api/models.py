# Standard Libary
import datetime
import logging
import random
import uuid

# Third-Party
from auth0.v3.management.rest import Auth0Error
from auth0.v3.authentication import Passwordless
from django_fsm import (
    RETURN_VALUE,
    FSMIntegerField,
    transition,
)
from django_fsm_log.decorators import fsm_log_by
from dry_rest_permissions.generics import (
    allow_staff_or_superuser,
    authenticated_users,
)
from model_utils import Choices
from model_utils.models import TimeStampedModel
from nameparser import HumanName
from ranking import Ranking
from timezone_field import TimeZoneField
from cloudinary_storage.storage import RawMediaCloudinaryStorage

# Django
from django.apps import apps as api_apps
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.postgres.fields import (
    ArrayField,
    FloatRangeField,
    IntegerRangeField,
    # CIEmailField,
)
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
    validate_email,
)
from django.db import (
    models,
    IntegrityError,
)
from django.utils.encoding import smart_text
from django.utils.timezone import now
from django.template.loader import get_template
from django.core.files.base import ContentFile
from django.utils.functional import cached_property
# Local
from .fields import (
    OneToOneOrNoneField,
    PathAndRename,
)
from .managers import UserManager
from .messages import send_entry, send_session
from .utils import create_bbscores

config = api_apps.get_app_config('api')

import docraptor
docraptor.configuration.username = settings.DOCRAPTOR_API_KEY
doc_api = docraptor.DocApi()

log = logging.getLogger(__name__)


class Appearance(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    STATUS = Choices(
        (0, 'new', 'New',),
        (2, 'published', 'Published',),
        (5, 'verified', 'Verified',),
        (10, 'started', 'Started',),
        (20, 'finished', 'Finished',),
        (30, 'confirmed', 'Confirmed',),
        (40, 'flagged', 'Flagged',),
        (50, 'scratched', 'Scratched',),
        (60, 'cleared', 'Cleared',),
        (90, 'announced', 'Announced',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    num = models.IntegerField(
        null=True,
        blank=True,
    )

    draw = models.IntegerField(
        null=True,
        blank=True,
    )

    actual_start = models.DateTimeField(
        help_text="""
            The actual appearance window.""",
        null=True,
        blank=True,
    )

    actual_finish = models.DateTimeField(
        help_text="""
            The actual appearance window.""",
        null=True,
        blank=True,
    )

    var_pdf = models.FileField(
        upload_to=PathAndRename(
            prefix='var',
        ),
        max_length=255,
        null=True,
        blank=True,
        storage=RawMediaCloudinaryStorage(),
    )

    # Privates
    rank = models.IntegerField(
        null=True,
        blank=True,
    )

    mus_points = models.IntegerField(
        null=True,
        blank=True,
    )

    per_points = models.IntegerField(
        null=True,
        blank=True,
    )

    sng_points = models.IntegerField(
        null=True,
        blank=True,
    )

    tot_points = models.IntegerField(
        null=True,
        blank=True,
    )

    mus_score = models.FloatField(
        null=True,
        blank=True,
    )

    per_score = models.FloatField(
        null=True,
        blank=True,
    )

    sng_score = models.FloatField(
        null=True,
        blank=True,
    )

    tot_score = models.FloatField(
        null=True,
        blank=True,
    )

    # FKs
    round = models.ForeignKey(
        'Round',
        related_name='appearances',
        on_delete=models.CASCADE,
    )

    entry = models.ForeignKey(
        'Entry',
        related_name='appearances',
        on_delete=models.CASCADE,
    )

    slot = models.OneToOneField(
        'Slot',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    # Internals
    class JSONAPIMeta:
        resource_name = "appearance"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = " ".join(
            map(
                lambda x: smart_text(x), [
                    self.round,
                    self.entry,
                ]
            )
        )
        super().save(*args, **kwargs)

    # Methods
    def print_var(self):
        appearance = self
        song_one = appearance.songs.all().order_by('num').first()
        song_two = appearance.songs.all().order_by('num').last()
        scores_one = song_one.scores.all().order_by('panelist__num')
        scores_two = song_two.scores.all().order_by('panelist__num')
        scores_one_avg = scores_one.aggregate(a=models.Avg('points'))['a']
        scores_two_avg = scores_two.aggregate(a=models.Avg('points'))['a']
        tem = get_template('variance.html')
        template = tem.render(context={
            'appearance': appearance,
            'song_one': song_one,
            'song_two': song_two,
            'scores_one' : scores_one,
            'scores_two' : scores_two,
            'scores_one_avg' : scores_one_avg,
            'scores_two_avg' : scores_two_avg,
        })
        try:
            create_response = doc_api.create_doc({
                "test": True,
                "document_content": template,
                "name": "var-{0}.pdf".format(id),
                "document_type": "pdf",
            })
            f = ContentFile(create_response)
            appearance.var_pdf.save(
                "{0}.pdf".format(id),
                f
            )
            appearance.save()
        except docraptor.rest.ApiException as error:
            print(error)
        return "Complete"

    def calculate(self, *args, **kwargs):
        self.rank = self.calculate_rank()
        self.mus_points = self.calculate_mus_points()
        self.per_points = self.calculate_per_points()
        self.sng_points = self.calculate_sng_points()
        self.tot_points = self.calculate_tot_points()
        self.mus_score = self.calculate_mus_score()
        self.per_score = self.calculate_per_score()
        self.sng_score = self.calculate_sng_score()
        self.tot_score = self.calculate_tot_score()

    def calculate_rank(self):
        return self.round.ranking(self.calculate_tot_points())

    def calculate_mus_points(self):
        return self.songs.filter(
            scores__kind=10,
            scores__category=30,
        ).aggregate(
            tot=models.Sum('scores__points')
        )['tot']

    def calculate_per_points(self):
        return self.songs.filter(
            scores__kind=10,
            scores__category=40,
        ).aggregate(
            tot=models.Sum('scores__points')
        )['tot']

    def calculate_sng_points(self):
        return self.songs.filter(
            scores__kind=10,
            scores__category=50,
        ).aggregate(
            tot=models.Sum('scores__points')
        )['tot']

    def calculate_tot_points(self):
        return self.songs.filter(
            scores__kind=10,
        ).aggregate(
            tot=models.Sum('scores__points')
        )['tot']

    def calculate_mus_score(self):
        return self.songs.filter(
            scores__kind=10,
            scores__category=30,
        ).aggregate(
            tot=models.Avg('scores__points')
        )['tot']

    def calculate_per_score(self):
        return self.songs.filter(
            scores__kind=10,
            scores__category=40,
        ).aggregate(
            tot=models.Avg('scores__points')
        )['tot']

    def calculate_sng_score(self):
        return self.songs.filter(
            scores__kind=10,
            scores__category=50,
        ).aggregate(
            tot=models.Avg('scores__points')
        )['tot']

    def calculate_tot_score(self):
        return self.songs.filter(
            scores__kind=10,
        ).aggregate(
            tot=models.Avg('scores__points')
        )['tot']

    # Appearance Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            request.user.person.officers.filter(
                office__is_scoring_manager=True,
                status__gt=0,
            ),
            request.user.person.officers.filter(
                office__is_convention_manager=True,
                status__gt=0,
            )
        ])

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            self.round.session.convention.assignments.filter(
                person=request.user.person,
                category__lt=30,
                status__gt=0,
                kind=10,
            )
        ])


    # Transitions
    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.started)
    def start(self, *args, **kwargs):
        panelists = self.round.panelists.filter(
            category__gt=20,
        )
        i = 1
        while i <= 2:  # Number songs constant
            song = self.songs.create(
                num=i
            )
            for panelist in panelists:
                song.scores.create(
                    category=panelist.category,
                    kind=panelist.kind,
                    panelist=panelist,
                )
            i += 1
        self.actual_start = now()
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.finished)
    def finish(self, *args, **kwargs):
        self.actual_finish = now()
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.confirmed)
    def confirm(self, *args, **kwargs):
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.announced)
    def announce(self, *args, **kwargs):
        return


class Assignment(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    STATUS = Choices(
        (-10, 'inactive', 'Inactive',),
        (0, 'new', 'New',),
        (10, 'active', 'Active',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    KIND = Choices(
        (10, 'official', 'Official'),
        (20, 'practice', 'Practice'),
        (30, 'composite', 'Composite'),
    )

    kind = models.IntegerField(
        choices=KIND,
    )

    CATEGORY = Choices(
        (5, 'drcj', 'DRCJ'),
        (10, 'admin', 'CA'),
        (30, 'music', 'Music'),
        (40, 'performance', 'Performance'),
        (50, 'singing', 'Singing'),
    )

    category = models.IntegerField(
        choices=CATEGORY,
        null=True,
        blank=True,
    )

    # FKs
    convention = models.ForeignKey(
        'Convention',
        related_name='assignments',
        on_delete=models.CASCADE,
    )

    person = models.ForeignKey(
        'Person',
        related_name='assignments',
        on_delete=models.CASCADE,
    )

    # Internals
    class Meta:
        unique_together = (
            ('convention', 'person',)
        )

    class JSONAPIMeta:
        resource_name = "assignment"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = " ".join(filter(None, [
            "{0}".format(self.person),
            "{0}".format(self.convention),
            self.get_kind_display(),
        ]))
        super().save(*args, **kwargs)

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            request.user.person.officers.filter(
                office__is_judge_manager=True,
                status__gt=0,
            ),
            request.user.person.officers.filter(
                office__is_convention_manager=True,
                status__gt=0,
            )
        ])

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            self.convention.assignments.filter(
                person=request.user.person,
                category__lt=20,
                status__gt=0,
            )
        ])

    # Transitions
    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.active)
    def activate(self, *args, **kwargs):
        """Activate the Assignment."""
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.inactive)
    def deactivate(self, *args, **kwargs):
        """Deactivate the Assignment."""
        return


class Award(TimeStampedModel):
    """
    Award Model.

    The specific award conferred by an Organization.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    name = models.CharField(
        help_text="""Award Name.""",
        max_length=255,
    )

    STATUS = Choices(
        (-10, 'inactive', 'Inactive',),
        (0, 'new', 'New',),
        (10, 'active', 'Active',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    KIND = Choices(
        (32, 'chorus', "Chorus"),
        (33, 'vlq', "Very Large Quartet"),
        (34, 'mixed', "Mixed Group"),
        (41, 'quartet', "Quartet"),
    )

    kind = models.IntegerField(
        choices=KIND,
    )

    LEVEL = Choices(
        (10, 'championship', "Championship"),
        (20, 'award', "Award"),
        (30, 'qualifier', "Qualifier"),
        (40, 'sentinel', "Sentinel"),
    )

    level = models.IntegerField(
        choices=LEVEL,
        null=True,
        blank=True,
    )

    SEASON = Choices(
        (1, 'summer', 'Summer',),
        (2, 'midwinter', 'Midwinter',),
        (3, 'fall', 'Fall',),
        (4, 'spring', 'Spring',),
        (9, 'video', 'Video',),
    )

    season = models.IntegerField(
        choices=SEASON,
        null=True,
        blank=True,
    )

    is_primary = models.BooleanField(
        help_text="""Primary (v. Secondary).""",
        default=False,
    )

    is_invitational = models.BooleanField(
        help_text="""Invite-only (v. Open).""",
        default=False,
    )

    is_manual = models.BooleanField(
        help_text="""Manual (v. Automatic).""",
        default=False,
    )

    rounds = models.IntegerField(
        help_text="""Number of rounds to determine the championship""",
    )

    threshold = models.FloatField(
        help_text="""
            The score threshold for automatic qualification (if any.)
        """,
        null=True,
        blank=True,
    )

    minimum = models.FloatField(
        help_text="""
            The minimum score required for qualification (if any.)
        """,
        null=True,
        blank=True,
    )

    advance = models.FloatField(
        help_text="""
            The score threshold to advance to next round (if any) in
            multi-round qualification.
        """,
        null=True,
        blank=True,
    )

    description = models.TextField(
        help_text="""
            The Public description of the award.""",
        blank=True,
        max_length=1000,
    )

    notes = models.TextField(
        help_text="""
            Private Notes (for internal use only).""",
        blank=True,
    )

    footnote = models.CharField(
        help_text="""
            The text to present on the OSS""",
        blank=True,
        max_length=255,
    )

    is_improved = models.BooleanField(
        help_text="""Designates 'Most-Improved'.  Implies manual.""",
        default=False,
    )

    is_multi = models.BooleanField(
        help_text="""Award spans conventions; must be determined manually.""",
        default=False,
    )

    is_rep_qualifies = models.BooleanField(
        help_text="""Boolean; true means the district rep qualifies.""",
        default=False,
    )

    AGE = Choices(
        (10, 'seniors', 'Seniors',),
        (20, 'collegiate', 'Collegiate',),
        (30, 'youth', 'Youth',),
    )

    age = models.IntegerField(
        choices=AGE,
        null=True,
        blank=True,
    )

    SIZE = Choices(
        (100, 'p1', 'Plateau 1',),
        (110, 'p2', 'Plateau 2',),
        (120, 'p3', 'Plateau 3',),
        (130, 'p4', 'Plateau 4',),
        (140, 'pa', 'Plateau A',),
        (150, 'paa', 'Plateau AA',),
        (160, 'paaa', 'Plateau AAA',),
        (170, 'paaaa', 'Plateau AAAA',),
        (180, 'pb', 'Plateau B',),
        (190, 'pi', 'Plateau I',),
        (200, 'pii', 'Plateau II',),
        (210, 'piii', 'Plateau III',),
        (220, 'piv', 'Plateau IV',),
        (230, 'small', 'Small',),
    )

    size = models.IntegerField(
        choices=SIZE,
        null=True,
        blank=True,
    )

    size_range = IntegerRangeField(
        null=True,
        blank=True,
    )

    SCOPE = Choices(
        (100, 'p1', 'Plateau 1',),
        (110, 'p2', 'Plateau 2',),
        (120, 'p3', 'Plateau 3',),
        (130, 'p4', 'Plateau 4',),
        (140, 'pa', 'Plateau A',),
        (150, 'paa', 'Plateau AA',),
        (160, 'paaa', 'Plateau AAA',),
        (170, 'paaaa', 'Plateau AAAA',),
        (175, 'paaaaa', 'Plateau AAAAA',),
    )

    scope = models.IntegerField(
        choices=SCOPE,
        null=True,
        blank=True,
    )

    scope_range = FloatRangeField(
        null=True,
        blank=True,
    )

    # FKs
    organization = models.ForeignKey(
        'Organization',
        related_name='awards',
        on_delete=models.CASCADE,
    )

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        db_index=True,
        on_delete=models.SET_NULL,
    )

    # Internals
    class JSONAPIMeta:
        resource_name = "award"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = self.name
        super().save(*args, **kwargs)

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            request.user.person.officers.filter(
                office__is_convention_manager=True,
                status__gt=0,
            )
        ])

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            self.organization.officers.filter(
                person=request.user.person,
                office__is_convention_manager=True,
                status__gt=0,
            )
        ])

    # Transitions
    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.active)
    def activate(self, *args, **kwargs):
        """Activate the Award."""
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.inactive)
    def deactivate(self, *args, **kwargs):
        """Deactivate the Award."""
        return


class Chart(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    STATUS = Choices(
        (-10, 'inactive', 'Inactive',),
        (0, 'new', 'New'),
        (10, 'active', 'Active'),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    title = models.CharField(
        max_length=255,
    )

    arrangers = models.CharField(
        max_length=255,
    )

    composers = models.CharField(
        max_length=255,
    )

    lyricists = models.CharField(
        max_length=255,
    )

    holders = models.TextField(
        blank=True,
    )

    description = models.TextField(
        help_text="""
            Fun or interesting facts to share about the chart (ie, 'from Disney's Lion King, first sung by Elton John'.)""",
        blank=True,
        max_length=1000,
    )

    notes = models.TextField(
        help_text="""
            Private Notes (for internal use only).""",
        blank=True,
    )

    image = models.FileField(
        upload_to=PathAndRename(),
        max_length=255,
        null=True,
        blank=True,
    )

    # Internals
    class Meta:
        unique_together = (
            ('title', 'arrangers',)
        )

    class JSONAPIMeta:
        resource_name = "chart"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = " ".join(filter(None, [
            self.title,
            "[{0}]".format(self.arrangers),
        ]))
        super().save(*args, **kwargs)

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            request.user.person.officers.filter(
                office__is_chart_manager=True,
                status__gt=0,
            ),
            request.user.person.officers.filter(
                office__is_group_manager=True,
                status__gt=0,
            ),
        ])

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            request.user.person.officers.filter(
                office__is_chart_manager=True,
                status__gt=0,
            ),
        ])

    # Transitions
    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.active)
    def activate(self, *args, **kwargs):
        """Activate the Chart."""
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.inactive)
    def deactivate(self, *args, **kwargs):
        """Deactivate the Chart."""
        return


class Contest(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    STATUS = Choices(
        (0, 'new', 'New',),
        (10, 'opened', 'Opened',),
        (15, 'closed', 'Closed',),
        (35, 'verified', 'Verified',),
        (42, 'finished', 'Finished',),
        (45, 'announced', 'Announced',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    is_qualifier = models.BooleanField(
        default=False,
    )

    is_primary = models.BooleanField(
        default=False,
    )

    KIND = Choices(
        (-10, 'qualifier', 'Qualifier',),
        (0, 'new', 'New',),
        (10, 'championship', 'Championship',),
    )

    kind = FSMIntegerField(
        choices=KIND,
        default=KIND.new,
    )

    # Private
    champion = models.ForeignKey(
        'Entry',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    # FKs
    session = models.ForeignKey(
        'Session',
        related_name='contests',
        on_delete=models.CASCADE,
    )

    award = models.ForeignKey(
        'Award',
        related_name='contests',
        on_delete=models.CASCADE,
    )

    # Internals
    class Meta:
        unique_together = (
            ('session', 'award',)
        )

    class JSONAPIMeta:
        resource_name = "contest"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = " ".join(filter(None, [
            self.award.name,
            self.session.nomen,
        ]))
        super().save(*args, **kwargs)

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            request.user.person.officers.filter(
                office__is_convention_manager=True,
                status__gt=0,
            )
        ])

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            self.session.convention.assignments.filter(
                person=request.user.person,
                category__lte=10,
                kind=10,
            )
        ])

    # Methods
    def ranking(self, point_total):
        if not point_total:
            return None
        contestants = self.contestants.all()
        points = [contestant.calculate_tot_points() for contestant in contestants]
        points = sorted(points, reverse=True)
        ranking = Ranking(points, start=1)
        rank = ranking.rank(point_total)
        return rank

    def calculate(self, *args, **kwargs):
        if self.contest.is_qualifier:
            champion = None
        else:
            try:
                champion = self.contest.contestants.get(rank=1).entry
            except self.contest.contestants.model.DoesNotExist:
                champion = None
            except self.contest.contestants.model.MultipleObjectsReturned:
                champion = self.contest.contestants.filter(rank=1).order_by(
                    '-sng_points',
                    '-mus_points',
                    '-per_points',
                ).first().entry
        self.champion = champion

    # Transitions
    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.finished)
    def finish(self, *args, **kwargs):
        return


class Contestant(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    STATUS = Choices(
        (0, 'new', 'New',),
        (10, 'eligible', 'Eligible',),
        (20, 'ineligible', 'Ineligible',),
        (40, 'rep', 'District Representative',),
        (50, 'qualified', 'Qualified',),
        (55, 'verified', 'Verified',),
        (60, 'finished', 'Finished',),
        (70, 'scratched', 'Scratched',),
        (80, 'disqualified', 'Disqualified',),
        (90, 'announced', 'Announced',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    # Privates
    rank = models.IntegerField(
        null=True,
        blank=True,
    )

    mus_points = models.IntegerField(
        null=True,
        blank=True,
    )

    per_points = models.IntegerField(
        null=True,
        blank=True,
    )

    sng_points = models.IntegerField(
        null=True,
        blank=True,
    )

    tot_points = models.IntegerField(
        null=True,
        blank=True,
    )

    mus_score = models.FloatField(
        null=True,
        blank=True,
    )

    per_score = models.FloatField(
        null=True,
        blank=True,
    )

    sng_score = models.FloatField(
        null=True,
        blank=True,
    )

    tot_score = models.FloatField(
        null=True,
        blank=True,
    )

    # FKs
    entry = models.ForeignKey(
        'Entry',
        related_name='contestants',
        on_delete=models.CASCADE,
    )

    contest = models.ForeignKey(
        'Contest',
        related_name='contestants',
        on_delete=models.CASCADE,
    )

    # Internals
    class Meta:
        unique_together = (
            ('entry', 'contest',),
        )

    class JSONAPIMeta:
        resource_name = "contestant"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = " ".join(
            map(
                lambda x: smart_text(x), [
                    self.entry,
                    self.contest,
                ]
            )
        )
        super().save(*args, **kwargs)

    # Methods
    def calculate(self, *args, **kwargs):
        self.mus_points = self.calculate_mus_points()
        self.per_points = self.calculate_per_points()
        self.sng_points = self.calculate_sng_points()
        self.tot_points = self.calculate_tot_points()
        self.mus_score = self.calculate_mus_score()
        self.per_score = self.calculate_per_score()
        self.sng_score = self.calculate_sng_score()
        self.tot_score = self.calculate_tot_score()
        self.rank = self.calculate_rank()

    def calculate_rank(self):
        return self.contest.ranking(self.calculate_tot_points())

    def calculate_mus_points(self):
        return self.entry.appearances.filter(
            songs__scores__kind=10,
            songs__scores__category=30,
            round__num__lte=self.contest.award.rounds,
        ).aggregate(
            tot=models.Sum('songs__scores__points')
        )['tot']

    def calculate_per_points(self):
        return self.entry.appearances.filter(
            songs__scores__kind=10,
            songs__scores__category=40,
            round__num__lte=self.contest.award.rounds,
        ).aggregate(
            tot=models.Sum('songs__scores__points')
        )['tot']

    def calculate_sng_points(self):
        return self.entry.appearances.filter(
            songs__scores__kind=10,
            songs__scores__category=50,
            round__num__lte=self.contest.award.rounds,
        ).aggregate(
            tot=models.Sum('songs__scores__points')
        )['tot']

    def calculate_tot_points(self):
        return self.entry.appearances.filter(
            songs__scores__kind=10,
            round__num__lte=self.contest.award.rounds,
        ).aggregate(
            tot=models.Sum('songs__scores__points')
        )['tot']

    def calculate_mus_score(self):
        return self.entry.appearances.filter(
            songs__scores__kind=10,
            songs__scores__category=30,
            round__num__lte=self.contest.award.rounds,
        ).aggregate(
            tot=models.Avg('songs__scores__points')
        )['tot']

    def calculate_per_score(self):
        return self.entry.appearances.filter(
            songs__scores__kind=10,
            songs__scores__category=40,
            round__num__lte=self.contest.award.rounds,
        ).aggregate(
            tot=models.Avg('songs__scores__points')
        )['tot']

    def calculate_sng_score(self):
        return self.entry.appearances.filter(
            songs__scores__kind=10,
            songs__scores__category=50,
            round__num__lte=self.contest.award.rounds,
        ).aggregate(
            tot=models.Avg('songs__scores__points')
        )['tot']

    def calculate_tot_score(self):
        return self.entry.appearances.filter(
            songs__scores__kind=10,
            round__num__lte=self.contest.award.rounds,
        ).aggregate(
            tot=models.Avg('songs__scores__points')
        )['tot']

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            request.user.person.officers.filter(
                office__is_convention_manager=True,
                status__gt=0,
            ),
            request.user.person.members.filter(
                is_admin=True,
                status__gt=0,
            ),
        ])

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            self.contest.session.convention.assignments.filter(
                person=request.user.person,
                category__lte=10,
                kind=10,
            ),
            self.entry.group.members.filter(
                person=request.user.person,
                is_admin=True,
                status__gt=0,
            ),
        ])


    # Methods

    # Transitions
    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.disqualified)
    def process(self, *args, **kwargs):
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.scratched)
    def scratch(self, *args, **kwargs):
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.disqualified)
    def disqualify(self, *args, **kwargs):
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.finished)
    def finish(self, *args, **kwargs):
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.announced)
    def announce(self, *args, **kwargs):
        return


class Convention(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    name = models.CharField(
        max_length=255,
    )

    STATUS = Choices(
        (0, 'new', 'New',),
        (2, 'published', 'Published',),
        (95, 'archived', 'Archived',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    SEASON = Choices(
        (1, 'summer', 'Summer',),
        (2, 'midwinter', 'Midwinter',),
        (3, 'fall', 'Fall',),
        (4, 'spring', 'Spring',),
        (9, 'video', 'Video',),
    )

    season = models.IntegerField(
        choices=SEASON,
    )

    PANEL = Choices(
        (1, 'single', "Single"),
        (2, 'double', "Double"),
        (3, 'triple', "Triple"),
        (4, 'quadruple', "Quadruple"),
        (5, 'quintiple', "Quintiple"),
    )

    panel = models.IntegerField(
        choices=PANEL,
        null=True,
        blank=True,
    )

    YEAR_CHOICES = []
    for r in reversed(range(1939, (datetime.datetime.now().year + 2))):
        YEAR_CHOICES.append((r, r))

    year = models.IntegerField(
        choices=YEAR_CHOICES,
    )

    open_date = models.DateField(
        null=True,
        blank=True,
    )

    close_date = models.DateField(
        null=True,
        blank=True,
    )

    start_date = models.DateField(
        null=True,
        blank=True,
    )

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    location = models.CharField(
        max_length=255,
        blank=True,
    )

    # FKs
    venue = models.ForeignKey(
        'Venue',
        related_name='conventions',
        help_text="""
            The venue for the convention.""",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    organization = models.ForeignKey(
        'Organization',
        related_name='conventions',
        help_text="""
            The owning organization for the convention.""",
        on_delete=models.CASCADE,
    )

    # Internals
    class JSONAPIMeta:
        resource_name = "convention"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = self.name
        super().save(*args, **kwargs)

    # Convention Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            request.user.person.officers.filter(
                office__is_convention_manager=True,
                status__gt=0,
            ),
        ])

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            self.organization.officers.filter(
                person__user=request.user,
                status__gt=0,
            ),
        ])

    # Convention Transition Conditions
    def can_publish_convention(self):
        return all([
            self.name,
            self.organization,
            self.season,
            self.year,
            self.open_date,
            self.close_date,
            self.start_date,
            self.end_date,
        ])

    # Transitions
    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.published, conditions=[can_publish_convention])
    def publish(self, *args, **kwargs):
        """Publish convention and related sessions"""
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.archived)
    def archive(self, *args, **kwargs):
        return


class Entry(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    STATUS = Choices(
        (0, 'new', 'New',),
        (5, 'invited', 'Invited',),
        (7, 'declined', 'Declined',),
        (10, 'submitted', 'Submitted',),
        (20, 'approved', 'Approved',),
        (30, 'rejected', 'Rejected',),
        (40, 'withdrew', 'Withdrew',),
        (50, 'verified', 'Verified',),
        (52, 'scratched', 'Scratched',),
        (55, 'disqualified', 'Disqualified',),
        (57, 'started', 'Started',),
        (60, 'finished', 'Finished',),
        (70, 'completed', 'Completed',),
        (90, 'announced', 'Announced',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    image = models.ImageField(
        upload_to=PathAndRename(),
        max_length=255,
        null=True,
        blank=True,
    )

    is_evaluation = models.BooleanField(
        help_text="""
            Entry requests evaluation.""",
        default=True,
    )

    is_private = models.BooleanField(
        help_text="""
            Keep scores private.""",
        default=False,
    )

    draw = models.IntegerField(
        help_text="""
            The draw for the initial round only.""",
        null=True,
        blank=True,
    )

    seed = models.IntegerField(
        help_text="""
            The incoming rank based on prelim score.""",
        null=True,
        blank=True,
    )

    prelim = models.FloatField(
        help_text="""
            The incoming prelim score.""",
        null=True,
        blank=True,
    )

    # Privates
    rank = models.IntegerField(
        null=True,
        blank=True,
    )

    mus_points = models.IntegerField(
        null=True,
        blank=True,
    )

    per_points = models.IntegerField(
        null=True,
        blank=True,
    )

    sng_points = models.IntegerField(
        null=True,
        blank=True,
    )

    tot_points = models.IntegerField(
        null=True,
        blank=True,
    )

    mus_score = models.FloatField(
        null=True,
        blank=True,
    )

    per_score = models.FloatField(
        null=True,
        blank=True,
    )

    sng_score = models.FloatField(
        null=True,
        blank=True,
    )

    tot_score = models.FloatField(
        null=True,
        blank=True,
    )

    csa_pdf = models.FileField(
        upload_to=PathAndRename(
            prefix='csa',
        ),
        max_length=255,
        null=True,
        blank=True,
        storage=RawMediaCloudinaryStorage(),
    )

    # FKs
    session = models.ForeignKey(
        'Session',
        related_name='entries',
        on_delete=models.CASCADE,
    )

    group = models.ForeignKey(
        'Group',
        related_name='entries',
        on_delete=models.CASCADE,
    )

    # Internals
    class Meta:
        verbose_name_plural = 'entries'
        unique_together = (
            ('group', 'session',),
        )

    class JSONAPIMeta:
        resource_name = "entry"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = " ".join(
            map(
                lambda x: smart_text(x), [
                    self.group,
                    self.session,
                ]
            )
        )
        super().save(*args, **kwargs)

    # Methods
    def calculate(self, *args, **kwargs):
        self.mus_points = self.calculate_mus_points()
        self.per_points = self.calculate_per_points()
        self.sng_points = self.calculate_sng_points()
        self.tot_points = self.calculate_tot_points()
        self.mus_score = self.calculate_mus_score()
        self.per_score = self.calculate_per_score()
        self.sng_score = self.calculate_sng_score()
        self.tot_score = self.calculate_tot_score()
        self.rank = self.calculate_rank()

    def calculate_pdf(self):
        for appearance in self.appearances.all():
            for song in appearance.songs.all():
                song.calculate()
                song.save()
            appearance.calculate()
            appearance.save()
        self.calculate()
        self.save()
        return

    def print_csa(self):
        entry = self
        contestants = entry.contestants.all()
        appearances = entry.appearances.order_by(
            'round__kind',
        )
        assignments = entry.session.convention.assignments.filter(
            category__gt=20,
        ).order_by(
            'category',
            'kind',
            'nomen',
        )
        tem = get_template('csa.html')
        template = tem.render(context={
            'entry': entry,
            'appearances': appearances,
            'assignments': assignments,
            'contestants': contestants,
        })
        try:
            create_response = doc_api.create_doc({
                "test": True,
                "document_content": template,
                "name": "csa-{0}.pdf".format(id),
                "document_type": "pdf",
            })
            f = ContentFile(create_response)
            entry.csa_pdf.save(
                "{0}.pdf".format(id),
                f
            )
            entry.save()
        except docraptor.rest.ApiException as error:
            print(error)
        return "Complete"

    def calculate_rank(self):
        try:
            primary = self.session.contests.first()
            return self.contestants.get(contest=primary).calculate_rank()
        except self.contestants.model.DoesNotExist:
            return None

    def calculate_mus_points(self):
        return self.appearances.filter(
            songs__scores__kind=10,
            songs__scores__category=30,
        ).aggregate(
            tot=models.Sum('songs__scores__points')
        )['tot']

    def calculate_per_points(self):
        return self.appearances.filter(
            songs__scores__kind=10,
            songs__scores__category=40,
        ).aggregate(
            tot=models.Sum('songs__scores__points')
        )['tot']

    def calculate_sng_points(self):
        return self.appearances.filter(
            songs__scores__kind=10,
            songs__scores__category=50,
        ).aggregate(
            tot=models.Sum('songs__scores__points')
        )['tot']

    def calculate_tot_points(self):
        return self.appearances.filter(
            songs__scores__kind=10,
        ).aggregate(
            tot=models.Sum('songs__scores__points')
        )['tot']

    def calculate_mus_score(self):
        return self.appearances.filter(
            songs__scores__kind=10,
            songs__scores__category=30,
        ).aggregate(
            tot=models.Avg('songs__scores__points')
        )['tot']

    def calculate_per_score(self):
        return self.appearances.filter(
            songs__scores__kind=10,
            songs__scores__category=40,
        ).aggregate(
            tot=models.Avg('songs__scores__points')
        )['tot']

    def calculate_sng_score(self):
        return self.appearances.filter(
            songs__scores__kind=10,
            songs__scores__category=50,
        ).aggregate(
            tot=models.Avg('songs__scores__points')
        )['tot']

    def calculate_tot_score(self):
        return self.appearances.filter(
            songs__scores__kind=10,
        ).aggregate(
            tot=models.Avg('songs__scores__points')
        )['tot']

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            request.user.person.members.filter(
                status__gt=0,
                is_admin=True,
            ),
            request.user.person.officers.filter(
                status__gt=0,
                office__is_session_manager=True,
            ),
        ])

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            self.session.convention.assignments.filter(
                person=request.user.person,
                category__lt=10,
                kind=10,
            ),
            self.group.members.filter(
                person=request.user.person,
                status__gt=0,
                is_admin=True,
            ),
        ])


    # Methods

    # Entry Transition Conditions
    def can_invite_entry(self):
        return all([
            self.group.members.filter(is_admin=True),
        ])


    # Transitions
    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.invited, conditions=[can_invite_entry])
    def invite(self, *args, **kwargs):
        send_entry(self, 'entry_invite.txt')
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.declined)
    def decline(self, *args, **kwargs):
        send_entry(self, 'entry_decline.txt')
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.submitted)
    def submit(self, *args, **kwargs):
        send_entry(self, 'entry_submit.txt')
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.approved)
    def approve(self, *args, **kwargs):
        send_entry(self, 'entry_approve.txt')
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.scratched)
    def scratch(self, *args, **kwargs):
        if self.session.status == self.session.STATUS.verified:
            remains = self.session.entries.filter(draw__gt=self.draw)
            self.draw = None
            self.save()
            for entry in remains:
                entry.draw = entry.draw - 1
                entry.save()
        send_entry(self, 'entry_scratch.txt')
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.completed)
    def complete(self, *args, **kwargs):
        self.calculate()
        self.save()
        return


class Grantor(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    STATUS = Choices(
        (0, 'new', 'New',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    # FKs
    session = models.ForeignKey(
        'Session',
        related_name='grantors',
        on_delete=models.CASCADE,
    )

    organization = models.ForeignKey(
        'Organization',
        related_name='grantors',
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = (
            ('session', 'organization',),
        )

    class JSONAPIMeta:
        resource_name = "grantor"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = " ".join(
            map(
                lambda x: smart_text(x), [
                    self.session,
                    self.organization,
                ]
            )
        )
        super().save(*args, **kwargs)

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return any([
            True,
        ])


    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return any([
            True,
        ])


    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            True,
            # request.user.person.officers.filter(
            #     office__is_convention_manager=True,
            #     status__gt=0,
            # ),
        ])

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            True,
            # self.round.session.convention.assignments.filter(
            #     person=request.user.person,
            #     category__lt=30,
            #     kind=10,
            # ),
        ])


class Group(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    name = models.CharField(
        help_text="""
            The name of the resource.
        """,
        max_length=255,
    )

    STATUS = Choices(
        (-10, 'inactive', 'Inactive',),
        (-5, 'aic', 'AIC',),
        (0, 'new', 'New',),
        (10, 'active', 'Active',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    KIND = Choices(
        (32, 'chorus', "Chorus"),
        (33, 'vlq', "Very Large Quartet"),
        (34, 'mixed', "Mixed Group"),
        (41, 'quartet', "Quartet"),
    )

    kind = models.IntegerField(
        help_text="""
            The kind of group.
        """,
        choices=KIND,
    )

    short_name = models.CharField(
        help_text="""
            A short-form name for the resource.""",
        blank=True,
        max_length=255,
    )

    code = models.CharField(
        help_text="""
            The chapter code.""",
        max_length=255,
        blank=True,
    )

    start_date = models.DateField(
        null=True,
        blank=True,
    )

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    location = models.CharField(
        help_text="""
            The geographical location of the resource.""",
        max_length=255,
        blank=True,
    )

    website = models.URLField(
        help_text="""
            The website URL of the resource.""",
        blank=True,
    )

    facebook = models.URLField(
        help_text="""
            The facebook URL of the resource.""",
        blank=True,
    )

    twitter = models.CharField(
        help_text="""
            The twitter handle (in form @twitter_handle) of the resource.""",
        blank=True,
        max_length=16,
        validators=[
            RegexValidator(
                regex=r'@([A-Za-z0-9_]+)',
                message="""
                    Must be a single Twitter handle
                    in the form `@twitter_handle`.
                """,
            ),
        ],
    )

    email = models.EmailField(
        help_text="""
            The contact email of the resource.""",
        blank=True,
    )

    phone = models.CharField(
        help_text="""
            The phone number of the resource.  Include country code.""",
        blank=True,
        max_length=25,
    )

    image = models.ImageField(
        upload_to=PathAndRename(),
        max_length=255,
        null=True,
        blank=True,
    )

    description = models.TextField(
        help_text="""
            A description of the group.  Max 1000 characters.""",
        blank=True,
        max_length=1000,
    )

    notes = models.TextField(
        help_text="""
            Notes (for internal use only).""",
        blank=True,
    )

    bhs_id = models.IntegerField(
        unique=True,
        blank=True,
        null=True,
    )

    org_sort = models.IntegerField(
        unique=True,
        blank=True,
        null=True,
        editable=False,
    )

    # FKs
    organization = models.ForeignKey(
        'Organization',
        null=True,
        blank=True,
        related_name='groups',
        db_index=True,
        on_delete=models.SET_NULL,
    )

    # Internals
    class Meta:
        verbose_name_plural = 'groups'

    class JSONAPIMeta:
        resource_name = "group"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = self.name
        super().save(*args, **kwargs)

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            request.user.person.officers.filter(
                office__is_group_manager=True,
                status__gt=0,
            ),
            request.user.person.members.filter(
                is_admin=True,
                status__gt=0,
            ),
        ])


    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            self.members.filter(
                person=request.user.person,
                is_admin=True,
                status__gt=0,
            ),
            request.user.person.officers.filter(
                office__is_group_manager=True,
                status__gt=0,
            ),
        ])

    # Transitions
    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.active)
    def activate(self, *args, **kwargs):
        """Activate the Group."""
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.inactive)
    def deactivate(self, *args, **kwargs):
        """Deactivate the Group."""
        return


class Member(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    STATUS = Choices(
        (-10, 'inactive', 'Inactive',),
        (0, 'new', 'New',),
        (5, 'provisional', 'Provisional',),
        (10, 'active', 'Active',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    PART = Choices(
        (-1, 'director', 'Director'),
        (1, 'tenor', 'Tenor'),
        (2, 'lead', 'Lead'),
        (3, 'baritone', 'Baritone'),
        (4, 'bass', 'Bass'),
    )

    part = models.IntegerField(
        choices=PART,
        null=True,
        blank=True,
    )

    start_date = models.DateField(
        null=True,
        blank=True,
    )

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    is_admin = models.BooleanField(
        default=False,
    )

    # FKs
    group = models.ForeignKey(
        'Group',
        related_name='members',
        on_delete=models.CASCADE,
    )

    person = models.ForeignKey(
        'Person',
        related_name='members',
        on_delete=models.CASCADE,
    )

    # Internals
    class Meta:
        unique_together = (
            ('group', 'person',),
        )

    class JSONAPIMeta:
        resource_name = "member"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = " ".join(
            map(
                lambda x: smart_text(x), [
                    self.person,
                    self.group,
                ]
            )
        )
        super().save(*args, **kwargs)

    def create_account(self):
        try:
            validate_email(self.person.email)
        except ValidationError as e:
            return
        try:
            user, created = User.objects.get_or_create(
                person=self.person,
                email=self.person.email.lower()
            )
            return user, created
        except IntegrityError as e:
            return
        except Auth0Error as e:
            log.error((e.details, self))
            return e

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            request.user.person.members.filter(
                is_admin=True,
                status__gt=0,
            ),
        ])

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            self.group.members.filter(
                person=request.user.person,
                is_admin=True,
                status__gt=0,
            ),
        ])

    # Transitions
    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.active)
    def activate(self, *args, **kwargs):
        """Activate the Member."""
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.inactive)
    def deactivate(self, *args, **kwargs):
        """Deactivate the Member."""
        return


class Office(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    name = models.CharField(
        max_length=255,
    )

    STATUS = Choices(
        (-10, 'inactive', 'Inactive',),
        (0, 'new', 'New',),
        (10, 'active', 'Active',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    KIND = Choices(
        ('International', [
            (1, 'international', "International"),
        ]),
        ('District', [
            (11, 'district', "District"),
            (12, 'noncomp', "Noncompetitive"),
            (13, 'affiliate', "Affiliate"),
        ]),
        ('Division', [
            (21, 'division', "Division"),
        ]),
        ('Group', [
            (32, 'chapter', "Chapter"),
            (33, 'vlq', "Very Large Quartet"),
            (34, 'mixed', "Mixed Group"),
            (41, 'quartet', "Quartet"),
        ]),
    )

    kind = models.IntegerField(
        help_text="""
            The kind of office.""",
        choices=KIND,
        null=True,
        blank=True,
    )

    short_name = models.CharField(
        max_length=255,
        blank=True,
    )

    # Module permissions
    is_convention_manager = models.BooleanField(
        default=False,
    )

    is_session_manager = models.BooleanField(
        default=False,
    )

    is_scoring_manager = models.BooleanField(
        default=False,
    )

    is_organization_manager = models.BooleanField(
        default=False,
    )

    is_group_manager = models.BooleanField(
        default=False,
    )

    is_person_manager = models.BooleanField(
        default=False,
    )

    is_award_manager = models.BooleanField(
        default=False,
    )

    is_judge_manager = models.BooleanField(
        default=False,
    )

    is_chart_manager = models.BooleanField(
        default=False,
    )


    # Methods
    def save(self, *args, **kwargs):
        self.nomen = self.name
        super().save(*args, **kwargs)

    # Internals
    class JSONAPIMeta:
        resource_name = "office"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return False

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return False


class Officer(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    STATUS = Choices(
        (-10, 'inactive', 'Inactive',),
        (0, 'new', 'New',),
        (10, 'active', 'Active',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.active,
    )

    start_date = models.DateField(
        null=True,
        blank=True,
    )

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    # FKs
    office = models.ForeignKey(
        'Office',
        related_name='officers',
        on_delete=models.CASCADE,
    )

    person = models.ForeignKey(
        'Person',
        related_name='officers',
        on_delete=models.CASCADE,
    )

    organization = models.ForeignKey(
        'Organization',
        related_name='officers',
        on_delete=models.CASCADE,
    )

    # Internals
    class JSONAPIMeta:
        resource_name = "officer"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = " ".join(
            map(
                lambda x: smart_text(x), [
                    self.organization,
                    self.office,
                    self.person,
                ]
            )
        )
        super().save(*args, **kwargs)

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return False

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return False

    # Transitions
    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.active)
    def activate(self, *args, **kwargs):
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.inactive)
    def deactivate(self, *args, **kwargs):
        return


class Organization(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    name = models.CharField(
        help_text="""
            The name of the resource.
        """,
        max_length=255,
    )

    STATUS = Choices(
        (-10, 'inactive', 'Inactive',),
        (0, 'new', 'New',),
        (10, 'active', 'Active',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    KIND = Choices(
        ('International', [
            (1, 'international', "International"),
        ]),
        ('District', [
            (11, 'district', "District"),
            (12, 'noncomp', "Noncompetitive"),
            (13, 'affiliate', "Affiliate"),
        ]),
        ('Division', [
            (21, 'division', "Division"),
        ]),
        ('Chapter', [
            (30, 'chapter', "Chapter"),
        ]),
    )

    kind = models.IntegerField(
        help_text="""
            The kind of organization.
        """,
        choices=KIND,
    )

    short_name = models.CharField(
        help_text="""
            A short-form name for the resource.""",
        blank=True,
        max_length=255,
    )

    code = models.CharField(
        help_text="""
            The chapter code.""",
        max_length=255,
        blank=True,
    )

    start_date = models.DateField(
        null=True,
        blank=True,
    )

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    location = models.CharField(
        help_text="""
            The geographical location of the resource.""",
        max_length=255,
        blank=True,
    )

    website = models.URLField(
        help_text="""
            The website URL of the resource.""",
        blank=True,
    )

    facebook = models.URLField(
        help_text="""
            The facebook URL of the resource.""",
        blank=True,
    )

    twitter = models.CharField(
        help_text="""
            The twitter handle (in form @twitter_handle) of the resource.""",
        blank=True,
        max_length=16,
        validators=[
            RegexValidator(
                regex=r'@([A-Za-z0-9_]+)',
                message="""
                    Must be a single Twitter handle
                    in the form `@twitter_handle`.
                """,
            ),
        ],
    )

    email = models.EmailField(
        help_text="""
            The contact email of the resource.""",
        blank=True,
    )

    phone = models.CharField(
        help_text="""
            The phone number of the resource.  Include country code.""",
        blank=True,
        max_length=25,
    )

    image = models.ImageField(
        upload_to=PathAndRename(),
        max_length=255,
        null=True,
        blank=True,
    )

    description = models.TextField(
        help_text="""
            A description of the organization.  Max 1000 characters.""",
        blank=True,
        max_length=1000,
    )

    notes = models.TextField(
        help_text="""
            Notes (for internal use only).""",
        blank=True,
    )

    bhs_id = models.IntegerField(
        unique=True,
        blank=True,
        null=True,
    )

    org_sort = models.IntegerField(
        unique=True,
        blank=True,
        null=True,
        editable=False,
    )

    # FKs
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        db_index=True,
        on_delete=models.SET_NULL,
    )

    # Internals
    class Meta:
        verbose_name_plural = 'organizations'
        ordering = [
            'org_sort',
        ]
    class JSONAPIMeta:
        resource_name = "organization"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = self.name
        super().save(*args, **kwargs)

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            request.user.person.officers.filter(
                office__is_organization_manager=True,
                status__gt=0,
            ),
        ])


    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            request.user.person.officers.filter(
                office__is_organization_manager=True,
                status__gt=0,
            ),
        ])

    # Transitions
    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.active)
    def activate(self, *args, **kwargs):
        """Activate the Organization."""
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.inactive)
    def deactivate(self, *args, **kwargs):
        """Deactivate the Organization."""
        return


class Panelist(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    STATUS = Choices(
        (-10, 'inactive', 'Inactive',),
        (0, 'new', 'New',),
        (10, 'active', 'Active',),
    )

    status = models.IntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    num = models.IntegerField(
        blank=True,
        null=True,
    )

    KIND = Choices(
        (10, 'official', 'Official'),
        (20, 'practice', 'Practice'),
        (30, 'composite', 'Composite'),
    )

    kind = models.IntegerField(
        choices=KIND,
    )

    CATEGORY = Choices(
        (5, 'drcj', 'DRCJ'),
        (10, 'admin', 'CA'),
        (30, 'music', 'Music'),
        (40, 'performance', 'Performance'),
        (50, 'singing', 'Singing'),
    )

    category = models.IntegerField(
        choices=CATEGORY,
        null=True,
        blank=True,
    )

    # FKs
    round = models.ForeignKey(
        'Round',
        related_name='panelists',
        on_delete=models.CASCADE,
    )

    person = models.ForeignKey(
        'Person',
        related_name='panelists',
        on_delete=models.CASCADE,
    )

    # Internals
    class Meta:
        unique_together = (
            ('round', 'person',)
        )

    class JSONAPIMeta:
        resource_name = "panelist"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = " ".join(filter(None, [
            "{0}".format(self.round),
            "{0}".format(self.person),
            self.get_kind_display(),
        ]))
        super().save(*args, **kwargs)

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            True,
            request.user.person.officers.filter(
                office__is_judge_manager=True,
                status__gt=0,
            )
        ])

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            True,
            request.user.person.officers.filter(
                office__is_judge_manager=True,
                status__gt=0,
            )
        ])


class Participant(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    STATUS = Choices(
        (0, 'new', 'New',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    PART = Choices(
        (-1, 'director', 'Director'),
        (1, 'tenor', 'Tenor'),
        (2, 'lead', 'Lead'),
        (3, 'baritone', 'Baritone'),
        (4, 'bass', 'Bass'),
    )

    part = models.IntegerField(
        choices=PART,
        null=True,
        blank=True,
    )

    # FKs
    entry = models.ForeignKey(
        'Entry',
        related_name='participants',
        on_delete=models.CASCADE,
    )

    member = models.ForeignKey(
        'Member',
        related_name='participants',
        on_delete=models.CASCADE,
    )

    # Internals
    class Meta:
        unique_together = (
            ('entry', 'member',),
        )

    class JSONAPIMeta:
        resource_name = "participant"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = " ".join(
            map(
                lambda x: smart_text(x), [
                    self.entry,
                    self.member,
                ]
            )
        )
        super().save(*args, **kwargs)

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            request.user.person.officers.filter(
                office__is_convention_manager=True,
                status__gt=0,
            ),
            request.user.person.members.filter(
                is_admin=True,
                status__gt=0,
            ),
        ])

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            self.entry.session.convention.assignments.filter(
                person=request.user.person,
                category__lte=10,
                kind=10,
            ),
            self.entry.group.members.filter(
                person=request.user.person,
                is_admin=True,
                status__gt=0,
            ),
        ])


class Person(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    name = models.CharField(
        help_text="""
            The name of the person.""",
        max_length=255,
    )

    STATUS = Choices(
        (-10, 'inactive', 'Inactive',),
        (0, 'new', 'New',),
        (10, 'active', 'Active',),
    )

    status = models.IntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    birth_date = models.DateField(
        null=True,
        blank=True,
    )

    dues_thru = models.DateField(
        null=True,
        blank=True,
    )

    spouse = models.CharField(
        max_length=255,
        blank=True,
    )

    location = models.CharField(
        help_text="""
            The geographical location of the resource.""",
        max_length=255,
        blank=True,
    )

    PART = Choices(
        (-1, 'director', 'Director'),
        (1, 'tenor', 'Tenor'),
        (2, 'lead', 'Lead'),
        (3, 'baritone', 'Baritone'),
        (4, 'bass', 'Bass'),
    )

    part = models.IntegerField(
        choices=PART,
        null=True,
        blank=True,
    )

    website = models.URLField(
        help_text="""
            The website URL of the resource.""",
        blank=True,
    )

    facebook = models.URLField(
        help_text="""
            The facebook URL of the resource.""",
        blank=True,
    )

    twitter = models.CharField(
        help_text="""
            The twitter handle (in form @twitter_handle) of the resource.""",
        blank=True,
        max_length=16,
        validators=[
            RegexValidator(
                regex=r'@([A-Za-z0-9_]+)',
                message="""
                    Must be a single Twitter handle
                    in the form `@twitter_handle`.
                """,
            ),
        ],
    )

    email = models.EmailField(
        help_text="""
            The contact email of the resource.""",
        blank=True,
        null=True,
        unique=True,
    )

    phone = models.CharField(
        help_text="""
            The phone number of the resource.  Include country code.""",
        blank=True,
        max_length=25,
    )

    address = models.TextField(
        help_text="""
            The complete address of the resource.""",
        blank=True,
        max_length=1000,
    )

    home_phone = models.CharField(
        help_text="""
            The home phone number of the resource.  Include country code.""",
        blank=True,
        max_length=25,
    )

    work_phone = models.CharField(
        help_text="""
            The work phone number of the resource.  Include country code.""",
        blank=True,
        max_length=25,
    )

    cell_phone = models.CharField(
        help_text="""
            The cell phone number of the resource.  Include country code.""",
        blank=True,
        max_length=25,
    )

    airports = ArrayField(
        base_field=models.CharField(
            blank=True,
            max_length=3,
        ),
        null=True,
        blank=True,
    )

    image = models.ImageField(
        upload_to=PathAndRename(),
        max_length=255,
        null=True,
        blank=True,
    )

    description = models.TextField(
        help_text="""
            A bio of the person.  Max 1000 characters.""",
        blank=True,
        max_length=1000,
    )

    notes = models.TextField(
        help_text="""
            Notes (for internal use only).""",
        blank=True,
    )

    bhs_id = models.IntegerField(
        null=True,
        blank=True,
        unique=True,
    )

    # Denormalizations
    last_name = models.CharField(
        help_text="""
            The name of the resource.""",
        max_length=255,
        default='',
    )

    @cached_property
    def is_convention_manager(self):
        return bool(self.officers.filter(
            office__is_convention_manager=True,
            status__gt=0,
        ))

    @cached_property
    def is_session_manager(self):
        return bool(self.officers.filter(
            office__is_session_manager=True,
            status__gt=0,
        ))

    @cached_property
    def is_scoring_manager(self):
        return bool(self.officers.filter(
            office__is_scoring_manager=True,
            status__gt=0,
        ))

    @cached_property
    def is_organization_manager(self):
        return bool(self.officers.filter(
            office__is_organization_manager=True,
            status__gt=0,
        ))

    @cached_property
    def is_group_manager(self):
        return bool(self.members.filter(
            status__gt=0,
        ))

    @cached_property
    def is_person_manager(self):
        return bool(self.officers.filter(
            office__is_person_manager=True,
            status__gt=0,
        ))

    @cached_property
    def is_award_manager(self):
        return bool(self.officers.filter(
            office__is_award_manager=True,
            status__gt=0,
        ))

    @cached_property
    def is_judge_manager(self):
        return bool(self.officers.filter(
            office__is_judge_manager=True,
            status__gt=0,
        ))

    @cached_property
    def is_chart_manager(self):
        return bool(self.officers.filter(
            office__is_chart_manager=True,
            status__gt=0,
        ))


    @cached_property
    def first_name(self):
        if self.name:
            name = HumanName(self.name)
            return name.first
        else:
            return None

    @cached_property
    def nick_name(self):
        if self.name:
            name = HumanName(self.name)
            return name.nickname
        else:
            return None

    @cached_property
    def common_name(self):
        if self.name:
            name = HumanName(self.name)
            nickname = name.nickname
            if nickname:
                first = nickname
            else:
                first = name.first
            last = name.last
            return "{0} {1}".format(first, last)
        else:
            return None

    @cached_property
    def full_name(self):
        if self.name:
            name = HumanName(self.name)
            full = []
            full.append(name.first)
            full.append(name.middle)
            full.append(name.last)
            full.append(name.suffix)
            full.append(name.nickname)
            return " ".join(filter(None, full))
        else:
            return None

    @cached_property
    def formal_name(self):
        if self.name:
            name = HumanName(self.name)
            formal = []
            formal.append(name.title)
            formal.append(name.first)
            formal.append(name.middle)
            formal.append(name.last)
            formal.append(name.suffix)
            return " ".join(filter(None, formal))
        else:
            return None

    # Internals
    class JSONAPIMeta:
        resource_name = "person"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        if self.name:
            name = HumanName(self.name)
            self.last_name = name.last
        else:
            self.last_name = None
        self.nomen = " ".join(
            map(
                lambda x: smart_text(x),
                filter(
                    None, [
                        self.name,
                        self.bhs_id,
                    ]
                )
            )
        )
        super().save(*args, **kwargs)

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return True


    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            self == request.user.person,
        ])


class Repertory(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    STATUS = Choices(
        (-10, 'inactive', 'Inactive',),
        (0, 'new', 'New'),
        (10, 'active', 'Active'),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    # FKs
    group = models.ForeignKey(
        'Group',
        related_name='repertories',
        on_delete=models.CASCADE,
    )

    chart = models.ForeignKey(
        'Chart',
        related_name='repertories',
        on_delete=models.CASCADE,
    )

    # Internals
    class Meta:
        verbose_name_plural = 'repertories'
        unique_together = (
            ('group', 'chart',),
        )

    class JSONAPIMeta:
        resource_name = "repertory"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = " ".join(
            map(
                lambda x: smart_text(x), [
                    self.group,
                    self.chart,
                ]
            )
        )
        super().save(*args, **kwargs)

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return any([
            request.user.person.officers.filter(
                office__is_convention_manager=True,
                status__gt=0,
            ),
            request.user.person.officers.filter(
                office__is_scoring_manager=True,
                status__gt=0,
            ),
            request.user.person.members.filter(
                is_admin=True,
                status__gt=0,
            ),
        ])


    @allow_staff_or_superuser
    @authenticated_users
    def has_object_read_permission(self, request):
        return any([
            self.group.members.filter(
                person=request.user.person,
                is_admin=True,
                status__gt=0,
            ),
            request.user.person.officers.filter(
                office__is_convention_manager=True,
                status__gt=0,
            ),
            request.user.person.officers.filter(
                office__is_scoring_manager=True,
                status__gt=0,
            ),
        ])


    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            request.user.person.officers.filter(
                office__is_convention_manager=True,
                status__gt=0,
            ),
            request.user.person.officers.filter(
                office__is_scoring_manager=True,
                status__gt=0,
            ),
            request.user.person.members.filter(
                is_admin=True,
                status__gt=0,
            ),
        ])

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            self.group.members.filter(
                person=request.user.person,
                is_admin=True,
                status__gt=0,
            ),
            request.user.person.officers.filter(
                office__is_convention_manager=True,
                status__gt=0,
            ),
            request.user.person.officers.filter(
                office__is_scoring_manager=True,
                status__gt=0,
            ),
        ])

    # Transitions
    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.active)
    def activate(self, *args, **kwargs):
        """Activate the Repertory."""
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.inactive)
    def deactivate(self, *args, **kwargs):
        """Deactivate the Repertory."""
        return


class Round(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    STATUS = Choices(
        (0, 'new', 'New',),
        (2, 'listed', 'Listed',),
        (4, 'opened', 'Opened',),
        (8, 'closed', 'Closed',),
        (10, 'verified', 'Verified',),
        (15, 'prepared', 'Prepared',),
        (20, 'started', 'Started',),
        # (25, 'ranked', 'Ranked',),
        (30, 'finished', 'Finished',),
        # (40, 'drafted', 'Drafted',),
        (50, 'announced', 'Announced',),
        # (50, 'final', 'Final',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    KIND = Choices(
        (1, 'finals', 'Finals'),
        (2, 'semis', 'Semi-Finals'),
        (3, 'quarters', 'Quarter-Finals'),
    )

    kind = models.IntegerField(
        choices=KIND,
    )

    num = models.IntegerField(
    )

    ann_pdf = models.FileField(
        upload_to=PathAndRename(
            prefix='ann',
        ),
        max_length=255,
        null=True,
        blank=True,
        storage=RawMediaCloudinaryStorage(),
    )

    # FKs
    session = models.ForeignKey(
        'Session',
        related_name='rounds',
        on_delete=models.CASCADE,
    )

    # Internals
    class Meta:
        unique_together = (
            ('session', 'kind',),
        )

    class JSONAPIMeta:
        resource_name = "round"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = " ".join(
            map(
                lambda x: smart_text(x), [
                    self.session,
                    self.get_kind_display(),
                ]
            )
        )
        super().save(*args, **kwargs)

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            request.user.person.officers.filter(
                office__is_scoring_manager=True,
                status__gt=0,
            ),
        ])

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            self.session.convention.assignments.filter(
                person=request.user.person,
                category__in=[10,20],
                kind=10,
            ),
        ])

    # Methods
    def ranking(self, point_total):
        if not point_total:
            return None
        appearances = self.appearances.all()
        points = [appearance.calculate_tot_points() for appearance in appearances]
        points = sorted(points, reverse=True)
        ranking = Ranking(points, start=1)
        rank = ranking.rank(point_total)
        return rank

    def print_ann(self):
        primary = self.session.contests.get(is_primary=True)
        contests = self.session.contests.filter(is_primary=False)
        winners = []
        for contest in contests:
            winner = contest.contestants.get(rank=1)
            winners.append(winner)
        medalists = []
        for contestant in primary.contestants.order_by('-rank'):
            medalists.append(contestant)
        medalists = medalists[-5:]
        tem = get_template('ann.html')
        template = tem.render(context={
            'primary': primary,
            'contests': contests,
            'winners': winners,
            'medalists': medalists,
        })
        try:
            create_response = doc_api.create_doc({
                "test": True,
                "document_content": template,
                "name": "announcements-{0}.pdf".format(id),
                "document_type": "pdf",
            })
            f = ContentFile(create_response)
            self.ann_pdf.save(
                "{0}.pdf".format(id),
                f
            )
            self.save()
        except docraptor.rest.ApiException as error:
            print(error)
        return "Complete"

    # Transitions
    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.verified)
    def verify(self, *args, **kwargs):
        """Confirm panel and appearances"""
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.prepared)
    def prepare(self, *args, **kwargs):
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.started)
    def start(self, *args, **kwargs):
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.finished)
    def finish(self, *args, **kwargs):
        """Separate advancers and finishers"""
        # TODO This probably should not be hard-coded.
        if self.kind == self.KIND.finals:
            for appearance in self.appearances.all():
                appearance.draw = -1
                appearance.save()
            entries = self.session.entries.exclude(
                status=self.session.entries.model.STATUS.scratched,
            )
            for entry in entries:
                entry.calculate_pdf()
                entry.save()
            contests = self.session.contests.all()
            for contest in contests:
                for contestant in contest.contestants.all():
                    contestant.calculate()
                    contestant.save()
            foo = self.print_ann()
            return
        if self.kind == self.KIND.quarters:
            spots = 20
        elif self.kind == self.KIND.semis:
            spots = 10
        else:
            raise RuntimeError('No round kind.')
        # Build list of advancing appearances to number of spots available
        ordered_entries = self.session.entries.annotate(
            tot=models.Sum('appearances__songs__scores__points')
        ).order_by('-tot')
        # Check for tie at cutoff
        if spots:
            cutoff = ordered_entries[spots-1:spots][0].tot
            plus_one = ordered_entries[spots:spots+1][0].tot
            while cutoff == plus_one:
                spots += 1
                cutoff = ordered_entries[spots-1:spots][0].tot
                plus_one = ordered_entries[spots:spots+1][0].tot

        # Get Advancers and finishers
        advancers = list(ordered_entries[:spots])
        cutdown = ordered_entries.filter(
            appearances__round=self,
        )
        finishers = list(cutdown[spots:])

        # Randomize Advancers
        random.shuffle(list(advancers))

        # Set Draw
        i = 1
        for entry in advancers:
            appearance = self.appearances.get(entry=entry)
            appearance.draw = i
            appearance.save()
            i += 1

        # Set draw on finishers to negative one.
        for entry in finishers:
            appearance = self.appearances.get(entry=entry)
            appearance.draw = -1
            appearance.save()

        # TODO Bypassing all this in favor of International-only

        # # Create appearances accordingly
        # # Instantiate the advancing list
        # advancing = []
        # # Only address multi-round contests; single-round awards do not proceed.
        # for contest in self.session.contests.filter(award__rounds__gt=1):
        #     # Qualifiers have an absolute score cutoff
        #     if not contest.award.parent:
        #         # Uses absolute cutoff.
        #         contestants = contest.contestants.filter(
        #             tot_score__gte=contest.award.advance,
        #         )
        #         for contestant in contestants:
        #             advancing.append(contestant.entry)
        #     # Championships are relative.
        #     else:
        #         # Get the top scorer
        #         top = contest.contestants.filter(
        #             rank=1,
        #         ).first()
        #         # Derive the approve threshold from that top score.
        #         approve = top.calculate_tot_score() - 4.0
        #         contestants = contest.contestants.filter(
        #             tot_score__gte=approve,
        #         )
        #         for contestant in contestants:
        #             advancing.append(contestant.entry)
        # # Remove duplicates
        # advancing = list(set(advancing))
        # # Append up to spots available.
        # diff = spots - len(advancing)
        # if diff > 0:
        #     adds = self.appearances.filter(
        #         entry__contestants__contest__award__rounds__gt=1,
        #     ).exclude(
        #         entry__in=advancing,
        #     ).order_by(
        #         '-tot_points',
        #     )[:diff]
        #     for a in adds:
        #         advancing.append(a.entry)
        # random.shuffle(advancing)
        # i = 1
        # for entry in advancing:
        #     next_round.appearances.get_or_create(
        #         entry=entry,
        #         num=i,
        #     )
        #     i += 1
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.announced)
    def announce(self, *args, **kwargs):
        if self.kind != self.KIND.finals:
            round = self.session.rounds.create(
                num=self.num + 1,
                kind=self.kind - 1,
            )
            for appearance in self.appearances.filter(draw__gt=0):
                round.appearances.create(
                    entry=appearance.entry,
                    num=appearance.draw,
                    status=appearance.STATUS.published,
                )
            for appearance in self.appearances.filter(draw__lte=0):
                e = appearance.entry
                e.complete()
                e.save()
            for assignment in self.session.convention.assignments.filter(
                status=Assignment.STATUS.active,
            ):
                round.panelists.create(
                    kind=assignment.kind,
                    category=assignment.category,
                    person=assignment.person,
                )
            round.verify()
            round.save()
            return


class Score(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    STATUS = Choices(
        (0, 'new', 'New',),
        (10, 'verified', 'Verified',),
        # (20, 'entered', 'Entered',),
        (25, 'cleared', 'Cleared',),
        (30, 'flagged', 'Flagged',),
        (35, 'revised', 'Revised',),
        (40, 'confirmed', 'Confirmed',),
        # (50, 'final', 'Final',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    CATEGORY = Choices(
        (30, 'music', 'Music'),
        (40, 'performance', 'Performance'),
        (50, 'singing', 'Singing'),
    )

    category = models.IntegerField(
        choices=CATEGORY,
    )

    KIND = Choices(
        (10, 'official', 'Official'),
        (20, 'practice', 'Practice'),
        (30, 'composite', 'Composite'),
    )

    kind = models.IntegerField(
        choices=KIND,
    )

    num = models.IntegerField(
        null=True,
        blank=True,
    )

    points = models.IntegerField(
        help_text="""
            The number of points (0-100)""",
        null=True,
        blank=True,
        validators=[
            MaxValueValidator(
                100,
                message='Points must be between 0 - 100',
            ),
            MinValueValidator(
                0,
                message='Points must be between 0 - 100',
            ),
        ]
    )

    original = models.IntegerField(
        help_text="""
            The original score (before revision).""",
        null=True,
        blank=True,
        validators=[
            MaxValueValidator(
                100,
                message='Points must be between 0 - 100',
            ),
            MinValueValidator(
                0,
                message='Points must be between 0 - 100',
            ),
        ]
    )

    VIOLATION = Choices(
        (10, 'general', 'General'),
    )

    violation = FSMIntegerField(
        choices=VIOLATION,
        null=True,
        blank=True,
    )

    penalty = models.IntegerField(
        help_text="""
            The penalty (0-100)""",
        null=True,
        blank=True,
        validators=[
            MaxValueValidator(
                100,
                message='Points must be between 0 - 100',
            ),
            MinValueValidator(
                0,
                message='Points must be between 0 - 100',
            ),
        ]
    )

    is_flagged = models.BooleanField(
        default=False,
    )

    # FKs
    song = models.ForeignKey(
        'Song',
        related_name='scores',
        on_delete=models.CASCADE,
    )

    # person = models.ForeignKey(
    #     'Person',
    #     related_name='scores',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    # )

    panelist = models.ForeignKey(
        'Panelist',
        related_name='scores',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class JSONAPIMeta:
        resource_name = "score"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = str(self.pk)
        super().save(*args, **kwargs)

    # Methods
    def verify(self):
        variance = False
        mus_avg = self.song.scores.filter(
            kind=self.song.scores.model.KIND.official,
            category=self.song.scores.model.CATEGORY.music,
        ).aggregate(
            avg=models.Avg('points')
        )['avg']
        if self.category == self.CATEGORY.music:
            if abs(self.points - mus_avg) > 5:
                log.info("Variance Music {0}".format(self))
                variance = True
        per_avg = self.song.scores.filter(
            kind=self.song.scores.model.KIND.official,
            category=self.song.scores.model.CATEGORY.performance,
        ).aggregate(
            avg=models.Avg('points')
        )['avg']
        if self.category == self.CATEGORY.performance:
            if abs(self.points - per_avg) > 5:
                log.info("Variance Performance {0}".format(self))
                variance = True
        sng_avg = self.song.scores.filter(
            kind=self.song.scores.model.KIND.official,
            category=self.song.scores.model.CATEGORY.singing,
        ).aggregate(
            avg=models.Avg('points')
        )['avg']
        if self.category == self.CATEGORY.singing:
            if abs(self.points - sng_avg) > 5:
                log.info("Variance Singing {0}".format(self))
                variance = True
        ordered_asc = self.song.scores.filter(
            kind=self.song.scores.model.KIND.official,
        ).order_by('points')
        if ordered_asc[1].points - ordered_asc[0].points > 5 and ordered_asc[0].points == self.points:
            log.info("Variance Low {0}".format(self))
            variance = True
        ordered_dsc = self.song.scores.filter(
            kind=self.song.scores.model.KIND.official,
        ).order_by('-points')
        if ordered_dsc[0].points - ordered_dsc[1].points > 5 and ordered_dsc[0].points == self.points:
            log.info("Variance High {0}".format(self))
            variance = True
        if variance:
            self.original = self.points
            self.is_flagged = True
            self.save()
        return variance

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_read_permission(request):
        return any([
            True,
            request.user.person.officers.filter(
                office__is_scoring_manager=True,
                status__gt=0,
            ),
            request.user.person.officers.filter(
                office__is_group_manager=True,
                status__gt=0,
            ),
        ])


    @allow_staff_or_superuser
    @authenticated_users
    def has_object_read_permission(self, request):
        return any([
            # self.song.appearance.entry.entity.officers.filter(
            #     person=request.user.person,
            #     office__is_group_manager=True,
            #     status__gt=0,
            # ),
        ])


    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            request.user.person.officers.filter(
                office__is_scoring_manager=True,
                status__gt=0,
            ),
        ])

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            self.song.appearance.round.session.convention.assignments.filter(
                person=request.user.person,
                category__lt=30,
                kind=10,
            ),
        ])


class Session(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    STATUS = Choices(
        (0, 'new', 'New',),
        (4, 'opened', 'Opened',),
        (8, 'closed', 'Closed',),
        (10, 'verified', 'Verified',),
        (20, 'started', 'Started',),
        # (25, 'ranked', 'Ranked',),
        (30, 'finished', 'Finished',),
        # (40, 'drafted', 'Drafted',),
        (45, 'announced', 'Announced',),
        (95, 'archived', 'Archived',),
        # (50, 'final', 'Final',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    KIND = Choices(
        (32, 'chorus', "Chorus"),
        (33, 'vlq', "Very Large Quartet"),
        (34, 'mixed', "Mixed Group"),
        (41, 'quartet', "Quartet"),
    )

    kind = models.IntegerField(
        help_text="""
            The kind of session.  Generally this will be either quartet or chorus.
        """,
        choices=KIND,
    )

    is_invitational = models.BooleanField(
        help_text="""Invite-only (v. Open).""",
        default=False,
    )

    scoresheet = models.FileField(
        upload_to=PathAndRename(
            prefix='scoresheet',
        ),
        max_length=255,
        null=True,
        blank=True,
        storage=RawMediaCloudinaryStorage(),
    )

    bbscores = models.FileField(
        upload_to=PathAndRename(
            prefix='bbscores',
        ),
        max_length=255,
        null=True,
        blank=True,
        storage=RawMediaCloudinaryStorage(),
    )

    oss_pdf = models.FileField(
        upload_to=PathAndRename(
            prefix='oss',
        ),
        max_length=255,
        null=True,
        blank=True,
        storage=RawMediaCloudinaryStorage(),
    )

    ann_pdf = models.FileField(
        upload_to=PathAndRename(
            prefix='announcements',
        ),
        max_length=255,
        null=True,
        blank=True,
        storage=RawMediaCloudinaryStorage(),
    )

    num_rounds = models.IntegerField(
        null=True,
        blank=True,
    )

    # FKs
    convention = models.ForeignKey(
        'Convention',
        related_name='sessions',
        on_delete=models.CASCADE,
    )

    # Internals
    class JSONAPIMeta:
        resource_name = "session"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = " ".join(
            map(
                lambda x: smart_text(x), [
                    self.convention,
                    self.get_kind_display(),
                    'Session',
                ]
            )
        )
        super().save(*args, **kwargs)

    # Methods
    def print_oss(self):
        session = self
        entries = self.entries.filter(
            status=self.entries.model.STATUS.complete,
        )
        appearances = entry.appearances.order_by(
            'round__kind',
        )
        assignments = session.convention.assignments.filter(
            category__gt=20,
        ).order_by(
            'category',
            'kind',
            'nomen',
        )
        tem = get_template('csa.html')
        template = tem.render(context={
            'entry': entry,
            'appearances': appearances,
            'assignments': assignments,
            'contestants': contestants,
        })
        try:
            create_response = doc_api.create_doc({
                "test": True,
                "document_content": template,
                "name": "csa-{0}.pdf".format(id),
                "document_type": "pdf",
            })
            f = ContentFile(create_response)
            entry.csa_pdf.save(
                "{0}.pdf".format(id),
                f
            )
            entry.save()
        except docraptor.rest.ApiException as error:
            print(error)
        return "Complete"

    # Session Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return any([
            True,
        ])


    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return any([
            True,
        ])


    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            request.user.person.officers.filter(
                office__is_convention_manager=True,
                status__gt=0,
            ),
        ])

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            self.convention.assignments.filter(
                person=request.user.person,
                category__lt=30,
                kind=10,
            ),
        ])

    # Session Transitions
    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.opened)
    def open(self, *args, **kwargs):
        """Make session available for entry."""
        if not self.is_invitational:
            send_session(self, 'session_open.txt')
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.closed)
    def close(self, *args, **kwargs):
        """Make session unavailable and set initial draw."""
        entries = self.entries.filter(
            status=self.entries.model.STATUS.approved,
        )
        i = 1
        for entry in entries:
            entry.draw = i
            entry.save()
            i += 1
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.verified)
    def verify(self, *args, **kwargs):
        """Make draw public."""
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.started)
    def start(self, *args, **kwargs):
        """Create round, seat panel, copy draw."""
        #  Create the BBScores export file
        create_bbscores(self)
        self.bbscores.save(
            'bbscores.csv',
            File(open('bbscores.csv')),
        )
        # Build the rounds
        Assignment = config.get_model('Assignment')
        Slot = config.get_model('Slot')
        Entry = config.get_model('Entry')
        Appearance = config.get_model('Appearance')
        max = self.contests.all().aggregate(
            max=models.Max('award__rounds')
        )['max']
        i = 1
        round = self.rounds.create(
            num=i,
            kind=max,
        )
        for entry in self.entries.filter(status=Entry.STATUS.approved):
            slot = Slot.objects.create(
                num=entry.draw,
                round=round,
            )
            round.appearances.create(
                entry=entry,
                slot=slot,
                num=entry.draw,
                status=Appearance.STATUS.published,
            )
        for assignment in self.convention.assignments.filter(
            status=Assignment.STATUS.active,
        ):
            round.panelists.create(
                kind=assignment.kind,
                category=assignment.category,
                person=assignment.person,
            )
        round.verify()
        round.save()
        return


    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.finished)
    def finish(self, *args, **kwargs):
        session = self
        for entry in session.entries.all():
            for appearance in entry.appearances.all():
                for song in appearance.songs.all():
                    song.calculate()
                    song.save()
                appearance.calculate()
                appearance.save()
            entry.calculate()
            entry.save()
        return

    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.announced)
    def announce(self, *args, **kwargs):
        return


class Slot(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    STATUS = Choices(
        (0, 'new', 'New',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    num = models.IntegerField(
    )

    location = models.CharField(
        max_length=255,
        blank=True,
    )

    photo = models.DateTimeField(
        null=True,
        blank=True,
    )

    arrive = models.DateTimeField(
        null=True,
        blank=True,
    )

    depart = models.DateTimeField(
        null=True,
        blank=True,
    )

    backstage = models.DateTimeField(
        null=True,
        blank=True,
    )

    onstage = models.DateTimeField(
        null=True,
        blank=True,
    )

    # FKs
    round = models.ForeignKey(
        'Round',
        related_name='slots',
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = (
            ('round', 'num',),
        )

    class JSONAPIMeta:
        resource_name = "slot"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = " ".join(
            map(
                lambda x: smart_text(x), [
                    self.round,
                    self.num,
                ]
            )
        )
        super().save(*args, **kwargs)

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return any([
            True,
        ])


    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return any([
            True,
        ])


    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            request.user.person.officers.filter(
                office__is_convention_manager=True,
                status__gt=0,
            ),
        ])

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            self.round.session.convention.assignments.filter(
                person=request.user.person,
                category__lt=30,
                kind=10,
            ),
        ])


class Song(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    STATUS = Choices(
        (0, 'new', 'New',),
        (10, 'verified', 'Verified',),
        # (20, 'entered', 'Entered',),
        # (30, 'flagged', 'Flagged',),
        # (35, 'verified', 'Verified',),
        (38, 'finished', 'Finished',),
        (40, 'confirmed', 'Confirmed',),
        (50, 'final', 'Final',),
        (90, 'announced', 'Announced',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    num = models.IntegerField(
    )

    # Privates
    rank = models.IntegerField(
        null=True,
        blank=True,
    )

    mus_points = models.IntegerField(
        null=True,
        blank=True,
    )

    per_points = models.IntegerField(
        null=True,
        blank=True,
    )

    sng_points = models.IntegerField(
        null=True,
        blank=True,
    )

    tot_points = models.IntegerField(
        null=True,
        blank=True,
    )

    mus_score = models.FloatField(
        null=True,
        blank=True,
    )

    per_score = models.FloatField(
        null=True,
        blank=True,
    )

    sng_score = models.FloatField(
        null=True,
        blank=True,
    )

    tot_score = models.FloatField(
        null=True,
        blank=True,
    )

    # FKs
    appearance = models.ForeignKey(
        'Appearance',
        related_name='songs',
        on_delete=models.CASCADE,
    )

    chart = models.ForeignKey(
        'Chart',
        related_name='songs',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    # Internals
    class Meta:
        unique_together = (
            ('appearance', 'num',),
        )

    class JSONAPIMeta:
        resource_name = "song"

    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = " ".join(
            map(
                lambda x: smart_text(x), [
                    self.appearance,
                    self.num,
                ]
            )
        )
        super().save(*args, **kwargs)

    # Methods
    def calculate(self, *args, **kwargs):
        self.mus_points = self.calculate_mus_points()
        self.per_points = self.calculate_per_points()
        self.sng_points = self.calculate_sng_points()
        self.tot_points = self.calculate_tot_points()
        self.mus_score = self.calculate_mus_score()
        self.per_score = self.calculate_per_score()
        self.sng_score = self.calculate_sng_score()
        self.tot_score = self.calculate_tot_score()

    def calculate_mus_points(self):
        return self.scores.filter(
            kind=10,
            category=30,
        ).aggregate(
            tot=models.Sum('points')
        )['tot']

    def calculate_per_points(self):
        return self.scores.filter(
            kind=10,
            category=40,
        ).aggregate(
            tot=models.Sum('points')
        )['tot']

    def calculate_sng_points(self):
        return self.scores.filter(
            kind=10,
            category=50,
        ).aggregate(
            tot=models.Sum('points')
        )['tot']

    def calculate_tot_points(self):
        return self.scores.filter(
            kind=10,
        ).aggregate(
            tot=models.Sum('points')
        )['tot']

    def calculate_mus_score(self):
        return self.scores.filter(
            kind=10,
            category=30,
        ).aggregate(
            tot=models.Avg('points')
        )['tot']

    def calculate_per_score(self):
        return self.scores.filter(
            kind=10,
            category=40,
        ).aggregate(
            tot=models.Avg('points')
        )['tot']

    def calculate_sng_score(self):
        return self.scores.filter(
            kind=10,
            category=50,
        ).aggregate(
            tot=models.Avg('points')
        )['tot']

    def calculate_tot_score(self):
        return self.scores.filter(
            kind=10,
        ).aggregate(
            tot=models.Avg('points')
        )['tot']

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return any([
            True,
        ])


    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return any([
            True,
        ])


    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            True,
            # request.user.person.officers.filter(
            #     office__is_scoring_manager=True,
            #     status__gt=0,
            # ),
        ])

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            self.appearance.round.session.convention.assignments.filter(
                person=request.user.person,
                category__lt=30,
                kind=10,
            ),
        ])

    # Transitions
    @fsm_log_by
    @transition(field=status, source='*', target=STATUS.announced)
    def announce(self, *args, **kwargs):
        return


class Venue(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    nomen = models.CharField(
        max_length=255,
        editable=False,
    )

    name = models.CharField(
        help_text="""
            The name of the resource.""",
        max_length=255,
    )

    STATUS = Choices(
        (-10, 'inactive', 'Inactive',),
        (0, 'new', 'New',),
        (10, 'active', 'Active',),
    )

    status = FSMIntegerField(
        choices=STATUS,
        default=STATUS.new,
    )

    location = models.CharField(
        max_length=255,
        blank=True,
    )

    city = models.CharField(
        max_length=255,
        blank=True,
    )

    state = models.CharField(
        max_length=255,
        blank=True,
    )

    airport = models.CharField(
        max_length=3,
        blank=True,
    )

    timezone = TimeZoneField(
        help_text="""
            The local timezone of the venue.""",
        blank=True,
    )

    # Methods
    def __str__(self):
        return self.nomen if self.nomen else str(self.pk)

    def save(self, *args, **kwargs):
        self.nomen = self.name
        super().save(*args, **kwargs)

    # Internals
    class JSONAPIMeta:
        resource_name = "venue"

    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return any([
            True,
        ])


    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return any([
            True,
        ])


    @staticmethod
    @allow_staff_or_superuser
    @authenticated_users
    def has_write_permission(request):
        return any([
            request.user.person.officers.filter(
                office__is_convention_manager=True,
                status__gt=0,
            ),
        ])

    @allow_staff_or_superuser
    @authenticated_users
    def has_object_write_permission(self, request):
        return any([
            request.user.person.officers.filter(
                office__is_convention_manager=True,
                status__gt=0,
            ),
        ])


class User(AbstractBaseUser):
    USERNAME_FIELD = settings.USERNAME_FIELD
    REQUIRED_FIELDS = settings.REQUIRED_FIELDS

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    email = models.EmailField(
        unique=True,
        editable=False,
    )

    auth0_id = models.CharField(
        max_length=100,
        unique=True,
        editable=False,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    is_staff = models.BooleanField(
        default=False,
    )

    objects = UserManager()

    # FKs
    person = OneToOneOrNoneField(
        'Person',
        null=True,
        blank=True,
        related_name='user',
    )

    @property
    def is_superuser(self):
        return self.is_staff

    class JSONAPIMeta:
        resource_name = "user"

    # Methods
    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff


    # Permissions
    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return False

    @staticmethod
    @allow_staff_or_superuser
    def has_write_permission(request):
        return False

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        if request.user.is_authenticated():
            return self == request.user
        return False

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        if request.user.is_authenticated():
            return self == request.user
        return False
