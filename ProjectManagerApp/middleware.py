from django.http import HttpResponseNotAllowed
from django.template import RequestContext
from django.template import loader


class HttpResponseNotAllowedMiddleware(object):
    @staticmethod
    def process_response(request, response):
        if isinstance(response, HttpResponseNotAllowed):
            context = RequestContext(request)
            response.content = loader.render_to_string("405.html", context_instance=context)
        return response
