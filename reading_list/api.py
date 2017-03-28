from django.conf.urls import url
from django.db.models import F
from django.http import HttpResponse
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpNotFound, HttpBadRequest, HttpUnauthorized
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash, dict_strip_unicode_keys

from .models import ReadingList
from book.models import Book
from djgap.corsresource import CorsResourceBase


class ReadingListResource(CorsResourceBase, ModelResource):
    class Meta:
        queryset = ReadingList.objects.all()
        allowed_method = ['get', 'post']
        resource_name = 'reading_list'
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/create%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('create_reading_list'), name="api_create_reading_list"),
            url(r"^(?P<resource_name>%s)/read%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('read_reading_list'), name="api_read_reading_list"),
            url(r"^(?P<resource_name>%s)/delete%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('delete_reading_list'), name="api_delete_reading_list"),
            url(r"^(?P<resource_name>%s)/add_book%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('add_book'), name="api_add_book"),
            url(r"^(?P<resource_name>%s)/update_book%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('update_book'), name="api_update_book"),
            url(r"^(?P<resource_name>%s)/delete_book%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('delete_book'), name="api_delete_book"),
        ]

    def create_reading_list(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        deserialized = self.deserialize(request, request.body,
                                        format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_detail_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)
        ReadingList(user=request.user, private=bundle.data.get("private")).save()

        return self.create_response(request, {})

    def read_reading_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        auth_result = self._meta.authentication.is_authenticated(request)
        anonymous = isinstance(auth_result, HttpResponse)
        reading_lists = []
        reading_lists.append(ReadingList.objects.filter(private=False).all())
        if not anonymous:
            reading_lists.append(ReadingList.objects.filter(user=request.user).all())

        data = []
        for rl in set(reading_lists):
            data.append(self.read_a_reading_list(rl))
        object_list = {
            'objects': data
        }
        return self.create_response(request, object_list)

    def read_a_reading_list(self, reading_list):
        return [book.title for book in Book.objects.filter(reading_list=reading_list).all()]

    def delete_reading_list(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        deserialized = self.deserialize(request, request.body,
                                        format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_detail_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)
        try:
            ReadingList.objects.get(id=bundle.data.get("id"), user=request.user).delete()
        except ReadingList.DoesNotExist:
            raise ImmediateHttpResponse(HttpBadRequest('Bad reading list id'))

        return self.create_response(request, {})

    def add_book(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        deserialized = self.deserialize(request, request.body,
                                        format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_detail_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)
        try:
            reading_list = ReadingList.objects.get(id=bundle.data.get("id"), user=request.user)
        except ReadingList.DoesNotExist:
            raise ImmediateHttpResponse(HttpBadRequest('Bad reading list id'))

        data = {}
        for field in Book.BOOK_FIELDS:
            data[field] = bundle.data.get(field)

        Book(reading_list=reading_list, **data).save()

        return self.create_response(request, {})

    def update_book(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        deserialized = self.deserialize(request, request.body,
                                        format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_detail_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)
        try:
            reading_list = ReadingList.objects.get(id=bundle.data.get("id"), user=request.user)
        except ReadingList.DoesNotExist:
            raise ImmediateHttpResponse(HttpBadRequest('Bad reading list id'))

        try:
            book = Book.objects.get(id=bundle.data.get("book_id"), reading_list=reading_list)
        except Book.DoesNotExist:
            raise ImmediateHttpResponse(HttpBadRequest('Bad book id'))

        for field in Book.BOOK_FIELDS:
            setattr(book, field, bundle.data.get(field))
        book.save()

        return self.create_response(request, {})

    def delete_book(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        deserialized = self.deserialize(request, request.body,
                                        format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_detail_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)
        try:
            reading_list = ReadingList.objects.get(id=bundle.data.get("id"), user=request.user)
        except ReadingList.DoesNotExist:
            raise ImmediateHttpResponse(HttpBadRequest('Bad reading list id'))

        try:
            Book.objects.get(id=bundle.data.get("book_id"), reading_list=reading_list).delete()
        except Book.DoesNotExist:
            raise ImmediateHttpResponse(HttpBadRequest('Bad book id'))

        return self.create_response(request, {})