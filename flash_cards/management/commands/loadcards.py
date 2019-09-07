from django.core.management.base import BaseCommand, CommandError
import xml.etree.ElementTree as ET
from flash_cards.models import Entry

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('xml_file')

    def handle(self, *args, **options):
        xmlFile = options['xml_file']
        tree = ET.parse(xmlFile)
        root = tree.getroot()
        for card in root.find('cards'):
            parse_card_and_save(card)

        self.stdout.write(self.style.SUCCESS("we out here"))

def parse_card_and_save(card):
    category = card.find('catassign')
    entry = card.find('entry')
    headwords = entry.findall('headword')
    headword = ""
    if len(headwords) == 1:
        headword = headwords[0].text
    else:
        for headwordObj in headwords:
            if headwordObj.attrib['charset'] == 'sc':
                headword = headwordObj.text

    pron = entry.find('pron').text
    defn = entry.find('defn').text
    category = category.attrib['category']

    print("Saving ")
    print(ET.tostring(entry))
    Entry.objects.get_or_create(headword=headword, pron=pron, defn=defn, category=category)
