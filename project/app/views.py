# Standard Libary
import logging

# Third-Party
from dry_rest_permissions.generics import DRYPermissions
from django_filters.rest_framework import DjangoFilterBackend
from drf_fsm_transitions.viewset_mixins import (
    get_viewset_transition_action_mixin,
)
from rest_framework import (
    viewsets,
    status,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from rest_framework.decorators import (
    detail_route,
    list_route,
    parser_classes,
)

from rest_framework.parsers import (
    FormParser,
    MultiPartParser,
)

# Local
from .backends import (
    CoalesceFilterBackend,
    ContestScoreFilterBackend,
    PerformanceScoreFilterBackend,
    PerformerScoreFilterBackend,
    SongScoreFilterBackend,
    ScoreFilterBackend,
)

from .filters import (
    AwardFilter,
    CatalogFilter,
    ContestantFilter,
    ConventionFilter,
    EntityFilter,
    PerformerFilter,
    PersonFilter,
    SessionFilter,
    SubmissionFilter,
    VenueFilter,
)

from .models import (
    Assignment,
    Award,
    Catalog,
    Contest,
    ContestScore,
    Contestant,
    ContestantScore,
    Convention,
    Entity,
    Host,
    Membership,
    Office,
    Officer,
    Performance,
    PerformanceScore,
    Performer,
    PerformerScore,
    Person,
    Round,
    Score,
    Session,
    Slot,
    Song,
    SongScore,
    Submission,
    Venue,
    User,
)

from .paginators import (
    PageNumberPagination,
)

from .serializers import (
    AssignmentSerializer,
    AwardSerializer,
    CatalogSerializer,
    ContestantSerializer,
    ContestantScoreSerializer,
    ContestSerializer,
    ContestScoreSerializer,
    ConventionSerializer,
    EntitySerializer,
    MembershipSerializer,
    OfficeSerializer,
    OfficerSerializer,
    HostSerializer,
    PerformanceSerializer,
    PerformanceScoreSerializer,
    PerformerSerializer,
    PerformerScoreSerializer,
    PersonSerializer,
    RoundSerializer,
    ScoreSerializer,
    SessionSerializer,
    SlotSerializer,
    SongSerializer,
    SongScoreSerializer,
    SubmissionSerializer,
    VenueSerializer,
    UserSerializer,
)

log = logging.getLogger(__name__)


class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    filter_class = EntityFilter
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "entity"


class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    filter_class = None
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "membership"


class OfficerViewSet(viewsets.ModelViewSet):
    queryset = Officer.objects.all()
    serializer_class = OfficerSerializer
    filter_class = None
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "officer"


class OfficeViewSet(viewsets.ModelViewSet):
    queryset = Office.objects.all()
    serializer_class = OfficeSerializer
    filter_class = None
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "office"


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related(
        'convention',
        'person',
    )
    serializer_class = AssignmentSerializer
    filter_class = None
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "assignment"


class AwardViewSet(viewsets.ModelViewSet):
    queryset = Award.objects.select_related(
    ).prefetch_related(
        'contests',
    ).order_by(
        '-is_primary',
        'kind',
        'size',
        'scope',
    )
    serializer_class = AwardSerializer
    filter_class = AwardFilter
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "award"


class CatalogViewSet(viewsets.ModelViewSet):
    queryset = Catalog.objects.prefetch_related(
        'submissions',
    )
    serializer_class = CatalogSerializer
    filter_class = CatalogFilter
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "catalog"


class ContestViewSet(viewsets.ModelViewSet):
    queryset = Contest.objects.select_related(
        'session',
        'award',
        'contestscore',
    ).prefetch_related(
        'contestants',
    ).order_by(
        '-session__convention__year',
        'award',
        'session',
    )
    serializer_class = ContestSerializer
    filter_class = None
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "contest"


class ContestScoreViewSet(viewsets.ModelViewSet):
    queryset = ContestScore.objects.select_related(
        'champion',
    )
    serializer_class = ContestScoreSerializer
    filter_class = None
    filter_backends = [
        CoalesceFilterBackend,
        ContestScoreFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "contestscore"


class ContestantViewSet(viewsets.ModelViewSet):
    queryset = Contestant.objects.select_related(
        'performer',
        'contest',
    ).order_by(
        'contest',
    )
    serializer_class = ContestantSerializer
    filter_class = ContestantFilter
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "contestant"


class ContestantScoreViewSet(viewsets.ModelViewSet):
    queryset = ContestantScore.objects.all()
    serializer_class = ContestantScoreSerializer
    filter_class = None
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "contestantscore"


class ConventionViewSet(
    get_viewset_transition_action_mixin(Convention),
    viewsets.ModelViewSet
):
    queryset = Convention.objects.select_related(
        'venue',
    ).prefetch_related(
        'sessions',
    ).order_by(
        'start_date',
    )
    serializer_class = ConventionSerializer
    filter_class = ConventionFilter
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "convention"


class HostViewSet(viewsets.ModelViewSet):
    queryset = Host.objects.select_related(
        'convention',
    )
    serializer_class = HostSerializer
    filter_class = None
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "host"


class PerformanceViewSet(
    get_viewset_transition_action_mixin(Performance),
    viewsets.ModelViewSet,
):
    queryset = Performance.objects.select_related(
        'round',
        'performer',
        'slot',
        'performancescore',
    ).prefetch_related(
        'songs',
    ).order_by(
        'round',
        'num',
    )
    serializer_class = PerformanceSerializer
    filter_class = None
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "performance"


class PerformanceScoreViewSet(viewsets.ModelViewSet):
    queryset = PerformanceScore.objects.order_by(
        'nomen',
    )
    serializer_class = PerformanceScoreSerializer
    filter_class = None
    filter_backends = [
        CoalesceFilterBackend,
        PerformanceScoreFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "performancescore"


class PerformerViewSet(viewsets.ModelViewSet):
    queryset = Performer.objects.select_related(
        'session',
        # 'group',
        'entity',
        'tenor',
        'lead',
        'baritone',
        'bass',
        'director',
        'codirector',
        # 'representing',
        'performerscore',
    ).prefetch_related(
        'submissions',
        'performances',
        'contestants',
    ).order_by(
        'session',
    )
    serializer_class = PerformerSerializer
    filter_class = PerformerFilter
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "performer"


class PerformerScoreViewSet(viewsets.ModelViewSet):
    queryset = PerformerScore.objects.order_by(
        'nomen',
    )
    serializer_class = PerformerScoreSerializer
    filter_class = None
    filter_backends = [
        CoalesceFilterBackend,
        PerformerScoreFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "performerscore"


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.select_related(
        'user',
    ).prefetch_related(
    ).order_by(
        'name',
    )
    serializer_class = PersonSerializer
    filter_class = PersonFilter
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "person"

    @detail_route(methods=['POST'], permission_classes=[AllowAny])
    @parser_classes((FormParser, MultiPartParser,))
    def picture(self, request, *args, **kwargs):
        if 'upload' in request.data:
            person = self.get_object()
            person.picture.delete()

            upload = request.data['upload']

            person.picture.save(upload.name, upload)

            return Response(status=status.HTTP_201_CREATED, headers={'Location': person.picture.url})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class RoundViewSet(
    get_viewset_transition_action_mixin(Round),
    viewsets.ModelViewSet
):
    queryset = Round.objects.select_related(
        'session',
    ).prefetch_related(
        'performances',
        'slots',
    ).order_by(
        'session',
        'kind',
    )
    serializer_class = RoundSerializer
    filter_class = None
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "round"


class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.select_related(
        'song',
        'person',
        'song__performance__performer__session',
        'song__performance__round',
    )
    serializer_class = ScoreSerializer
    filter_class = None
    filter_backends = [
        CoalesceFilterBackend,
        ScoreFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "score"


class SessionViewSet(
    get_viewset_transition_action_mixin(Session),
    viewsets.ModelViewSet
):
    queryset = Session.objects.select_related(
        'convention',
    ).prefetch_related(
        'performers',
        'rounds',
        'contests',
    ).order_by(
        '-start_date',
    )
    serializer_class = SessionSerializer
    filter_class = SessionFilter
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "session"


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.select_related(
        'performer',
    ).prefetch_related(
        'songs',
    )
    serializer_class = SubmissionSerializer
    filter_class = SubmissionFilter
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "submission"


class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.select_related(
        'performance',
        'submission',
        'songscore',
    ).prefetch_related(
        'scores',
    ).order_by(
        'performance',
        'num',
    )
    serializer_class = SongSerializer
    filter_class = None
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "song"


class SongScoreViewSet(viewsets.ModelViewSet):
    queryset = SongScore.objects.order_by(
        'nomen',
    )
    serializer_class = SongScoreSerializer
    filter_class = None
    filter_backends = [
        CoalesceFilterBackend,
        SongScoreFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "songscore"


class SlotViewSet(viewsets.ModelViewSet):
    queryset = Slot.objects.select_related(
        'round',
    ).prefetch_related(
        'performance',
    ).order_by(
        'round',
        'num',
    )
    serializer_class = SlotSerializer
    filter_class = None
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "slot"


class VenueViewSet(viewsets.ModelViewSet):
    queryset = Venue.objects.prefetch_related(
        'conventions',
    ).order_by(
        'name',
    )
    serializer_class = VenueSerializer
    filter_class = VenueFilter
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "venue"


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_class = None
    filter_backends = [
        CoalesceFilterBackend,
        DjangoFilterBackend,
    ]
    pagination_class = PageNumberPagination
    permission_classes = [
        DRYPermissions,
    ]
    resource_name = "user"

    @list_route(methods=['get'], permission_classes=[AllowAny])
    def me(self, request):
        if request.user.is_authenticated:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)
