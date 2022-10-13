from django.utils import timezone
from haystack import indexes
from apps.user.models import User


class UserIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    username = indexes.CharField(model_attr="username")
    id = indexes.CharField(model_attr="id")

    def get_model(self):
        return User

    def index_queryset(self, using=None):
        return self.get_model().objects.all().exclude(id=1)