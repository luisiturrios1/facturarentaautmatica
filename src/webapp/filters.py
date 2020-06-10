# -*- coding: utf-8 -*-
import django_filters

from webapp import models


class FacturaFilter(django_filters.FilterSet):
    nombre_cliente = django_filters.CharFilter(lookup_expr='icontains')
    fecha = django_filters.DateFromToRangeFilter()

    class Meta:
        model = models.Factura
        fields = ['serie', 'folio', 'fecha', 'nombre_cliente', 'rfc_cliente', 'contrato', 'fecha_pago']


class ContratoFilter(django_filters.FilterSet):
    nombre_predio = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = models.Contrato
        fields = ['nombre_predio', 'cuenta_predial', 'nombre_cliente', 'dia_facturacion']
