# -*- coding: utf-8 -*-
import base64
import hashlib
import requests
from lxml import etree
from decimal import Decimal, ROUND_HALF_UP, getcontext
from base64 import b64encode
from cStringIO import StringIO

from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils import timezone

import pdfkit
import qrcode
import xmltodict
from M2Crypto import X509, RSA
from requests_toolbelt import MultipartEncoder
from celery import shared_task
from celery.utils.log import get_task_logger

from webapp import models

logger = get_task_logger(__name__)

TWO_PLACES = Decimal(10) ** -2


def nombre_mes(mes):
    if mes == 1:
        return 'Enero'
    elif mes == 2:
        return 'Febrero'
    elif mes == 3:
        return 'Marzo'
    elif mes == 4:
        return 'Abril'
    elif mes == 5:
        return 'Mayo'
    elif mes == 6:
        return 'Junio'
    elif mes == 7:
        return 'Julio'
    elif mes == 8:
        return 'Agosto'
    elif mes == 9:
        return 'Septiembre'
    elif mes == 10:
        return 'Octubre'
    elif mes == 11:
        return 'Noviembre'
    elif mes == 12:
        return 'Diciembre'
    return mes


@shared_task()
def facturar(contrato_id, descripcion=None, sub_total=None):
    logger.info('Task facturar iniciada')

    # Configurar redondeo
    getcontext().rounding = ROUND_HALF_UP

    # Calcular fecha actual
    fecha = timezone.localtime()

    # Consultar contrato
    contrato = models.Contrato.objects.get(id=contrato_id)

    # Si no se envia descripcion factura el mes correspondiente a la fecha actual
    if descripcion is None:
        sub_total = contrato.precio_mensual
        descripcion = u'Renta correspondiente al mes {0} del {1} {2}'.format(
            nombre_mes(fecha.month), fecha.year, contrato.nombre_predio
        )

    # Calcular impuestos
    iva_tra = (sub_total * Decimal('0.160000')).quantize(TWO_PLACES)
    iva_ret = Decimal('0.00')
    isr_ret = Decimal('0.00')

    if contrato.retener_impuestos:
        iva_ret = (sub_total * Decimal('0.106666')).quantize(TWO_PLACES)
        isr_ret = (sub_total * Decimal('0.100000')).quantize(TWO_PLACES)

    total_tra = iva_tra
    total_ret = (iva_ret + isr_ret).quantize(TWO_PLACES)
    total = ((sub_total + total_tra) - total_ret).quantize(TWO_PLACES)

    # Cargar certificado CSD
    cer = X509.load_cert(settings.CSD_CER, X509.FORMAT_DER)

    # Cargar llave privada CSD
    key = RSA.load_key(settings.CSD_KEY)

    # Obtener numero de serie
    serial_number = '{:x}'.format(int(cer.get_serial_number())).decode('hex')

    # Obtener folio
    folio_conf = models.Configuracion.objects.get(nombre='U_FOLIO')
    folio_conf.valor = folio_conf.valor + 1
    folio_conf.save()

    nsmap = {
        'cfdi': 'http://www.sat.gob.mx/cfd/3',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    }

    attrib = {
        '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation': 'http://www.sat.gob.mx/cfd/3'
    }

    # Nodo cfdi:Comprobante
    cfdi = etree.Element('{http://www.sat.gob.mx/cfd/3}Comprobante', nsmap=nsmap, attrib=attrib)

    cfdi.set('Version', '3.3')
    cfdi.set('Serie', settings.SERIE)
    cfdi.set('Folio', str(folio_conf.valor))
    cfdi.set('Fecha', fecha.isoformat()[:19])
    cfdi.set('FormaPago', contrato.forma_pago)
    cfdi.set('NoCertificado', serial_number)
    cfdi.set('Certificado', base64.b64encode(cer.as_der()))
    cfdi.set('SubTotal', '{}'.format(sub_total))
    cfdi.set('Moneda', settings.MONEDA)
    cfdi.set('Total', '{}'.format(total))
    cfdi.set('TipoDeComprobante', 'I')
    cfdi.set('MetodoPago', contrato.metodo_pago)
    cfdi.set('LugarExpedicion', settings.CODIGO_POSTAL)

    # Nodo cfdi:Emisor
    emisor = etree.SubElement(cfdi, '{http://www.sat.gob.mx/cfd/3}Emisor')
    emisor.set('Rfc', settings.RFC)
    emisor.set('Nombre', settings.RAZON_SOCIAL)
    emisor.set('RegimenFiscal', settings.REGIMEN_FISCAL)

    # Nodo cfdi:Receptor
    receptor = etree.SubElement(cfdi, '{http://www.sat.gob.mx/cfd/3}Receptor')
    receptor.set('Rfc', contrato.rfc_cliente)
    receptor.set('Nombre', contrato.nombre_cliente)
    receptor.set('UsoCFDI', contrato.uso_cfdi)

    # Nodo cfdi:Conceptos
    conceptos = etree.SubElement(cfdi, '{http://www.sat.gob.mx/cfd/3}Conceptos')

    # Nodo cfdi:Concepto
    concepto = etree.SubElement(conceptos, '{http://www.sat.gob.mx/cfd/3}Concepto')
    concepto.set('ClaveProdServ', settings.CLAVE_PROD_SERV)
    concepto.set('Cantidad', '1')
    concepto.set('ClaveUnidad', settings.CLAVE_UNIDAD)
    concepto.set('Descripcion', descripcion)
    concepto.set('ValorUnitario', '{}'.format(sub_total))
    concepto.set('Importe', '{}'.format(sub_total))

    # Nodo cfdi:Impuestos
    impuestos = etree.SubElement(concepto, '{http://www.sat.gob.mx/cfd/3}Impuestos')

    # Nodo cfdi:Traslados
    traslados = etree.SubElement(impuestos, '{http://www.sat.gob.mx/cfd/3}Traslados')

    # Nodo cfdi:Traslado
    traslado = etree.SubElement(traslados, '{http://www.sat.gob.mx/cfd/3}Traslado')
    traslado.set('Base', '{}'.format(sub_total))
    traslado.set('Impuesto', '002')
    traslado.set('TipoFactor', 'Tasa')
    traslado.set('TasaOCuota', '0.160000')
    traslado.set('Importe', '{}'.format(iva_tra))

    if contrato.retener_impuestos:
        # Nodo cfdi:Retenciones
        retenciones = etree.SubElement(impuestos, '{http://www.sat.gob.mx/cfd/3}Retenciones')

        # Nodo cfdi:Retencion IVA
        traslado = etree.SubElement(retenciones, '{http://www.sat.gob.mx/cfd/3}Retencion')
        traslado.set('Base', '{}'.format(sub_total))
        traslado.set('Impuesto', '002')
        traslado.set('TipoFactor', 'Tasa')
        traslado.set('TasaOCuota', '0.106666')
        traslado.set('Importe', '{}'.format(iva_ret))

        # Nodo cfdi:Retencion ISR
        retencion = etree.SubElement(retenciones, '{http://www.sat.gob.mx/cfd/3}Retencion')
        retencion.set('Base', '{}'.format(sub_total))
        retencion.set('Impuesto', '001')
        retencion.set('TipoFactor', 'Tasa')
        retencion.set('TasaOCuota', '0.100000')
        retencion.set('Importe', '{}'.format(isr_ret))

    if contrato.cuenta_predial is not None:
        cuenta_predial = etree.SubElement(concepto, '{http://www.sat.gob.mx/cfd/3}CuentaPredial')
        cuenta_predial.set('Numero', str(contrato.cuenta_predial))

    # Nodo cfdi:Impuestos
    impuestos = etree.SubElement(cfdi, '{http://www.sat.gob.mx/cfd/3}Impuestos')
    impuestos.set('TotalImpuestosTrasladados', '{}'.format(total_tra))

    if contrato.retener_impuestos:
        impuestos.set('TotalImpuestosRetenidos', '{}'.format(total_ret))

        # Nodo cfdi:Retenciones
        retenciones = etree.SubElement(impuestos, '{http://www.sat.gob.mx/cfd/3}Retenciones')

        # Nodo cfdi:Retencion IVA
        retencion_iva = etree.SubElement(retenciones, '{http://www.sat.gob.mx/cfd/3}Retencion')
        retencion_iva.set('Impuesto', '002')
        retencion_iva.set('Importe', '{}'.format(iva_ret))

        # Nodo cfdi:Retencion ISR
        retencion_isr = etree.SubElement(retenciones, '{http://www.sat.gob.mx/cfd/3}Retencion')
        retencion_isr.set('Impuesto', '001')
        retencion_isr.set('Importe', '{}'.format(isr_ret))

    # Nodo cfdi:Traslados
    traslados = etree.SubElement(impuestos, '{http://www.sat.gob.mx/cfd/3}Traslados')

    # Nodo cfdi:Traslado
    traslado_iva = etree.SubElement(traslados, '{http://www.sat.gob.mx/cfd/3}Traslado')
    traslado_iva.set('Impuesto', '002')
    traslado_iva.set('TipoFactor', 'Tasa')
    traslado_iva.set('TasaOCuota', '0.160000')
    traslado_iva.set('Importe', '{}'.format(iva_tra))

    # Cargar xslt para generar cadena original
    xslt = etree.XSLT(etree.parse(settings.PATH_XLST))

    # Generar cadena original
    cadena_original = xslt(cfdi)

    # sacar hash a cadena original
    digest = hashlib.new('sha256', str(cadena_original)).digest()

    # Firmar digest de cadena original
    sign = key.sign(digest, "sha256")

    # Pasar sello de Bytes a b64
    sello = base64.b64encode(sign)

    # Agrefar sello a documento xml
    cfdi.set('Sello', sello)

    # Generar archivo xml
    xml = etree.tostring(cfdi, pretty_print=True)

    # Format token
    token = 'bearer %s' % str(settings.PAC_TOKEN)

    # Crear mensaje multiparte para adjuntar archivo
    m = MultipartEncoder(fields={'xml': ('xml', xml, 'text/xml', {'Content-Transfer-Encoding': 'binary'})})

    # Crear headers
    headers = {'Content-Type': m.content_type, 'Authorization': token}

    # Realizar request tipo post al pac
    req = requests.post(settings.PAC_URL, headers=headers, data=m.to_string())

    # Verificar request
    if req.status_code != 200:
        raise Exception(u'id_contrato: {} Error {}'.format(contrato.id, req.json()))

    # Extraer xml
    xml_timbrado = req.json()['data']['cfdi'].encode('utf-8')

    # Parsear XML timpado
    cfdi_timbrado = etree.fromstring(xml_timbrado)

    # Buscar UUID
    uuid = cfdi_timbrado.find(
        '{http://www.sat.gob.mx/cfd/3}Complemento'
    ).find(
        '{http://www.sat.gob.mx/TimbreFiscalDigital}TimbreFiscalDigital'
    ).attrib.get('UUID')

    # Generar PDF
    xml_dict = xmltodict.parse(xml_timbrado)['cfdi:Comprobante']

    cbb_url = 'https://verificacfdi.facturaelectronica.sat.gob.mx/' \
              'default.aspx?id={0}re={1}&rr={2}&tt={3}&fe={4}'.format(
        uuid,
        settings.RFC,
        contrato.rfc_cliente,
        total,
        sello[(len(sello) - 8):],
    )

    # Generar codigo qr de cbb
    qrdata = qrcode.make(cbb_url)
    raw = StringIO()
    qrdata.save(raw)
    cbb = b64encode(raw.getvalue())

    # Renderizar HTML
    html = get_template('webapp/factura-pdf.html').render({
        'xml': xml_dict,
        'cadena_original': cadena_original,
        'cbb': cbb,
    })

    # Generar PDF
    pdf = pdfkit.from_string(html, False, options={
        'page-size': 'Letter',
        'encoding': "UTF-8",
        'quiet': '',
    })

    # Guardar factura en base de datos
    factura = models.Factura()
    factura.fecha = fecha
    factura.contrato = contrato
    factura.uuid = uuid
    factura.serie = settings.SERIE
    factura.folio = folio_conf.valor
    factura.nombre_cliente = contrato.nombre_cliente
    factura.rfc_cliente = contrato.rfc_cliente
    factura.correo_cliente = contrato.correo_cliente
    factura.concepto = descripcion
    factura.sub_total = sub_total
    factura.iva_trasladado = iva_tra
    factura.iva_retenido = iva_ret
    factura.isr_retenido = isr_ret
    factura.total = total
    factura.xml = ContentFile(xml_timbrado, name='{0}.xml'.format(uuid))
    factura.pdf = ContentFile(pdf, name='{0}.pdf'.format(uuid))
    factura.save()

    # sumar saldo en contrato
    contrato.saldo_contrato = contrato.saldo_contrato + total
    contrato.save()

    # Enviar correo
    html_email = get_template('webapp/factura-correo.txt').render({'factura': factura})

    msg = EmailMessage(
        '{} Nueva Factura {} {} Generada'.format(settings.RAZON_SOCIAL, factura.serie, factura.folio),
        html_email, settings.DEFAULT_FROM_EMAIL, to=[factura.correo_cliente],
        reply_to=[settings.TENANT_EMAIL], cc=[settings.TENANT_EMAIL]
    )
    msg.attach('{}_{}.xml'.format(factura.serie, factura.folio), factura.xml.read(), 'application/xml')
    msg.attach('{}_{}.pdf'.format(factura.serie, factura.folio), factura.pdf.read(), 'application/pdf')
    msg.send()

    logger.info('Task facturar terminada')

    return factura.id


