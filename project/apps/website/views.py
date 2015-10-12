import logging
log = logging.getLogger(__name__)

from django.shortcuts import (
    render,
    redirect,
)

from django.core.urlresolvers import reverse

from fuzzywuzzy import process

from django.db import (
    IntegrityError,
    transaction,
)

from django.contrib import messages
from django.db.models import Q
from django.core.paginator import (
    Paginator,
    EmptyPage,
    PageNotAnInteger,
)

from apps.api.models import (
    Group,
    Song,
    Person,
    Arrangement,
    DuplicateGroup,
    DuplicateSong,
    DuplicatePerson,
)

from .forms import (
    MergePersonForm,
    MergeGroupForm,
    MergeSongForm,
)


def home(request):
    choruses = DuplicateGroup.objects.filter(
        parent__kind=Group.KIND.chorus,
    ).count()
    quartets = DuplicateGroup.objects.filter(
        parent__kind=Group.KIND.quartet,
    ).count()
    songs = DuplicateSong.objects.count()
    persons = DuplicatePerson.objects.count()

    return render(
        request,
        'home.html', {
            'choruses': choruses,
            'quartets': quartets,
            'songs': songs,
            'persons': persons,
        },
    )


def all_choruses(request):
    groups = Group.objects.filter(
        duplicates__isnull=False,
    ).filter(kind=Group.KIND.chorus).distinct().order_by('name')
    return render(
        request,
        'all_choruses.html',
        {'groups': groups},
    )


def choruses(request):
    groups_all = Group.objects.filter(
        duplicates__isnull=False,
    ).filter(kind=Group.CHORUS).distinct().order_by('name')
    paginator = Paginator(
        groups_all,
        1,
    )
    page = request.GET.get('page')
    try:
        groups = paginator.page(page)
    except PageNotAnInteger:
        groups = paginator.page(1)
    except EmptyPage:
        groups = paginator.page(paginator.num_pages)
    try:
        duplicate = groups.object_list[0].duplicates.first()
    except IndexError:
        duplicate = None
    return render(
        request,
        'choruses.html',
        {'groups': groups, 'page': page, 'duplicate': duplicate},
    )


def all_quartets(request):
    groups = Group.objects.filter(
        duplicates__isnull=False,
    ).filter(kind=Group.QUARTET).distinct().order_by('name')
    return render(
        request,
        'all_quartets.html',
        {'groups': groups},
    )


def quartets(request):
    groups_all = Group.objects.filter(
        duplicates__isnull=False,
    ).filter(kind=Group.QUARTET).distinct().order_by('name')
    paginator = Paginator(
        groups_all,
        1,
    )
    page = request.GET.get('page')
    try:
        groups = paginator.page(page)
    except PageNotAnInteger:
        groups = paginator.page(1)
    except EmptyPage:
        groups = paginator.page(paginator.num_pages)
    duplicate = groups.object_list[0].duplicates.first()
    return render(
        request,
        'quartets.html',
        {'groups': groups, 'page': page, 'duplicate': duplicate},
    )


def all_songs(request):
    songs = Song.objects.filter(
        duplicates__isnull=False,
    ).distinct().order_by('name')
    return render(
        request,
        'all_songs.html',
        {'songs': songs},
    )


def songs(request):
    songs_all = Song.objects.filter(
        duplicates__isnull=False,
    ).distinct().order_by('name')
    paginator = Paginator(
        songs_all,
        1,
    )
    page = request.GET.get('page')
    try:
        songs = paginator.page(page)
    except PageNotAnInteger:
        songs = paginator.page(1)
    except EmptyPage:
        songs = paginator.page(paginator.num_pages)
    duplicate = songs.object_list[0].duplicates.first()
    return render(
        request,
        'songs.html',
        {'songs': songs, 'page': page, 'duplicate': duplicate},
    )


def all_persons(request):
    persons = Person.objects.filter(
        duplicates__isnull=False,
    ).distinct().order_by('name')
    return render(
        request,
        'all_persons.html',
        {'persons': persons},
    )


def persons(request):
    persons_all = Person.objects.filter(
        duplicates__isnull=False,
    ).distinct().order_by('name')
    paginator = Paginator(
        persons_all,
        1,
    )
    page = request.GET.get('page')
    try:
        persons = paginator.page(page)
    except PageNotAnInteger:
        persons = paginator.page(1)
    except EmptyPage:
        persons = paginator.page(paginator.num_pages)
    duplicate = persons.object_list[0].duplicates.first()
    return render(
        request,
        'persons.html',
        {'persons': persons, 'page': page, 'duplicate': duplicate},
    )


