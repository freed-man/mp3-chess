from django.views import generic
from .models import Topic


class TopicList(generic.ListView):
    """
    Displays a list of published topics on the homepage.
    """
    queryset = Topic.objects.filter(status=1)
    template_name = "club/index.html"
    paginate_by = 6
