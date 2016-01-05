import logging
log = logging.getLogger(__name__)

from rest_framework import (
    viewsets,
    permissions,
)

from drf_haystack.viewsets import HaystackViewSet

from .models import (
    Arranger,
    Award,
    Chapter,
    Convention,
    Session,
    Contest,
    Contestant,
    Round,
    Group,
    Performer,
    Tune,
    Person,
    Song,
    Singer,
    Score,
    Director,
    Catalog,
    Judge,
    Performance,
    Organization,
)

from .serializers import (
    ArrangerSerializer,
    AwardSerializer,
    ChapterSerializer,
    ConventionSerializer,
    SessionSerializer,
    ContestSerializer,
    ContestantSerializer,
    RoundSerializer,
    GroupSerializer,
    PerformerSerializer,
    TuneSerializer,
    PersonSerializer,
    SearchSerializer,
    SongSerializer,
    SingerSerializer,
    ScoreSerializer,
    DirectorSerializer,
    CatalogSerializer,
    JudgeSerializer,
    PerformanceSerializer,
    OrganizationSerializer,
)


class ArrangerViewSet(viewsets.ModelViewSet):
    queryset = Arranger.objects.select_related(
        'catalog',
        'person',
    )
    serializer_class = ArrangerSerializer
    lookup_field = 'slug'


class AwardViewSet(viewsets.ModelViewSet):
    queryset = Award.objects.all()
    serializer_class = AwardSerializer
    lookup_field = 'slug'


class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.select_related(
        'organization',
    )
    serializer_class = ChapterSerializer
    lookup_field = 'slug'


class ContestViewSet(viewsets.ModelViewSet):
    queryset = Contest.objects.select_related(
        'session',
        'award',
    ).filter(
        # history=Session.HISTORY.complete,
    ).prefetch_related(
        'contestants',
    )
    serializer_class = ContestSerializer
    lookup_field = 'slug'


class CatalogViewSet(viewsets.ModelViewSet):
    queryset = Catalog.objects.select_related(
        'tune',
    )
    serializer_class = CatalogSerializer
    lookup_field = 'slug'


class ContestantViewSet(viewsets.ModelViewSet):
    queryset = Contestant.objects.select_related(
        'contest',
        'performer',
    )
    serializer_class = ContestantSerializer
    lookup_field = 'slug'


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.select_related(
        'convention',
    ).filter(
        # history=Session.HISTORY.complete,
    ).prefetch_related(
        'contests',
        'performers',
        'rounds',
        'judges',
    )
    serializer_class = SessionSerializer
    lookup_field = 'slug'


class PerformerViewSet(viewsets.ModelViewSet):
    queryset = Performer.objects.select_related(
        'session',
        'organization',
    ).prefetch_related(
        'performances',
        'contestants',
        'directors',
        'singers',
    )
    serializer_class = PerformerSerializer
    lookup_field = 'slug'


class ConventionViewSet(viewsets.ModelViewSet):
    queryset = Convention.objects.select_related(
        'organization',
    ).exclude(
        status=Convention.STATUS.new,
    ).prefetch_related(
        'sessions',
    )
    serializer_class = ConventionSerializer
    lookup_field = 'slug'


class DirectorViewSet(viewsets.ModelViewSet):
    queryset = Director.objects.select_related(
        'person',
        'performer',
    )
    serializer_class = DirectorSerializer
    lookup_field = 'slug'


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().prefetch_related(
        'performers',
    )
    serializer_class = GroupSerializer
    lookup_field = 'slug'


class JudgeViewSet(viewsets.ModelViewSet):
    queryset = Judge.objects.select_related(
        'session',
        'person',
        'organization',
    ).prefetch_related(
        'scores',
    )
    serializer_class = JudgeSerializer
    lookup_field = 'slug'


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    lookup_field = 'slug'


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.select_related(
        'round',
        'performer',
    ).prefetch_related(
        'songs',
    )
    serializer_class = PerformanceSerializer
    lookup_field = 'slug'


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.prefetch_related(
        # 'catalogs',
        'choruses',
        'quartets',
        'sessions',
    )
    serializer_class = PersonSerializer
    lookup_field = 'slug'


class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.select_related(
        'song',
        'judge',
    )
    serializer_class = ScoreSerializer
    permission_classes = [
        permissions.DjangoModelPermissions,
    ]


class SearchViewSet(HaystackViewSet):
    serializer_class = SearchSerializer


class RoundViewSet(viewsets.ModelViewSet):
    queryset = Round.objects.select_related(
        'session',
    ).prefetch_related(
        'performances',
    )
    serializer_class = RoundSerializer
    lookup_field = 'slug'


class SingerViewSet(viewsets.ModelViewSet):
    queryset = Singer.objects.select_related(
        'person',
        'performer',
    )
    serializer_class = SingerSerializer
    lookup_field = 'slug'


class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.select_related(
        'catalog',
        'performance',
    ).prefetch_related(
        'scores',
    )
    serializer_class = SongSerializer
    lookup_field = 'slug'


class TuneViewSet(viewsets.ModelViewSet):
    queryset = Tune.objects.prefetch_related(
        # 'catalogs',
        'songs',
    )
    serializer_class = TuneSerializer
    lookup_field = 'slug'
