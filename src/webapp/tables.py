# -*- coding: utf-8 -*-
from django_tables2 import Table
from django_tables2 import LinkColumn

from webapp import models


class ContratoTable(Table):
    nombre_predio = LinkColumn()

    class Meta:
        model = models.Contrato
        template_name = 'django_tables2/bootstrap-responsive.html'
        fields = (
            'nombre_predio', 'cuenta_predial', 'nombre_cliente', 'rfc_cliente',
            'correo_cliente', 'telefono_cliente', 'saldo_contrato',
            'precio_mensual', 'dia_facturacion',
        )


class FacturaTable(Table):
    uuid = LinkColumn()

    class Meta:
        model = models.Factura
        template_name = 'django_tables2/bootstrap-responsive.html'
        fields = (
            'uuid',
            'serie',
            'folio',
            'fecha',
            'nombre_cliente',
            'rfc_cliente',
            'correo_cliente',
            'concepto',
            'sub_total',
            'iva_trasladado',
            'iva_retenido',
            'isr_retenido',
            'total',
            'contrato',
            'fecha_pago',
        )
