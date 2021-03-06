# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-18 17:08
from __future__ import unicode_literals

from django.db import migrations, models
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0096_auto_20170717_1539'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='organization',
            options={'ordering': ['org_sort'], 'verbose_name_plural': 'organizations'},
        ),
        migrations.AlterField(
            model_name='appearance',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(0, 'New'), (2, 'Published'), (5, 'Verified'), (10, 'Started'), (20, 'Finished'), (30, 'Confirmed'), (40, 'Flagged'), (50, 'Scratched'), (60, 'Cleared'), (90, 'Announced')], default=0),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='status',
            field=models.IntegerField(choices=[(-10, 'Archived'), (0, 'New'), (10, 'Published'), (20, 'Confirmed'), (25, 'Verified'), (30, 'Final')], default=0),
        ),
        migrations.AlterField(
            model_name='contest',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(0, 'New'), (10, 'Opened'), (15, 'Closed'), (35, 'Verified'), (42, 'Finished'), (45, 'Announced')], default=0),
        ),
        migrations.AlterField(
            model_name='contestant',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(0, 'New'), (10, 'Eligible'), (20, 'Ineligible'), (40, 'District Representative'), (50, 'Qualified'), (55, 'Verified'), (60, 'Finished'), (70, 'Scratched'), (80, 'Disqualified'), (90, 'Announced')], default=0),
        ),
        migrations.AlterField(
            model_name='convention',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(0, 'New'), (2, 'Published'), (4, 'Opened'), (8, 'Closed'), (10, 'Verified'), (20, 'Started'), (30, 'Finished'), (45, 'Announced')], default=0),
        ),
        migrations.AlterField(
            model_name='entry',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(0, 'New'), (5, 'Invited'), (10, 'Submitted'), (20, 'Accepted'), (30, 'Rejected'), (40, 'Withdrew'), (50, 'Verified'), (52, 'Scratched'), (55, 'Disqualified'), (57, 'Started'), (60, 'Finished'), (70, 'Completed'), (90, 'Announced')], default=0),
        ),
        migrations.AlterField(
            model_name='panelist',
            name='status',
            field=models.IntegerField(choices=[(-10, 'Archived'), (0, 'New'), (10, 'Published'), (20, 'Confirmed'), (25, 'Verified'), (30, 'Final')], default=0),
        ),
        migrations.AlterField(
            model_name='round',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(0, 'New'), (2, 'Listed'), (4, 'Opened'), (8, 'Closed'), (10, 'Verified'), (15, 'Prepared'), (20, 'Started'), (30, 'Finished'), (50, 'Announced')], default=0),
        ),
        migrations.AlterField(
            model_name='session',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(0, 'New'), (2, 'Published'), (4, 'Opened'), (8, 'Closed'), (10, 'Verified'), (20, 'Started'), (30, 'Finished'), (45, 'Announced')], default=0),
        ),
        migrations.AlterField(
            model_name='song',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(0, 'New'), (10, 'Verified'), (38, 'Finished'), (40, 'Confirmed'), (50, 'Final'), (90, 'Announced')], default=0),
        ),
    ]
