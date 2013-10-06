from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext, loader

import json

from mendeley_oapi.mendeley_client import *

mendeley = create_client()

def home(request):
    extra_context['folders'] = mendeley.folders()

    return render_to_response("home.html", extra_context, context_instance=RequestContext(request))

