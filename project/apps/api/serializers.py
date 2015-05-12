from rest_framework import serializers

from .models import (
    Convention,
    Contest,
    Contestant,
    Group,
    Performance,
)


class PerformanceSerializer(serializers.ModelSerializer):
    round = serializers.CharField(
        source='get_round_display',
    )

    class Meta:
        model = Performance
        fields = (
            'id',
            'slug',
            'round',
            'queue',
            'session',
            'stagetime',
            'place',
            'song1',
            'mus1',
            'prs1',
            'sng1',
            'song2',
            'mus2',
            'prs2',
            'sng2',
            'men',
            'mus1_rata',
            'prs1_rata',
            'sng1_rata',
            'song1_raw',
            'song1_rata',
            'mus2_rata',
            'prs2_rata',
            'sng2_rata',
            'song2_raw',
            'song2_rata',
            'total_raw',
            'total_rata',
        )


class GroupSerializer(serializers.ModelSerializer):

    district = serializers.CharField(
        source='get_district_display',
    )

    # lead = serializers.CharField(
    #     source='singer.name',
    # )

    # tenor = serializers.CharField(
    #     source='.name',
    # )

    # baritone = serializers.CharField(
    #     source='quartet.baritone.name',
    # )

    # bass = serializers.CharField(
    #     source='quartet.bass.name',
    # )

    class Meta:
        model = Group
        fields = (
            'id',
            'slug',
            'name',
            'district',
            'location',
            'website',
            'facebook',
            'twitter',
            'email',
            'phone',
            'picture',
            'description',
            # 'director',
            # 'chapterName',
            # 'lead',
            # 'tenor',
            # 'baritone',
            # 'bass',
        )


class ContestantContestSerializer(serializers.ModelSerializer):
    performances = PerformanceSerializer(
        many=True,
        read_only=True,
    )

    group = GroupSerializer(
        read_only=True,
    )

    class Meta:
        model = Contestant
        fields = (
            'id',
            'slug',
            'group',
            'seed',
            'prelim',
            'place',
            'score',
            'performances',
        )


class ContestSerializer(serializers.ModelSerializer):
    contestants = ContestantContestSerializer(
        many=True,
    )

    level = serializers.CharField(
        source='get_level_display',
    )

    kind = serializers.CharField(
        source='get_kind_display',
    )

    year = serializers.CharField(
        source='get_year_display',
    )

    district = serializers.CharField(
        source='get_district_display',
    )

    class Meta:
        model = Contest
        fields = (
            'id',
            'slug',
            'level',
            'kind',
            'year',
            'district',
            'panel',
            'scoresheet_pdf',
            'contestants',
        )


class ContestGroupSerializer(serializers.ModelSerializer):
    level = serializers.CharField(
        source='get_level_display',
    )

    kind = serializers.CharField(
        source='get_kind_display',
    )

    year = serializers.CharField(
        source='get_year_display',
    )

    district = serializers.CharField(
        source='get_district_display',
    )

    class Meta:
        model = Contest
        fields = (
            'id',
            'slug',
            'level',
            'kind',
            'year',
            'district',
            'panel',
            'scoresheet_pdf',
        )


class ContestantGroupSerializer(serializers.ModelSerializer):
    performances = PerformanceSerializer(
        many=True,
        read_only=True,
    )

    contest = ContestGroupSerializer(
        read_only=True,
    )

    class Meta:
        model = Contestant
        fields = (
            'id',
            'slug',
            'contest',
            'seed',
            'prelim',
            'place',
            'score',
            'performances',
        )


class ConventionSerializer(serializers.ModelSerializer):
    contests = ContestSerializer(
        many=True,
    )

    class Meta:
        model = Convention
        lookup_field = 'slug'
        fields = (
            'id',
            'url',
            'slug',
            'name',
            'dates',
            'timezone',
            'contests',
        )
