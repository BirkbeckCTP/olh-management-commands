import json
from datetime import datetime

from django.core.management.base import BaseCommand

from journal import models
from submission import models as submission_models

FAIL = '\033[91m'
ENDC = '\033[0m'


def find_article_in_dict(file_dict, article):
    for obj in file_dict:
        if obj['model'] == 'submission.article' and obj['pk'] == article.pk:
            print('Object {pk} found - {date}'.format(pk=article.pk, date=article.date_published))
            return obj


def update_article(article, obj):
    if obj['fields'].get('abstract', None):
        article.abstract = obj['fields'].get('abstract')
        article.save()
    else:
        print('{fail}No abstract found.{end}'.format(fail=FAIL, end=ENDC))


class Command(BaseCommand):
    """Fixes abstracts that were corrupted on the 16th of May, 2018"""

    help = "Fixes abstracts that were corrupted on the 16th of May, 2018."

    def add_arguments(self, parser):
        """ Adds arguments to Django's management command-line parser.

        :param parser: the parser to which the required arguments will be added
        :return: None
        """
        parser.add_argument('file')

    def handle(self, *args, **options):
        file_path = options.get('file')

        file = open(file_path, 'r')
        file_dict = json.loads(file.read())

        journal_codes = ['orbit', 'wwe', 'ddl']

        journals = models.Journal.objects.filter(code__in=journal_codes)

        print(journals)
        date_affected = datetime(year=2018, month=5, day=15)

        for journal in journals:
            print('Running {journal}'.format(journal=journal.name))
            articles = submission_models.Article.objects.filter(journal=journal, date_published__lte=date_affected)

            for article in articles:
                obj = find_article_in_dict(file_dict, article)
                update_article(article, obj)