@transaction.atomic
def merge_groups(request, parent_id, child_id):
    parent = Group.objects.get(id=parent_id)
    child = Group.objects.get(id=child_id)
    if parent.kind == 1:
        target = reverse('website:quartets')
    else:
        target = reverse('website:choruses')
    page = request.GET.get('page')
    if page:
        target = target + "?page={0}".format(page)
    r = redirect(target)
    contestants = child.contestants.all()
    # move related records
    with transaction.atomic():
        for contestant in contestants:
            contestant.group = parent
            try:
                contestant.save()
            except IntegrityError:
                messages.error(
                    request,
                    u"There is a Contest conflict betwen {0} and {1}.  Double-check that they are in fact duplicates.  Otherwise, merge manually.".format(parent, child),
                )
                return r
    # once records are moved, remove redundant group
    try:
        child.delete()
    except Exception as e:
        raise RuntimeError("Error deleting old group: {0}".format(e))
    messages.success(
        request,
        u"Merged {0} into {1}.".format(child, parent)
    )
    return r


def merge_songs(request, parent_id, child_id):
    parent = Song.objects.get(id=parent_id)
    child = Song.objects.get(id=child_id)
    arrangements = child.arrangements.all()
    target = reverse('website:songs')
    page = request.GET.get('page')
    if page:
        target = target + "?page={0}".format(page)
    r = redirect(target)
    # move related records
    for arrangement in arrangements:
        arrangement.song = parent
        try:
            arrangement.save()
        except IntegrityError:
            ps = arrangement.performances.all()
            for p in ps:
                p.arrangement = Arrangement.objects.get(
                    song=parent,
                    arranger=arrangement.arranger,
                )
                p.save()
    # once records are moved, remove redundant object
    try:
        child.delete()
    except Exception as e:
        raise RuntimeError("Error deleting old song: {0}".format(e))
    messages.success(
        request,
        u"Merged {0} into {1}.".format(child, parent)
    )
    return r


@transaction.atomic
def merge_persons(request, parent_id, child_id):
    parent = Person.objects.get(id=parent_id)
    child = Person.objects.get(id=child_id)
    quartets = child.quartets.all()
    choruses = child.choruses.all()
    arrangements = child.arrangements.all()
    target = reverse('website:persons')
    page = request.GET.get('page')
    if page:
        target = target + "?page={0}".format(page)
    r = redirect(target)

    # move related records
    with transaction.atomic():
        for quartet in quartets:
            quartet.person = parent
            try:
                quartet.save()
            except IntegrityError:
                messages.error(
                    request,
                    u"There is an existing member for {0} with the name {1}.  Double-check that they are in fact duplicates.  Otherwise, merge manually.".format(quartet, child),
                )
                return r
        for chorus in choruses:
            chorus.person = parent
            try:
                chorus.save()
            except IntegrityError:
                messages.error(
                    request,
                    u"There is an existing director for {0} with the name {1}.  Double-check that they are in fact duplicates.  Otherwise, merge manually.".format(chorus, child),
                )
                return r
        for arrangement in arrangements:
            arrangement.person = parent
            try:
                arrangement.save()
            except IntegrityError:
                messages.error(
                    request,
                    u"There is an existing arrangement for {0}.  Double-check that they are in fact duplicates.  Otherwise, merge manually.".format(arrangement),
                )
                return r
    # once records are moved, remove redundant group
    try:
        child.delete()
    except Exception as e:
        raise RuntimeError("Error deleting old person: {0}".format(e))
    messages.success(
        request,
        "Merged {0} into {1}.".format(child, parent)
    )
    return r


def remove_group(request, parent_id):
    parent = Group.objects.get(id=parent_id)
    if parent.kind == Group.QUARTET:
        target = reverse('website:quartets')
    else:
        target = reverse('website:choruses')
    page = request.GET.get('page')
    if page:
        target = target + "?page={0}".format(page)
    r = redirect(target)
    duplicates = DuplicateGroup.objects.filter(
        Q(parent=parent) | Q(child=parent)
    )
    duplicates.delete()
    messages.error(
        request,
        u"Removed {0} from duplicates.".format(parent.name)
    )
    return r


