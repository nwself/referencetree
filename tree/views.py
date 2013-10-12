# Python
import json, os
import oauth2 as oauth
import urlparse

# Django 
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

# Project
from tree.models import Profile

# Mendeley    
from tree.mendeley_oapi.mendeley_client import *
# mendeley = create_client(config_file="tree/mendeley_oapi/config.json")

consumer = oauth.Consumer(settings.MENDELEY_TOKEN, settings.MENDELEY_SECRET)
client = oauth.Client(consumer)

request_token_url = 'http://api.mendeley.com/oauth/request_token'
access_token_url = 'http://api.mendeley.com/oauth/access_token'
authenticate_url = 'http://api.mendeley.com/oauth/authorize'


def mendeley_login(request):
    # Step 1. Get a request token from Mendeley.
    resp, content = client.request(request_token_url, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response from Mendeley.")

    # Step 2. Store the request token in a session for later use.
    request.session['request_token'] = dict(urlparse.parse_qsl(content))

    # Step 3. Redirect the user to the authentication URL.
    url = "%s?oauth_token=%s&oauth_callback=%s" % (authenticate_url,
        request.session['request_token']['oauth_token'], 'http://bit.ly/1bN0rX3')

    return HttpResponseRedirect(url)


@login_required
def mendeley_logout(request):
    # Log a user out using Django's logout function and redirect them
    # back to the homepage.
    logout(request)
    return HttpResponseRedirect('/')


def mendeley_authenticated(request):
    # Step 1. Use the request token in the session to build a new client.
    token = oauth.Token(request.session['request_token']['oauth_token'],
        request.session['request_token']['oauth_token_secret'])
    client = oauth.Client(consumer, token)

    # Step 2. Request the authorized access token from Mendeley.
    resp, content = client.request(access_token_url, "GET")
    if resp['status'] != '200':
        print content
        raise Exception("Invalid response from Mendeley.")

    """
    This is what you'll get back from Mendeley. Note that it includes the
    user's user_id and screen_name.
    {
        'oauth_token_secret': 'IcJXPiJh8be3BjDWW50uCY31chyhsMHEhqJVsphC3M',
        'user_id': '120889797', 
        'oauth_token': '120889797-H5zNnM3qE0iFoTTpNEHIz3noL9FKzXiOxwtnyVOD',
        'screen_name': 'heyismysiteup'
    }
    """
    access_token = dict(urlparse.parse_qsl(content))

    # Step 3. Lookup the user or create them if they don't exist.
    try:
        user = User.objects.get(username=access_token['screen_name'])
    except User.DoesNotExist:
        # When creating the user I just use their screen_name@twitter.com
        # for their email and the oauth_token_secret for their password.
        # These two things will likely never be used. Alternatively, you 
        # can prompt them for their email here. Either way, the password 
        # should never be used.
        user = User.objects.create_user(access_token['screen_name'],
            '%s@mendeley.com' % access_token['screen_name'],
            access_token['oauth_token_secret'])

        # Save our permanent token and secret for later.
        profile = Profile()
        profile.user = user
        profile.oauth_token = access_token['oauth_token']
        profile.oauth_secret = access_token['oauth_token_secret']
        profile.save()

    # Authenticate the user and log them in using Django's pre-built 
    # functions for these things.
    user = authenticate(username=access_token['screen_name'],
        password=access_token['oauth_token_secret'])
    login(request, user)

    return HttpResponseRedirect('/')

def folder_documents(request, folder_id):
    # mendeley = create_client(config_file="tree/mendeley_oapi/config.json", keys_file="tree/mendeley_oapi/keys_api.mendeley.com.pkl")

    try:
        documents = Document.objects.get(folder_id=folder_id)
        # Do some stuff here
    except Folder.DoesNotExist:
        extra_context['documents'] = []
        for docId in folder_documents['document_ids']:
            doc = mendeley.document_details(docId)
            extra_context['documents'].append(doc)
            # Save this stuff somewhere


def home(request):
    extra_context = {}

    # extra_context['folders'] = mendeley.folders()
    extra_context['folders'] = [{u'id': u'35794901', u'name': u'Twitter Election', u'parent': -1, u'size': 24, u'version': u'2'}, {u'id': u'47153281', u'name': u'Data Viz', u'parent': -1, u'size': 17, u'version': u'3'}, {u'id': u'47153291', u'name': u'VTS', u'parent': -1, u'size': 2, u'version': u'2'}, {u'id': u'47783701', u'name': u'Interfaces', u'parent': -1, u'size': 3, u'version': u'2'}, {u'id': u'48033931', u'name': u'Other', u'parent': -1, u'size': 1, u'version': u'2'}, {u'id': u'51893391', u'name': u'Incoming', u'parent': -1, u'size': 4, u'version': u'2'}, {u'id': u'51959571', u'name': u'Teaching', u'parent': u'51893391', u'size': 2, u'version': u'3'}, {u'id': u'64229521', u'name': u'NLG', u'parent': -1, u'size': 17, u'version': u'1'}]
    folder_documents = {u'current_page': 0, u'document_ids': [u'6144827874', u'6144827814', u'6144827834', u'6144827804', u'6144827764', u'6144827774', u'6144827754', u'6145333404', u'6144827734', u'6144827784', u'6144827854', u'6145333374', u'6144827864', u'6144827894', u'6144827844', u'6144827824', u'6144827794'], u'documents': [{u'id': u'6144827874', u'version': 1380915342}, {u'id': u'6144827814', u'version': 1380915342}, {u'id': u'6144827834', u'version': 1380915342}, {u'id': u'6144827804', u'version': 1380915342}, {u'id': u'6144827764', u'version': 1380915342}, {u'id': u'6144827774', u'version': 1380915342}, {u'id': u'6144827754', u'version': 1380915342}, {u'id': u'6145333404', u'version': 1380915341}, {u'id': u'6144827734', u'version': 1380915342}, {u'id': u'6144827784', u'version': 1380915342}, {u'id': u'6144827854', u'version': 1380915342}, {u'id': u'6145333374', u'version': 1380915342}, {u'id': u'6144827864', u'version': 1380915342}, {u'id': u'6144827894', u'version': 1380915342}, {u'id': u'6144827844', u'version': 1380915342}, {u'id': u'6144827824', u'version': 1380915342}, {u'id': u'6144827794', u'version': 1380915342}], u'folder_id': u'64229521', u'folder_name': u'NLG', u'folder_version': u'1', u'items_per_page': 20, u'total_pages': 1, u'total_results': 17}


    return render_to_response("home.html", extra_context, context_instance=RequestContext(request))

