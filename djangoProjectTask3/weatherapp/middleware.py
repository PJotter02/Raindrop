from django.utils.deprecation import MiddlewareMixin
from .models import SearchHistory

#Process the search history for users and links to user
class SearchHistoryMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method == 'GET' and 'q' in request.GET:
            if request.user.is_authenticated:
                SearchHistory.objects.create(
                    user = request.user,
                    query = request.GET['q'],
                    source_ip = request.META.get['REMOTE_ADDR'],
                    user_agent=request.META.get['HTTP_USER_AGENT']
                )