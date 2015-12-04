from django.contrib import admin

from mptt.admin import MPTTModelAdmin
from fsm_admin.mixins import FSMTransitionMixin

from .inlines import (
    ContestantInline,
    DirectorInline,
    PerformanceInline,
    AwardInline,
    # PlacementInline,
    ContestInline,
    JudgeInline,
    ScoreInline,
    SongStackedInline,
    CertificationInline,
    # SongInline,
    SingerInline,
    SessionInline,
    CompetitorInline,
)

from .models import (
    Arranger,
    Catalog,
    Convention,
    Award,
    Contestant,
    Group,
    Tune,
    Person,
    Song,
    Score,
    Contest,
    Judge,
    Session,
    Performance,
    User,
    Organization,
    Competitor,
)

# from grappelli.forms import GrappelliSortableHiddenMixin
from super_inlines.admin import SuperModelAdmin


# class ArrangersInline(admin.TabularInline):
#     model = Arranger
#     fields = (
#         'song',
#         'person',
#         'part',
#         # 'is_practice',
#     )
#     ordering = (
#         'person',
#     )
#     extra = 0
#     raw_id_fields = (
#         'person',
#     )
#     autocomplete_lookup_fields = {
#         'fk': [
#             'person',
#         ]
#     }
#     can_delete = True
#     show_change_link = True
#     classes = ('grp-collapse grp-closed',)


@admin.register(Competitor)
class CompetitorAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    search_fields = [
        'name',
    ]
    fields = [
        'name',
        ('status', 'status_monitor',),
        'contestant',
        'award',
        'place',
        'men',
    ]
    list_filter = (
        'status',
        'award__contest__convention',
    )

    autocomplete_lookup_fields = {
        'fk': [
            'contestant',
            'award',
        ]
    }
    readonly_fields = [
        'name',
        'status_monitor',
    ]

    raw_id_fields = [
        'contestant',
        'award',
    ]


@admin.register(Contest)
class ContestAdmin(FSMTransitionMixin, admin.ModelAdmin):
    fsm_field = [
        'status',
    ]

    change_list_template = "admin/change_list_filter_sidebar.html"
    save_on_top = True
    fields = [
        'name',
        ('status', 'status_monitor',),
        'convention',
        'kind',
        'size',
        'rounds',
    ]

    list_display = [
        'name',
        'status',
        'convention',
        'kind',
        'size',
        'rounds',
    ]

    raw_id_fields = (
        'convention',
    )

    autocomplete_lookup_fields = {
        'fk': [
            'convention',
        ]
    }

    readonly_fields = [
        'name',
        'status_monitor',
    ]

    inlines = [
        SessionInline,
        JudgeInline,
        AwardInline,
        ContestantInline,
    ]


@admin.register(Arranger)
class ArrangerAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'catalog',
        'person',
    ]


@admin.register(Catalog)
class CatalogAdmin(admin.ModelAdmin):
    list_display = [
        'song_name',
        'tune',
        'bhs_id',
        'bhs_songname',
        'bhs_arranger',
    ]


@admin.register(Award)
class AwardAdmin(FSMTransitionMixin, admin.ModelAdmin):
    fsm_field = [
        'status',
    ]

    inlines = [
        CompetitorInline,
    ]

    change_list_template = "admin/change_list_filter_sidebar.html"
    save_on_top = True
    search_fields = (
        'name',
    )

    list_filter = (
        'status',
        'history',
        'goal',
        'level',
        'kind',
        'year',
        'organization',
        'contest',
    )

    list_display = (
        'name',
        'status',
        'contest',
        'organization',
        'level',
        'kind',
        'goal',
        'year',
        'rounds',
        'qual_score',
    )

    fields = (
        'name',
        ('status', 'status_monitor',),
        ('history', 'history_monitor',),
        'contest',
        'organization',
        'level',
        'kind',
        'goal',
        'year',
        'rounds',
        'qual_score',
    )

    readonly_fields = (
        'name',
        'status_monitor',
        'history_monitor',
    )

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "convention":
    #         try:
    #             parent_obj_id = request.resolver_match.args[0]
    #             obj = Award.objects.get(pk=parent_obj_id)
    #             kwargs["queryset"] = Convention.objects.filter(year=obj.year)
    #         except IndexError:
    #             pass
    #     return super(AwardAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Contestant)
