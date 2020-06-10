# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.urls import reverse_lazy

DIAS_MES = (
    (0, 'Factura Manual'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'),
    (10, '10'), (11, '11'), (12, '12'), (13, '13'), (14, '14'), (15, '15'), (16, '16'), (17, '17'),
    (18, '18'), (19, '19'), (20, '20'), (21, '21'), (22, '22'), (23, '23'), (24, '24'), (25, '25'),
    (26, '26'), (27, '27'), (28, '28'),
)

USO_CFDI = (
    ('P01', u'Por definir'),
    ('G03', u'Gastos en general'),
    ('I01', u'Construcciones'),
    ('I02', u'Mobilario y equipo de oficina por inversiones'),
    ('G01', u'Adquisición de mercancias'),
    ('G02', u'Devoluciones, descuentos o bonificaciones'),
    ('I03', u'Equipo de transporte'),
    ('I04', u'Equipo de computo y accesorios'),
    ('I05', u'Dados, troqueles, moldes, matrices y herramental'),
    ('I06', u'Comunicaciones telefónicas'),
    ('I07', u'Comunicaciones satelitales'),
    ('I08', u'Otra maquinaria y equipo'),
    ('D01', u'Honorarios médicos, dentales y gastos hospitalarios'),
    ('D02', u'Gastos médicos por incapacidad o discapacidad'),
    ('D03', u'Gastos funerales'),
    ('D04', u'Donativos'),
    ('D05', u'Intereses reales efectivamente pagados por créditos hipotecarios (casa habitación)'),
    ('D06', u'Aportaciones voluntarias al SAR'),
    ('D07', u'Primas por seguros de gastos médicos'),
    ('D08', u'Gastos de transportación escolar obligatoria'),
    ('D09', u'Depósitos en cuentas para el ahorro, primas que tengan como base planes de pensiones'),
    ('D10', u'Pagos por servicios educativos (colegiaturas)'),
)

METODO_PAGO = (
    ('PUE', u'Pago en una sola exhibición'),
    ('PPD', u'Pago en parcialidades o diferido'),
)

FORMA_PAGO = (
    ('01', u'Efectivo'),
    ('02', u'Cheque nominativo'),
    ('03', u'Transferencia electrónica de fondos'),
    ('04', u'Tarjeta de crédito'),
    ('05', u'Monedero electrónico'),
    ('06', u'Dinero electrónico'),
    ('08', u'Vales de despensa'),
    ('12', u'Dación en pago'),
    ('13', u'Pago por subrogación'),
    ('14', u'Pago por consignación'),
    ('15', u'Condonación'),
    ('17', u'Compensación'),
    ('23', u'Novación'),
    ('24', u'Confusión'),
    ('25', u'Remisión de deuda'),
    ('26', u'Prescripción o caducidad'),
    ('27', u'A satisfacción del acreedor'),
    ('28', u'Tarjeta de débito'),
    ('29', u'Tarjeta de servicios'),
    ('99', u'Por definir'),
)


class Contrato(models.Model):
    nombre_predio = models.CharField(max_length=100, null=False, blank=False)
    cuenta_predial = models.CharField(max_length=100, null=True, blank=True)

    nombre_cliente = models.CharField(max_length=100, null=False, blank=False)
    rfc_cliente = models.CharField(max_length=13, null=False, blank=False)
    correo_cliente = models.EmailField(null=False, blank=False)
    telefono_cliente = models.CharField(max_length=10, null=True, blank=True)

    saldo_contrato = models.DecimalField(max_digits=20, decimal_places=2, null=False, blank=False, default=0)
    precio_mensual = models.DecimalField(
        max_digits=20, decimal_places=2, null=False, help_text=u'Ingrese el precio antes de impuestos'
    )
    retener_impuestos = models.BooleanField(
        null=False, default=False, blank=False, help_text=u'Marque esta casilla si desea rentener ISR e IVA'
    )
    uso_cfdi = models.CharField(max_length=3, null=False, default='G03', choices=USO_CFDI)
    metodo_pago = models.CharField(max_length=3, null=False, default='PUE', choices=METODO_PAGO)
    forma_pago = models.CharField(max_length=3, null=False, default='01', choices=FORMA_PAGO)

    dia_facturacion = models.IntegerField(null=False, blank=False, default=1, choices=DIAS_MES)

    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_modificado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre_predio

    def __unicode__(self):
        return self.nombre_predio

    def get_absolute_url(self):
        return reverse_lazy('webapp:contrato-detail', kwargs={'pk': self.pk})

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.nombre_predio = self.nombre_predio.upper()
        self.nombre_cliente = self.nombre_cliente.upper()
        self.rfc_cliente = self.rfc_cliente.upper()
        self.correo_cliente = self.correo_cliente.lower()
        super(Contrato, self).save(force_insert, force_update, using, update_fields)


class Configuracion(models.Model):
    nombre = models.CharField(max_length=10, unique=True, null=False, blank=False)
    valor = models.IntegerField(null=False)

    def __unicode__(self):
        return self.nombre

    def __str__(self):
        return self.nombre


class Factura(models.Model):
    uuid = models.UUIDField(unique=True, null=False, db_index=True)
    uuid_rep = models.UUIDField(null=True)
    serie = models.CharField(max_length=10, null=False, blank=False)
    folio = models.IntegerField(null=False)
    fecha = models.DateField(null=False, blank=False)

    nombre_cliente = models.CharField(max_length=100, null=False, blank=False)
    rfc_cliente = models.CharField(max_length=13, null=False, blank=False)
    correo_cliente = models.EmailField(null=False, blank=False)

    concepto = models.CharField(max_length=500, null=False, blank=False)
    sub_total = models.DecimalField(max_digits=20, decimal_places=2, null=False, blank=False, default=0)
    iva_trasladado = models.DecimalField(max_digits=20, decimal_places=2, null=False, blank=False, default=0)
    iva_retenido = models.DecimalField(max_digits=20, decimal_places=2, null=False, blank=False, default=0)
    isr_retenido = models.DecimalField(max_digits=20, decimal_places=2, null=False, blank=False, default=0)
    total = models.DecimalField(max_digits=20, decimal_places=2, null=False, blank=False, default=0)

    contrato = models.ForeignKey('webapp.Contrato', null=True, on_delete=models.SET_NULL)

    pagada = models.BooleanField(null=False, default=False)
    fecha_pago = models.DateField(null=True, blank=True)
    forma_pago_rep = models.CharField(max_length=2, null=True, blank=True, choices=FORMA_PAGO)
    num_operacion = models.CharField(max_length=100, null=True, blank=True)

    pdf = models.FileField(upload_to='facturas', null=False)
    xml = models.FileField(upload_to='facturas', null=False)
    pdf_rep = models.FileField(upload_to='rep', null=True)
    xml_rep = models.FileField(upload_to='rep', null=True)

    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_modificado = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.concepto

    def __str__(self):
        return self.concepto

    def get_absolute_url(self):
        return reverse_lazy('webapp:factura-detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-id']
