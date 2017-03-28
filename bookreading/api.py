# -*- coding: utf-8 -*-

from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from tastypie import http
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.models import ApiKey
from tastypie.resources import ModelResource
from tastypie.exceptions import ImmediateHttpResponse
from tastypie_oauth.authentication import OAuth20Authentication

from .corsresource import CorsResourceBase


class LoginResource(CorsResourceBase, ModelResource):
    class Meta:
        queryset = User.objects.all()
        fields = ["first_name", "last_name", "username"]
        allowed_method = ['get']
        resource_name = 'login'
        authorization = DjangoAuthorization()
        authentication = OAuth20Authentication()
        always_return_data = True

    def authorized_read_list(self, object_list, bundle):
        return object_list.filter(username=bundle.request.user.username)

    def dehydrate(self, bundle):
        username = bundle.data.get('username')
        user = User.objects.get(username=username)
        bundle.data['api_key'] = ApiKey.objects.get_or_create(user=user)[0].key
        return bundle

    def is_authenticated(self, request):
        ''' Overriding to delete www-authenticate, preventing browser popup '''
        auth_result = self._meta.authentication.is_authenticated(request)

        if isinstance(auth_result, HttpResponse):
            del auth_result['WWW-Authenticate']
            raise ImmediateHttpResponse(response=auth_result)

        if not auth_result is True:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())
