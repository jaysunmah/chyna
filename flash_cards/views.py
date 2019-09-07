from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import View
from flash_cards.helpers import *
from flash_cards.models import Entry, Lesson

class Index(View):
    """
    Landing page of flash cards, should be used to create lesson, view previous ones, etc.
    """
    def getContext(self, request):
        entryTiers = getEntryTiers(Entry.objects.all())
        lessonHistory = getLessonHistory(4)
        return {
            "entry_stats": {
                "tier_0": len(entryTiers[0]),
                "tier_1": len(entryTiers[1]),
                "tier_2": len(entryTiers[2]),
                "tier_3": len(entryTiers[3])
            },
            "lesson_history": lessonHistory
        }
    def get(self, request):
        return render(request, "flash_cards/index.html", self.getContext(request))


class LessonView(View):
    """
    Given a lesson pk + optional starting entry id, return that lesson + correct entry
    """
    def getContext(self, request, pk):
        lesson = Lesson.objects.get(pk=pk)
        lessonIndex = request.GET.get('lesson_index')
        lessonIndex = lessonIndex if lessonIndex is not None else 0
        try:
            lessonEntry = lesson.lessonentry_set.get(lesson_index=lessonIndex)
            return {
                "entry": lessonEntry.entry.toMap(),
                "lesson_pk": pk,
                "lesson_index": lessonIndex,
                "total_entries": LESSON_ENTRIES
            }
        except:
            return { "finished_lesson": True }

    def get(self, request, pk):
        context = self.getContext(request, pk)
        if "finished_lesson" in context and context["finished_lesson"]:
            return HttpResponseRedirect('/')
        return render(request, 'flash_cards/view_lesson.html', self.getContext(request, pk))

class CreateLessonView(View):
    def get(self, request):
        lessonPk = createLesson()
        return HttpResponseRedirect('/lesson/%d' % lessonPk)

class EntryTierView(View):
    def getContext(self, tier):
        entryTiers = getEntryTiers(Entry.objects.all())
        entries = entryTiers[int(tier)]
        entryScores = []
        for entry in entries:
            attempts = entry.attempt_set.all()
            correct = attempts.filter(correct=True)
            entryScores.append({
                "entry": entry.toMap(),
                "attempts": len(attempts),
                "correct": len(correct)
            })
        return {
            "entry_scores": entryScores
        }
    def get(self, request, tier):
        return render(request, 'flash_cards/view_entry_tier.html', self.getContext(tier))

def markCorrect(request, entryPk, lessonPk, lessonIndex):
    return mark(entryPk, lessonPk, lessonIndex, True)

def markIncorrect(request, entryPk, lessonPk, lessonIndex):
    return mark(entryPk, lessonPk, lessonIndex, False)

def mark(entryPk, lessonPk, lessonIndex, correct):
    entry = Entry.objects.get(pk=entryPk)
    lesson = Lesson.objects.get(pk=lessonPk)
    lessonEntry = lesson.lessonentry_set.get(lesson_index=lessonIndex)
    attempt = Attempt(entry=entry,correct=correct,lesson_entry=lessonEntry)
    attempt.save()
    return HttpResponseRedirect('/lesson/%s?lesson_index=%i' % (lessonPk, int(lessonIndex)+1))
