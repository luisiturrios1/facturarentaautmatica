# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.Index.as_view(), name='index'),

    url(r'^contrato/list/$', views.ContratoList.as_view(), name='contrato-list'),
    url(r'^contrato/excel/$', views.ContratoExcel.as_view(), name='contrato-excel'),
    url(r'^contrato/create/$', views.ContratoCreate.as_view(), name='contrato-create'),
    url(r'^contrato/detail/(?P<pk>[0-9]+)/$', views.ContratoDetail.as_view(), name='contrato-detail'),
    url(r'^contrato/update/(?P<pk>[0-9]+)/$', views.ContratoUpdate.as_view(), name='contrato-update'),
    url(r'^contrato/delete/(?P<pk>[0-9]+)/$', views.ContratoDelete.as_view(), name='contrato-delete'),
    url(r'^contrato/facturar/(?P<pk>[0-9]+)/$', views.ContratoFacturar.as_view(), name='contrato-facturar'),

    url(r'^factura/list/$', views.FacturaList.as_view(), name='factura-list'),
    url(r'^factura/zip/$', views.FacturaZip.as_view(), name='factura-zip'),
    url(r'^factura/excel/$', views.FacturaExcel.as_view(), name='factura-excel'),
    url(r'^factura/detail/(?P<pk>[0-9]+)/$', views.FacturaDetail.as_view(), name='factura-detail'),
    url(r'^factura/pagar/(?P<pk>[0-9]+)/$', views.FacturaPagar.as_view(), name='factura-pagar'),
    url(r'^factura/pdf/(?P<pk>[0-9]+)/$', views.FacturaPdf.as_view(), name='factura-pdf'),

    url(r'^pagos/buscar/$', views.PagosBucar.as_view(), name='pagos-buscar'),
    url(
        r'^pagos/consolidar/(?P<fecha_inicial>\d{4}-\d{2}-\d{2})/(?P<fecha_final>\d{4}-\d{2}-\d{2})/$',
        views.PagosConsolidar.as_view(), name='pagos-consolidar'
    ),
]