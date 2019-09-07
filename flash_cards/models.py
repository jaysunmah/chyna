from django.db import models
from pytz import timezone
from datetime import datetime

class Entry(models.Model):
    headword = models.CharField(max_length=200, blank=False)
    pron = models.CharField(max_length=200, blank=False)
    defn = models.CharField(max_length=200, blank=False)
    category = models.CharField(max_length=200, blank=False)

    def __str__(self):
        return self.headword

    def toMap(self):
        return {
            "headword": self.headword,
            "pron": self.pron,
            "defn": self.defn,
            "category": self.category,
            "pk": self.pk
        }


class Lesson(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    def toMap(self):
        pacificTime = self.created_at.astimezone(timezone('US/Pacific'))
        return {
            "pk": self.pk,
            "created_at": pacificTime.strftime("%a %b %-d %-I:%-M%p")
        }

class LessonEntry(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    tier = models.IntegerField()
    lesson_index = models.IntegerField()

class Attempt(models.Model):
    # if we delete an entry, then there's no point in holding its attempts anymore
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    # if we delete a lesson, i think it should still be fine to keep the attempt
    lesson_entry = models.ForeignKey(LessonEntry, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    correct = models.BooleanField()

