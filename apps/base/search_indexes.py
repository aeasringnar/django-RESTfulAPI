from django.utils import timezone
from haystack import indexes
from .models import ConfDict


class ConfDictIndex(indexes.SearchIndex, indexes.Indexable):
    
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr="dict_title")

    def get_model(self):
        return ConfDict

    def index_queryset(self, using=None):
        return self.get_model().objects.all()