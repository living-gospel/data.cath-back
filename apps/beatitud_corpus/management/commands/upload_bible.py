from django.core.management.base import BaseCommand, CommandError
from apps.beatitud_corpus.models import BibleVerseRef, BibleVerse, BibleBook, BibleVersion
import json


class Command(BaseCommand):
    help = 'Upload bible verses in db'

    def handle(self, *args, **options):
        with open('./data/bible_verses.json', "r") as f:
            verses = json.load(f)

        with open('./data/bible_refs_list.json', "r") as f:
            refs = json.load(f)

        for ref in refs:
            verse = verses.get(ref)
            book, is_created = BibleBook.objects.get_or_create(
                code=verse.get("book")
            )
            ref_obj, is_created = BibleVerseRef.objects.get_or_create(
                code=verse.get("ref_bj"),
                book=book,
                chapter=int(verse.get("chapter")),
                number=int(verse.get("verse")),
            )
            versions = ["bj", "bw", "bfc", "tob", ]
            for version in versions:
                text = verse.get("text_{}".format(version))
                if not text:
                    continue
                version_obj, is_created = BibleVersion.objects.get_or_create(code=version)
                BibleVerse.objects.get_or_create(
                    ref=ref_obj,
                    version=version_obj,
                    text=text,
                    text_introductory="",
                    text_ending="",
                )
