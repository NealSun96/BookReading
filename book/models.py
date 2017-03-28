from django.db import models
from reading_list.models import ReadingList


class Book(models.Model):
    BOOK_FIELDS = ["ISBN", "title", "author", "category", "cover_url", "summary"]

    reading_list = models.ForeignKey(ReadingList)
    ISBN = models.TextField()
    title = models.TextField()
    author = models.TextField()
    category = models.TextField()
    cover_url = models.URLField()
    summary = models.TextField()
