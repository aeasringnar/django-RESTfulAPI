from django.utils.translation import gettext_lazy
from django.db.models.enums import IntegerChoices, TextChoices


class Gender(TextChoices):
    female = 'female', gettext_lazy('女')
    male = 'male', gettext_lazy('男')
    privacy = 'privacy', gettext_lazy('保密')