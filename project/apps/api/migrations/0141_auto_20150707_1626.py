# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0140_auto_20150707_1059'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contestant',
            name='baritone',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='bass',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='director',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='finals_mus1_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='finals_mus1_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='finals_mus2_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='finals_mus2_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='finals_prs1_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='finals_prs1_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='finals_prs2_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='finals_prs2_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='finals_sng1_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='finals_sng1_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='finals_sng2_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='finals_sng2_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='finals_song1',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='finals_song1_arranger',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='finals_song1_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='finals_song1_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='finals_song2',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='finals_song2_arranger',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='finals_song2_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='finals_song2_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='lead',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='quarters_mus1_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='quarters_mus1_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='quarters_mus2_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='quarters_mus2_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='quarters_prs1_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='quarters_prs1_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='quarters_prs2_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='quarters_prs2_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='quarters_sng1_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='quarters_sng1_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='quarters_sng2_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='quarters_sng2_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='quarters_song1',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='quarters_song1_arranger',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='quarters_song1_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='quarters_song1_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='quarters_song2',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='quarters_song2_arranger',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='quarters_song2_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='quarters_song2_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='semis_mus1_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='semis_mus1_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='semis_mus2_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='semis_mus2_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='semis_prs1_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='semis_prs1_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='semis_prs2_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='semis_prs2_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='semis_sng1_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='semis_sng1_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='semis_sng2_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='semis_sng2_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='semis_song1',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='semis_song1_arranger',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='semis_song1_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='semis_song1_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='semis_song2',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='semis_song2_arranger',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='semis_song2_points',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='semis_song2_score',
        ),
        migrations.RemoveField(
            model_name='contestant',
            name='tenor',
        ),
        migrations.RemoveField(
            model_name='group',
            name='baritone',
        ),
        migrations.RemoveField(
            model_name='group',
            name='bass',
        ),
        migrations.RemoveField(
            model_name='group',
            name='director',
        ),
        migrations.RemoveField(
            model_name='group',
            name='lead',
        ),
        migrations.RemoveField(
            model_name='group',
            name='tenor',
        ),
        migrations.AlterField(
            model_name='director',
            name='contestant',
            field=models.ForeignKey(related_name='directors', blank=True, to='api.Contestant'),
        ),
        migrations.AlterField(
            model_name='director',
            name='name',
            field=models.CharField(unique=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='director',
            name='part',
            field=models.IntegerField(default=1, choices=[(1, b'Director'), (2, b'Co-Director')]),
        ),
        migrations.AlterField(
            model_name='director',
            name='person',
            field=models.ForeignKey(related_name='choruses', blank=True, to='api.Person'),
        ),
        migrations.AlterField(
            model_name='director',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, populate_from=b'name', always_update=True, unique=True),
        ),
        migrations.AlterField(
            model_name='performance',
            name='contestant',
            field=models.ForeignKey(related_name='performances', to='api.Contestant'),
        ),
        migrations.AlterField(
            model_name='performance',
            name='name',
            field=models.CharField(unique=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='performance',
            name='order',
            field=models.IntegerField(choices=[(1, b'1'), (2, b'2')]),
        ),
        migrations.AlterField(
            model_name='performance',
            name='round',
            field=models.IntegerField(choices=[(1, b'Finals'), (2, b'Semis'), (3, b'Quarters')]),
        ),
        migrations.AlterField(
            model_name='performance',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, populate_from=b'name', always_update=True, unique=True),
        ),
        migrations.AlterField(
            model_name='singer',
            name='contestant',
            field=models.ForeignKey(related_name='singers', to='api.Contestant'),
        ),
        migrations.AlterField(
            model_name='singer',
            name='name',
            field=models.CharField(unique=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='singer',
            name='person',
            field=models.ForeignKey(related_name='quartets', to='api.Person'),
        ),
        migrations.AlterField(
            model_name='singer',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, populate_from=b'name', always_update=True, unique=True),
        ),
    ]