class ContestantAdmin(FSMTransitionMixin, admin.ModelAdmin):
    fsm_field = [
        'status',
    ]

    change_list_template = "admin/change_list_filter_sidebar.html"

    inlines = [
        SingerInline,
        DirectorInline,
        PerformanceInline,
        CompetitorInline,
    ]

    list_display = (
        'name',
        'status',
        'seed',
        'prelim',
        'mus_score',
        'prs_score',
        'sng_score',
        'total_score',
        'men',
        'place',
    )

    search_fields = (
        'name',
    )

    list_filter = (
        'status',
    )

    raw_id_fields = (
        'contest',
        'group',
    )

    autocomplete_lookup_fields = {
        'fk': [
            'contest',
            'group',
        ]
    }
    fields = (
        'name',
        ('status', 'status_monitor',),
        'contest',
        ('group', 'organization',),
        ('seed', 'prelim',),
        ('place', 'men',),
        ('mus_points', 'prs_points', 'sng_points', 'total_points',),
        ('mus_score', 'prs_score', 'sng_score', 'total_score',),
    )

    readonly_fields = (
        'name',
        'status_monitor',
        'mus_points',
        'prs_points',
        'sng_points',
        'total_points',
        'mus_score',
        'prs_score',
        'sng_score',
        'total_score',
    )

    save_on_top = True


@admin.register(Convention)
class ConventionAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    search_fields = (
        'name',
    )

    list_display = (
        'name',
        'status',
        'status_monitor',
        'location',
        'dates',
        'kind',
        'year',
        'organization',
    )

    fields = (
        'name',
        ('status', 'status_monitor',),
        ('location', 'timezone',),
        'dates',
        'organization',
        'kind',
        'year',
    )

    list_filter = (
        'status',
        'kind',
        'year',
        'organization',
    )

    inlines = [
        # AwardInline,
        ContestInline,
        # ContestantInline,
    ]

    readonly_fields = (
        'name',
        'status_monitor',
    )
    save_on_top = True


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
    )

    list_display = (
        'name',
        'status',
        'status_monitor',
        'location',
        'website',
        'facebook',
        'twitter',
        'email',
        'phone',
        'chapter_name',
        'chapter_code',
        'picture',
    )

    fields = (
        'name',
        ('status', 'status_monitor',),
        'kind',
        ('start_date', 'end_date',),
        'location',
        'website',
        'facebook',
        'twitter',
        'email',
        'phone',
        'picture',
        'description',
        ('chapter_name', 'chapter_code',),
        'notes',
    )

    list_filter = (
        'kind',
    )

    inlines = [
        ContestantInline,
    ]

    readonly_fields = (
        'status_monitor',
    )
    save_on_top = True


@admin.register(Judge)
class JudgeAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    save_on_top = True
    fields = [
        'name',
        ('status', 'status_monitor',),
        'contest',
        'person',
        'organization',
        ('category', 'slot',),
    ]

    list_display = [
        'name',
        'status',
        'person',
        'organization',
    ]

    list_filter = (
        'status',
    )

    list_select_related = [
        'organization',
        'contest',
        'person',
    ]

    raw_id_fields = (
        'contest',
        'person',
    )

    autocomplete_lookup_fields = {
        'fk': [
            'contest',
            'person',
        ]
    }

    readonly_fields = [
        'name',
    ]

    inlines = [
        ScoreInline,
    ]


@admin.register(Organization)
class OrganizationAdmin(MPTTModelAdmin):
    pass


