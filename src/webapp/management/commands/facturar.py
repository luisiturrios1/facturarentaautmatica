# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django_filters.utils import timezone

from webapp import models
from webapp import tasks


class Command(BaseCommand):
    help = 'Lanza las tareas a facturar del dia en que es ejecutado'

    def handle(self, *args, **options):
        fecha_actual = timezone.localtime()

        contratos = models.Contrato.objects.filter(dia_facturacion=1)

        for contrato in contratos:
            try:
                tasks.facturar.delay(contrato.id)
            except Exception as e:
                print(e.message)

        self.stdout.write(self.style.SUCCESS('Successfully contratos lanzados {0}'.format(contratos.count())))
