# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django_filters.utils import timezone

from webapp import tasks


class Command(BaseCommand):
    help = 'Regenera todos los pdf en la APP'

    def handle(self, *args, **options):
        tasks.regenerar_pdf.delay()

        self.stdout.write(self.style.SUCCESS('Successfully regenerarpdf'))