@admin.register(Performance)
class PerformanceAdmin(FSMTransitionMixin, SuperModelAdmin):
    fsm_field = [
        'status',
    ]

    save_on_top = True
    change_list_template = "admin/change_list_filter_sidebar.html"

    inlines = [
        SongStackedInline,
        # SessionInline,
    ]
    list_display = [
        'name',
        'status',
        'draw',
        'start_time',
        'total_score',
        'place',
    ]
    list_filter = [
        'status',
        'session',
    ]

    fields = [
        'name',
        ('status', 'status_monitor',),
        'contestant',
        ('draw', 'start_time',),
        ('mus_points', 'prs_points', 'sng_points', 'total_points',),
        ('mus_score', 'prs_score', 'sng_score', 'total_score',),
    ]

    readonly_fields = [
        'name',
        'status_monitor',
        'mus_points',
        'prs_points',
        'sng_points',
        'total_points',
        'mus_score',
        'prs_score',
        'sng_score',
        'total_score',
        'draw',
    ]

    raw_id_fields = (
        'contestant',
    )
    autocomplete_lookup_fields = {
        'fk': [
            'contestant',
        ]
    }

    search_fields = (
        'name',
    )


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    save_on_top = True
    list_display = (
        'name',
        'status',
        'tune',
        'mus_points',
        'prs_points',
        'sng_points',
        'total_points'
    )

    search_fields = (
        'name',
    )

    fields = [
        'name',
        ('status', 'status_monitor',),
        'order',
        ('mus_points', 'prs_points', 'sng_points', 'total_points',),
        ('mus_score', 'prs_score', 'sng_score', 'total_score',),
        'tune',
        'catalog',
    ]

    inlines = [
        # ArrangersInline,
        ScoreInline,
    ]

    list_filter = (
        'status',
    )

    readonly_fields = (
        'name',
        'order',
        'mus_points',
        'prs_points',
        'sng_points',
        'total_points',
        'mus_score',
        'prs_score',
        'sng_score',
        'total_score',
        'status_monitor',
    )
    raw_id_fields = (
        'performance',
        'tune',
        'catalog',
    )
    autocomplete_lookup_fields = {
        'fk': [
            'performance',
            'tune',
        ]
    }

    ordering = (
        'name',
        'order',
    )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
    )

    save_on_top = True
    list_display = (
        'name',
        'status',
        'status_monitor',
        'location',
        'website',
        'facebook',
        'twitter',
        'email',
        'phone',
        'picture',
    )

    fields = (
        'name',
        ('status', 'status_monitor',),
        'kind',
        ('start_date', 'end_date',),
        'organization',
        'location',
        'website',
        'facebook',
        'twitter',
        'email',
        'phone',
        'member',
        'picture',
        'description',
        'notes',
    )

    readonly_fields = (
        'status_monitor',
    )
    inlines = [
        DirectorInline,
        SingerInline,
        CertificationInline,
    ]


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    save_on_top = True
    fields = [
        'name',
        ('status', 'status_monitor',),
        'song',
        'judge',
        'points',
    ]

    readonly_fields = [
        'name',
        'status_monitor',
        'song',
        'judge',
    ]

    list_display = [
        'name',
        'status',
        'points',
    ]

    list_filter = [
        'status',
    ]

    raw_id_fields = [
        'song',
        'judge',
    ]

    autocomplete_lookup_fields = {
        'fk': [
            'song',
            'judge',
        ]
    }

    ordering = [
        'judge',
        'song',
    ]


@admin.register(Session)
class SessionAdmin(FSMTransitionMixin, admin.ModelAdmin):
    fsm_field = [
        'status',
    ]

    save_on_top = True
    change_list_template = "admin/change_list_filter_sidebar.html"
    list_display = [
        'name',
        'status',
        'start_date',
        'slots',
    ]
    fields = [
        'name',
        ('status', 'status_monitor',),
        ('contest', 'kind',),
        ('start_date', 'slots',),
    ]

    readonly_fields = [
        'name',
        'status_monitor',
        'contest',
        'kind',
    ]

    list_filter = (
        'status',
    )

    raw_id_fields = (
        'contest',
    )

    autocomplete_lookup_fields = {
        'fk': [
            'contest',
        ]
    }

    inlines = [
        PerformanceInline,
        # PlacementInline,
    ]

    search_fields = [
        'name',
    ]


@admin.register(Tune)
class TuneAdmin(admin.ModelAdmin):
    save_on_top = True
    fields = (
        'name',
    )

    search_fields = (
        'name',
    )


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    model = User
    save_on_top = True
