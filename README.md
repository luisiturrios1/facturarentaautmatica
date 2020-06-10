# Factura Renta Autmatica

Aplicación web en Django para facturar automáticamente recibos de renta.

## Contacto

ING. Luis Jesus Iturrios [iturrios3063@gmail.com](iturrios3063@gmail.com)

## Pasar CSD .key de DER a PEM
```
openssl pkcs8 -inform DER -passin pass:12345678a -h -in CSD_Pruebas_CFDI_LAN7008173R5.key -out CSD_Pruebas_CFDI_LAN7008173R5.pem.key
```