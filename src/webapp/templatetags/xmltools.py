# -*- coding: utf-8 -*-
from django.template import Library

register = Library()


@register.filter()
def get_data(d, k):
    """
    Regresa el valor del diccionario especificar subllaves asi:
        padre->hijo->llave
    :param d: Diccionario
    :param k: Llave del diccionario
    :return: Valor de la llave o none
    """
    for key in k.split('->'):
        key = key.strip()
        if key in d:
            d = d[key]
        else:
            d = ''
    return d
