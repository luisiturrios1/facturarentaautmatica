# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django_filters.utils import timezone

from webapp import models
from webapp import tasks


class Command(BaseCommand):
    help = 'Lanza las tareas a para reenviar correos'

    def handle(self, *args, **options):

        facturas = models.Factura.objects.filter(fecha='2018-11-03')

        for factura in facturas:
            try:
                tasks.reenviar_correo.delay(factura.id)
            except Exception as e:
                print(e.message)

        self.stdout.write(self.style.SUCCESS('Successfully factura lanzados {0}'.format(facturas.count())))
