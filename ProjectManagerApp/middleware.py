from django.http import HttpResponseNotAllowed
from django.template import loader, RequestContext


class HttpResponseNotAllowedMiddleware(object):
    @staticmethod
    def process_response(request, response):
        if isinstance(response, HttpResponseNotAllowed):
            context = RequestContext(request, {'error_code': 405, 'error_message': 'Method not allowed'})
            response.content = loader.render_to_string("http_error.html", context)
        return response
