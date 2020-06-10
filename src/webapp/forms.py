# -*- coding: utf-8 -*-
from django import forms

from webapp.models import FORMA_PAGO

class FacturaPagarForm(forms.Form):
    fecha_pago = forms.DateField(
        required=True,
        help_text=u'Al marcar esta factura como pagada se descontara el saldo del contrato.'
    )
    forma_pago_rep = forms.ChoiceField(FORMA_PAGO, required=True)
    num_operacion = forms.CharField(max_length=100, required=True)


class FacturarForm(forms.Form):
    concepto = forms.CharField(max_length=500, strip=True, required=True)
    sub_total = forms.DecimalField(
        decimal_places=2, max_digits=20, required=True,
        help_text=u'Ingrese el precio antes de impuestos'
    )


class FacturaExcelForm(forms.Form):
    fecha_inicial = forms.DateField(required=True)
    fecha_final = forms.DateField(required=True)


class FacturaExcelZip(forms.Form):
    fecha_inicial = forms.DateField(required=True)
    fecha_final = forms.DateField(required=True)


class PagoBuscarForm(forms.Form):
    fecha_inicial = forms.DateField(required=True)
    fecha_final = forms.DateField(required=True)
    estado_de_cuenta = forms.FileField(required=False, allow_empty_file=False)


class PagoConsolidarForm(forms.Form):
    id_factura = forms.CharField(required=True, widget=forms.HiddenInput())
    fecha_factura = forms.CharField(required=False, disabled=True)
    uuid = forms.CharField(required=False, disabled=True)
    folio = forms.CharField(required=False, disabled=True)
    nombre_cliente = forms.CharField(required=False, disabled=True)
    rfc_cliente = forms.CharField(required=False, disabled=True)
    concepto = forms.CharField(required=False, disabled=True)
    total = forms.DecimalField(decimal_places=2, max_digits=20, required=False, disabled=True)
    moviento_cuenta = forms.CharField(required=False, disabled=True,
                                      widget=forms.Textarea(attrs={'rows': 3, 'cols': 75}))
    fecha_pago = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