@shared_task()
def facturar_rep(factura_id):
    logger.info('Task facturar iniciada')

    # Configurar redondeo
    getcontext().rounding = ROUND_HALF_UP

    # Calcular fecha actual
    fecha = timezone.localtime()

    # Consultar contrato
    factura = models.Factura.objects.get(id=factura_id)

    # Calcular impuestos

    # Cargar certificado CSD
    cer = X509.load_cert(settings.CSD_CER, X509.FORMAT_DER)

    # Cargar llave privada CSD
    key = RSA.load_key(settings.CSD_KEY)

    # Obtener numero de serie
    serial_number = '{:x}'.format(int(cer.get_serial_number())).decode('hex')

    # Obtener folio
    folio_conf = models.Configuracion.objects.get(nombre='U_FOLIO')
    folio_conf.valor = folio_conf.valor + 1
    folio_conf.save()

    nsmap = {
        'cfdi': 'http://www.sat.gob.mx/cfd/3',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'pago10': 'http://www.sat.gob.mx/Pagos',
    }

    attrib = {
        '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation': 'http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv33.xsd http://www.sat.gob.mx/Pagos http://www.sat.gob.mx/sitio_internet/cfd/Pagos/Pagos10.xsd'
    }

    # Nodo cfdi:Comprobante
    cfdi = etree.Element('{http://www.sat.gob.mx/cfd/3}Comprobante', nsmap=nsmap, attrib=attrib)

    cfdi.set('Version', '3.3')
    cfdi.set('Serie', settings.SERIE_REP)
    cfdi.set('Folio', str(folio_conf.valor))
    cfdi.set('Fecha', fecha.isoformat()[:19])
    cfdi.set('NoCertificado', serial_number)
    cfdi.set('Certificado', base64.b64encode(cer.as_der()))
    cfdi.set('SubTotal', '0')
    cfdi.set('Moneda', 'XXX')
    cfdi.set('Total', '0')
    cfdi.set('TipoDeComprobante', 'P')
    cfdi.set('LugarExpedicion', settings.CODIGO_POSTAL)

    # Nodo cfdi:Emisor
    emisor = etree.SubElement(cfdi, '{http://www.sat.gob.mx/cfd/3}Emisor')
    emisor.set('Rfc', settings.RFC)
    emisor.set('Nombre', settings.RAZON_SOCIAL)
    emisor.set('RegimenFiscal', settings.REGIMEN_FISCAL)

    # Nodo cfdi:Receptor
    receptor = etree.SubElement(cfdi, '{http://www.sat.gob.mx/cfd/3}Receptor')
    receptor.set('Rfc', factura.rfc_cliente)
    receptor.set('Nombre', factura.nombre_cliente)
    receptor.set('UsoCFDI', 'P01')

    # Nodo cfdi:Conceptos
    conceptos = etree.SubElement(cfdi, '{http://www.sat.gob.mx/cfd/3}Conceptos')

    # Nodo cfdi:Concepto
    concepto = etree.SubElement(conceptos, '{http://www.sat.gob.mx/cfd/3}Concepto')
    concepto.set('ClaveProdServ', '84111506')
    concepto.set('Cantidad', '1')
    concepto.set('ClaveUnidad', 'ACT')
    concepto.set('Descripcion', 'Pago')
    concepto.set('ValorUnitario', '0.000000')
    concepto.set('Importe', '0.00')

    # Nodo cfdi:Conceptos
    complemento = etree.SubElement(cfdi, '{http://www.sat.gob.mx/cfd/3}Complemento')

    # Nodo pago10:Pagos
    pagos = etree.SubElement(complemento, '{http://www.sat.gob.mx/Pagos}Pagos')
    pagos.set('Version', '1.0')

    # Nodo pago10:Pagos
    pago = etree.SubElement(pagos, '{http://www.sat.gob.mx/Pagos}Pago')
    pago.set('FechaPago', '{}T01:00:00'.format(factura.fecha_pago.isoformat()))
    pago.set('FormaDePagoP', factura.forma_pago_rep)
    pago.set('MonedaP', settings.MONEDA)
    pago.set('Monto', '{}'.format(factura.total))
    pago.set('NumOperacion', factura.num_operacion)

    # Nonda pago10:DoctoRelacionado
    docto_relacionado = etree.SubElement(pago, '{http://www.sat.gob.mx/Pagos}DoctoRelacionado')
    docto_relacionado.set('IdDocumento', '{}'.format(factura.uuid))
    docto_relacionado.set('Serie', factura.serie)
    docto_relacionado.set('Folio', '{}'.format(factura.folio))
    docto_relacionado.set('MonedaDR', settings.MONEDA)
    docto_relacionado.set('MetodoDePagoDR', factura.contrato.metodo_pago)
    docto_relacionado.set('NumParcialidad', '1')
    docto_relacionado.set('ImpSaldoAnt', '{}'.format(factura.total))
    docto_relacionado.set('ImpPagado', '{}'.format(factura.total))
    docto_relacionado.set('ImpSaldoInsoluto', '0')

    # Cargar xslt para generar cadena original
    xslt = etree.XSLT(etree.parse(settings.PATH_XLST))

    # Generar cadena original
    cadena_original = xslt(cfdi)

    # sacar hash a cadena original
    digest = hashlib.new('sha256', str(cadena_original)).digest()

    # Firmar digest de cadena original
    sign = key.sign(digest, "sha256")

    # Pasar sello de Bytes a b64
    sello = base64.b64encode(sign)

    # Agrefar sello a documento xml
    cfdi.set('Sello', sello)

    # Generar archivo xml
    xml = etree.tostring(cfdi, pretty_print=True)

    # Format token
    token = 'bearer %s' % str(settings.PAC_TOKEN)

    # Crear mensaje multiparte para adjuntar archivo
    m = MultipartEncoder(fields={'xml': ('xml', xml, 'text/xml', {'Content-Transfer-Encoding': 'binary'})})

    # Crear headers
    headers = {'Content-Type': m.content_type, 'Authorization': token}

    # Realizar request tipo post al pac
    req = requests.post(settings.PAC_URL, headers=headers, data=m.to_string())

    # Verificar request
    if req.status_code != 200:
        raise Exception(u'id_factura: {} Error {}'.format(factura.id, req.json()))

    # Extraer xml
    xml_timbrado = req.json()['data']['cfdi'].encode('utf-8')

    # Parsear XML timpado
    cfdi_timbrado = etree.fromstring(xml_timbrado)

    # Buscar UUID
    uuid = cfdi_timbrado.find(
        '{http://www.sat.gob.mx/cfd/3}Complemento'
    ).find(
        '{http://www.sat.gob.mx/TimbreFiscalDigital}TimbreFiscalDigital'
    ).attrib.get('UUID')

    # Generar PDF
    xml_dict = xmltodict.parse(xml_timbrado)['cfdi:Comprobante']

    cbb_url = 'https://verificacfdi.facturaelectronica.sat.gob.mx/' \
              'default.aspx?id={0}re={1}&rr={2}&tt={3}&fe={4}'.format(
        uuid,
        settings.RFC,
        factura.rfc_cliente,
        factura.total,
        sello[(len(sello) - 8):],
    )

    # Generar codigo qr de cbb
    qrdata = qrcode.make(cbb_url)
    raw = StringIO()
    qrdata.save(raw)
    cbb = b64encode(raw.getvalue())

    # Renderizar HTML
    html = get_template('webapp/factura-pago-pdf.html').render({
        'xml': xml_dict,
        'cadena_original': cadena_original,
        'cbb': cbb,
    })

    # Generar PDF
    pdf = pdfkit.from_string(html, False, options={
        'page-size': 'Letter',
        'encoding': "UTF-8",
        'quiet': '',
    })

    # Guardar factura en base de datos
    factura.uuid_rep = uuid
    factura.xml_rep = ContentFile(xml_timbrado, name='{0}.xml'.format(uuid))
    factura.pdf_rep = ContentFile(pdf, name='{0}.pdf'.format(uuid))
    factura.save()

    # Enviar correo
    html_email = get_template('webapp/factura-correo.txt').render({'factura': factura})

    msg = EmailMessage(
        '{} Nuevo REP {} {} Generada'.format(settings.RAZON_SOCIAL, factura.serie, factura.folio),
        html_email, settings.DEFAULT_FROM_EMAIL, to=[factura.correo_cliente],
        reply_to=[settings.TENANT_EMAIL], cc=[settings.TENANT_EMAIL]
    )
    msg.attach('{}_{}.xml'.format(factura.serie, factura.folio), factura.xml.read(), 'application/xml')
    msg.attach('{}_{}.pdf'.format(factura.serie, factura.folio), factura.pdf.read(), 'application/pdf')

    msg.attach('{}_{}.xml'.format(factura.serie, factura.folio), factura.xml_rep.read(), 'application/xml')
    msg.attach('{}_{}.pdf'.format(factura.serie, factura.folio), factura.pdf_rep.read(), 'application/pdf')
    msg.send()

    logger.info('Task facturar terminada')

    return factura.id