def remove_song(request, parent_id):
    parent = Song.objects.get(id=parent_id)
    target = reverse('website:songs')
    page = request.GET.get('page')
    if page:
        target = target + "?page={0}".format(page)
    r = redirect(target)
    duplicates = DuplicateSong.objects.filter(
        Q(parent=parent) | Q(child=parent)
    )
    duplicates.delete()
    messages.error(
        request,
        u"Removed {0} from duplicates.".format(parent.name)
    )
    return r


def remove_person(request, parent_id):
    parent = Person.objects.get(id=parent_id)
    target = reverse('website:persons')
    page = request.GET.get('page')
    if page:
        target = target + "?page={0}".format(page)
    r = redirect(target)
    duplicates = DuplicatePerson.objects.filter(
        Q(parent=parent) | Q(child=parent)
    )
    duplicates.delete()
    messages.error(
        request,
        u"Removed {0} from duplicates.".format(parent.name)
    )
    return r


def build_chorus():
    vs = Group.objects.filter(kind=Group.CHORUS).values('name')
    choices = [v['name'] for v in vs]
    gs = Group.objects.filter(kind=Group.CHORUS)
    i = 0
    for g in gs:
        i += 1
        matches = process.extract(g.name, choices)
        for match, score in matches:
            if score > 85 and score < 100:
                child = Group.objects.get(name=match)
                DuplicateGroup.objects.create(
                    parent=g,
                    child=child,
                    score=score,
                )
        print i
    return "Done"
    # messages.success(
    #     request,
    #     "Build complete.",
    # )
    # return redirect('website:choruses')


def build_quartet():
    vs = Group.objects.filter(kind=Group.QUARTET).values('name')
    choices = [v['name'] for v in vs]
    gs = Group.objects.filter(kind=Group.QUARTET)
    i = 0
    for g in gs:
        i += 1
        matches = process.extract(g.name, choices)
        for match, score in matches:
            if score > 85 and score < 100:
                child = Group.objects.get(name=match)
                DuplicateGroup.objects.create(
                    parent=g,
                    child=child,
                    score=score,
                )
        print i
    return "Done"
    # messages.success(
    #     request,
    #     "Build complete.",
    # )
    # return redirect('website:quartets')


def build_song():
    vs = Song.objects.values('name')
    choices = [v['name'] for v in vs]
    gs = Song.objects.all()
    i = 0
    for g in gs:
        i += 1
        matches = process.extract(g.name, choices)
        for match, score in matches:
            if score > 85 and score < 100:
                child = Song.objects.get(name=match)
                DuplicateSong.objects.create(
                    parent=g,
                    child=child,
                    score=score,
                )
        print i
    return "Done"
    # messages.success(
    #     request,
    #     "Build complete.",
    # )
    # return redirect('website:songs')


def build_person():
    vs = Person.objects.values('name')
    choices = [v['name'] for v in vs]
    gs = Person.objects.all()
    i = 0
    for g in gs:
        i += 1
        matches = process.extract(g.name, choices)
        for match, score in matches:
            if score > 85 and score < 100:
                child = Person.objects.get(name=match)
                DuplicatePerson.objects.create(
                    parent=g,
                    child=child,
                    score=score,
                )
        print i
    return "Done"
    # messages.success(
    #     request,
    #     "Build complete.",
    # )
    # return redirect('website:persons')


def manual_persons(request):
    if request.method == 'POST':
        form = MergePersonForm(request.POST)
        if form.is_valid():
            form.merge()
            messages.success(
                request,
                "Success!! Merged {0} into {1}".format(
                    form.cleaned_data['old'],
                    form.cleaned_data['new'],
                )
            )
            return redirect('website:home')
        else:
            messages.warning(
                request,
                form.errors,
            )
    else:
        form = MergePersonForm()
    return render(
        request,
        'manual_merge.html',
        {'form': form},
    )


def manual_groups(request):
    if request.method == 'POST':
        form = MergeGroupForm(request.POST)
        if form.is_valid():
            form.merge()
            messages.success(
                request,
                "Success!!",
            )
            return redirect('website:home')
        else:
            messages.warning(
                request,
                form.errors,
            )
    else:
        form = MergeGroupForm()
    return render(
        request,
        'manual_merge.html',
        {'form': form},
    )


def manual_songs(request):
    if request.method == 'POST':
        form = MergeSongForm(request.POST)
        if form.is_valid():
            form.merge()
            messages.success(
                request,
                "Success!!",
            )
            return redirect('website:home')
        else:
            messages.warning(
                request,
                form.errors,
            )
    else:
        form = MergeSongForm()
    return render(
        request,
        'manual_merge.html',
        {'form': form},
    )
