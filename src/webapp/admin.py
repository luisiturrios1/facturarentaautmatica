# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from webapp import models

admin.site.register(models.Configuracion)
admin.site.register(models.Contrato)
admin.site.register(models.Factura)
