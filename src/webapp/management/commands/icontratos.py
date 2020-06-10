# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

import csv

from webapp import models


class Command(BaseCommand):
    help = 'Importar contratos en archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):

        with open(options['file']) as csvfile:

            reader = csv.DictReader(csvfile)

            count = 0

            for row in reader:
                c = models.Contrato()
                c.nombre_predio = row['nombre_predio']
                c.cuenta_predial = row['cuenta_predial']
                c.nombre_cliente = row['nombre_cliente']
                c.rfc_cliente = row['rfc_cliente']
                c.correo_cliente = row['correo_cliente']
                c.telefono_cliente = row['telefono_cliente']
                c.saldo_contrato = row['saldo_contrato']
                c.precio_mensual = row['precio_mensual']
                c.retener_impuestos = row['retener_impuestos'] == '1'
                c.uso_cfdi = row['uso_cfdi']
                c.metodo_pago = row['metodo_pago']
                c.forma_pago = row['forma_pago']
                c.dia_facturacion = row['dia_facturacion']
                c.save()

                count += 1

                self.stdout.write(self.style.NOTICE('Contrato {} creado'.format(c.id)))

        self.stdout.write(self.style.SUCCESS('Successfully total de contratos creados {}'.format(count)))
