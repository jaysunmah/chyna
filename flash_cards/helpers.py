import random
from flash_cards.models import Entry, Attempt, LessonEntry, Lesson
from datetime import datetime
import pytz

T2_MIN_ATTEMPTS = 3 # min number of attempts needed to upgrade (t2 -> t3)
T2_NUM_CORRECT = 3 # number of correct in a row to upgrade (t2 -> t3)
T3_MIN_ATTEMPTS = 5 # min number of attempts needed to upgrade (t3 -> t4)
T3_NUM_CORRECT = 5 # number of correct attempts in a row needed to upgrade (t3 -> t4)

LESSON_ENTRIES = 20 # number of entries we want per lesson
LESSON_PARTITION = [None, 14, 4, 2] # max # of entries per tier per lesson

def getEntryTiers(entries):
    entryTiers = [[], [], [], []] # rankings from tiers 0 to 3
    for entry in entries:
        entryRank = rankEntry(entry)
        entryTiers[entryRank].append(entry)
    return entryTiers

def createLesson():
    lesson = Lesson()
    lesson.save()
    # 1. Fetch all entries
    entries = Entry.objects.all()
    # 2. For each entry, fetch all attempts and rank that entry
    # 2b. save it to some mapping maybe??
    entryTiers = getEntryTiers(entries)
    # 3. Select which entries to test on, starting with tier 1's and ending at 4's
    entriesSelected = 0
    for i in range(len(entryTiers)-1, -1, -1):
        selectedEntries = selectEntriesForLesson(entryTiers[i], i, entriesSelected)
        for entry in selectedEntries:
            lessonEntry = LessonEntry(entry=entry,lesson=lesson,tier=i,lesson_index=entriesSelected)
            lessonEntry.save()
            entriesSelected += 1
    return lesson.pk

def rankEntry(entry):
    # TODO if this is too slow, make it faster with better queries
    attempts = entry.attempt_set.all().order_by('-created_at')
    if len(attempts) == 0: return 0
    if len(attempts) < T2_MIN_ATTEMPTS: return 1 # not enough attempts
    correct = len([attempt for attempt in attempts[:T2_NUM_CORRECT] if attempt.correct])
    if correct < T2_NUM_CORRECT: return 1 # not proficient enough
    if len(attempts) < T3_MIN_ATTEMPTS: return 2
    correct = len([attempt for attempt in attempts[:T3_NUM_CORRECT] if attempt.correct])
    if correct < T3_NUM_CORRECT: return 2
    return 3

def selectEntriesForLesson(entries, tier, amount):
    """
    Given tier, decide how to pick the entry
    """
    random.shuffle(entries)
    if tier == 3:
        return entries[:LESSON_PARTITION[tier]]
    if tier == 0:
        return entries[:LESSON_ENTRIES - amount]
    return selectEntriesImpl(entries, LESSON_PARTITION[tier])

def selectEntriesImpl(entries, limit):
    entryCreationDates = {}
    for entry in entries:
        # 1. For each entry, find oldest attempt date (if any)
        attempts = Attempt.objects.filter(entry=entry).order_by('created_at')
        date = datetime.now(pytz.utc)  # set date as now if its None
        if len(attempts) != 0: date = attempts[0].created_at
        entryCreationDates[entry] = date
    entries = sorted(entries, key=lambda x: entryCreationDates[x])
    return entries[:limit]

def getLessonHistory(limit):
    """
    :param limit:int Max number of lessons to return
    :return: list of past lesson meta data
    """
    lessons = Lesson.objects.all().order_by('-created_at')[:limit]
    result = []
    for lesson in lessons:
        lessonEntries = lesson.lessonentry_set.order_by('lesson_index')
        lessonEntryStats = []
        total = 0
        totalCorrect = 0
        for lessonEntry in lessonEntries:
            attempts = lessonEntry.attempt_set.all()
            correct = len([attempt for attempt in attempts if attempt.correct])
            lessonEntryStats.append({
                "entry": lessonEntry.entry.toMap(),
                "attempts": len(attempts),
                "correct": correct
            })
            total += len(attempts)
            totalCorrect += correct
        result.append({
            "lesson": lesson.toMap(),
            "lesson_accuracy": totalCorrect / total * 100,
            "lesson_entry_stats": lessonEntryStats
        })
    return result
