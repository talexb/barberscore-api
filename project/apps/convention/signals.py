from django.db.models.signals import pre_save
from django.dispatch import receiver

import logging
log = logging.getLogger('apps.convention')

from django.utils.text import slugify

from .models import (
    Contestant,
)


@receiver(pre_save, sender=Contestant)
def contestant_pre_save(sender, instance, **kwargs):
    instance.slug = slugify(instance.name)
