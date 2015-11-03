from random import randint

from factory.django import (
    DjangoModelFactory,
)

from .models import (
    Group,
    Person,
    Contestant,
    Tune,
    Judge,
)


def impanel_judges(contest):
    person = Person.objects.filter(
        judge=Person.JUDGE.admin,
    ).order_by('?').first()
    judge = contest.judges.filter(
        category=Judge.CATEGORY.admin,
        person=None,
    ).first()
    judge.person = person
    judge.save()
    persons = Person.objects.filter(
        judge=Person.JUDGE.music,
    ).order_by('?')[:contest.panel]
    for person in persons:
        judge = contest.judges.filter(
            category=Judge.CATEGORY.music,
            person=None,
        ).first()
        judge.person = person
        judge.save()
    persons = Person.objects.filter(
        judge=Person.JUDGE.singing,
    ).order_by('?')[:contest.panel]
    for person in persons:
        judge = contest.judges.filter(
            category=Judge.CATEGORY.singing,
            person=None,
        ).first()
        judge.person = person
        judge.save()
    persons = Person.objects.filter(
        judge=Person.JUDGE.presentation,
    ).order_by('?')[:contest.panel]
    for person in persons:
        judge = contest.judges.filter(
            category=Judge.CATEGORY.presentation,
            person=None,
        ).first()
        judge.person = person
        judge.save()
    return "Judges Impaneled"


def add_contestants(contest, number):
    groups = Group.objects.filter(
        kind=contest.kind,
    ).order_by('?')[:number]
    for group in groups:
        Contestant.objects.create(
            contest=contest,
            group=group,
            status=Contestant.STATUS.ready,
        )
    return "Contestants Added"


def score_performance(performance):
    base = randint(70, 90)
    songs = performance.songs.all()
    for song in songs:
        song.tune = Tune.objects.order_by('?').first()
        scores = song.scores.all()
        for score in scores:
            low, high = base, base + 5
            score.points = randint(low, high)
            score.save()
        song.save()
    performance.end_performance()
    return "Performance Scored"


class QuartetFactory(DjangoModelFactory):
    name = "The Buffalo Bills"
    kind = Group.KIND.quartet

    class Meta:
        model = Group