@shared_task()
def reenviar_correo(factura_id):
    logger.info('Task reenviar_correo iniciada')

    # Consultar contrato
    factura = models.Factura.objects.get(id=factura_id)

    # Enviar correo
    html_email = get_template('webapp/factura-correo.txt').render({'factura': factura})

    msg = EmailMessage(
        '{} Factura {} {} Generada'.format(settings.RAZON_SOCIAL, factura.serie, factura.folio),
        html_email, settings.DEFAULT_FROM_EMAIL, to=[factura.correo_cliente],
        reply_to=[settings.TENANT_EMAIL], cc=[settings.TENANT_EMAIL]
    )
    msg.attach('{}_{}.xml'.format(factura.serie, factura.folio), factura.xml.read(), 'application/xml')
    msg.attach('{}_{}.pdf'.format(factura.serie, factura.folio), factura.pdf.read(), 'application/pdf')

    msg.send()

    logger.info('Task reenviar_correo terminada')

    return factura.id


@shared_task()
def regenerar_pdf():
    """
    Regenera todos los PDF
    """
    contador = 0

    facturas = models.Factura.objects.all()

    for factura in facturas:
        xml_text = factura.xml.read()
        # Generar PDF
        xml_dict = xmltodict.parse(xml_text)['cfdi:Comprobante']

        # Cargar xslt para generar cadena original
        xslt = etree.XSLT(etree.parse(settings.PATH_XLST))

        # Generar cadena original
        cadena_original = xslt(etree.fromstring(xml_text))

        cbb_url = 'https://verificacfdi.facturaelectronica.sat.gob.mx/' \
                  'default.aspx?id={0}re={1}&rr={2}&tt={3}&fe={4}'.format(
            factura.uuid,
            settings.RFC,
            factura.rfc_cliente,
            factura.total,
            xml_dict['@Sello'][-8:],
        )

        # Generar codigo qr de cbb
        qrdata = qrcode.make(cbb_url)
        raw = StringIO()
        qrdata.save(raw)
        cbb = b64encode(raw.getvalue())

        # Renderizar HTML
        html = get_template('webapp/factura-pdf.html').render({
            'xml': xml_dict,
            'cadena_original': cadena_original,
            'cbb': cbb,
        })

        # Generar PDF
        pdf = pdfkit.from_string(html, False, options={
            'page-size': 'Letter',
            'encoding': "UTF-8",
            'quiet': '',
        })

        # Guardar factura en base de datos
        with open(factura.pdf.path, 'w+') as f:
            f.write(pdf)
        contador += 1

    return contador


@shared_task()
def email_test(email):
    logger.info('Task email_test iniciada')

    msg = EmailMessage(
        u'Mensaje de prueba desde una tarea', u'Mensaje de prueba desde una tarea',
        settings.DEFAULT_FROM_EMAIL, to=[email],
        reply_to=[settings.TENANT_EMAIL], cc=[settings.TENANT_EMAIL]
    )
    msg.send()

    logger.info('Task email_test terminada')

    return 'OK'
