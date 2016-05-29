# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-26 16:58
from __future__ import unicode_literals

from django.db import migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0039_auto_20160526_0910'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contestant',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(0, b'New'), (10, b'Eligible'), (20, b'Ineligible'), (40, b'District Representative'), (50, b'Qualified'), (55, b'Validated'), (60, b'Ranked'), (70, b'Scratched'), (80, b'Disqualified')], default=0),
        ),
        migrations.AlterField(
            model_name='performer',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(0, b'New'), (10, b'Registered'), (20, b'Accepted'), (30, b'Declined'), (40, b'Dropped'), (50, b'Validated'), (52, b'Scratched'), (55, b'Disqualified'), (60, b'Finished')], default=0),
        ),
        migrations.AlterField(
            model_name='round',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(0, b'New'), (15, b'Validated'), (20, b'Started'), (25, b'Finished'), (50, b'Published')], default=0),
        ),
        migrations.AlterField(
            model_name='submission',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(0, b'New'), (10, b'Pre-Submitted'), (20, b'Post-Submitted'), (30, b'Validated')], default=0),
        ),
    ]