# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
	(r'^/invoice/Faktura-RostiCZ-([0-9]*).pdf$', 'wsgiadmin.invoices.views.invoice_get'),
	(r'^/next_payment_id/+$', 'wsgiadmin.invoices.views.next_payment_id'),
	(r'^/items/([0-9]{1,9})/?$', 'wsgiadmin.invoices.views.items'),
	(r'^/stats/?$', 'wsgiadmin.invoices.views.stats'),
	(r'^/show/?$', 'wsgiadmin.invoices.views.show'),
	(r'^/show/([0-9]{1,11})/?$', 'wsgiadmin.invoices.views.show'),
	(r'^/rm/([0-9]{1,11})/?$', 'wsgiadmin.invoices.views.rm'),
	(r'^/rm_item/([0-9]{1,11})/?$', 'wsgiadmin.invoices.views.rm_item'),
	(r'^/invoice/add/?$', 'wsgiadmin.invoices.views.add_invoice'),
	(r'^/invoice/update/([0-9]{1,11})/?$', 'wsgiadmin.invoices.views.update_invoice'),
	(r'^/invoice/send/([0-9]{1,11})/?$', 'wsgiadmin.invoices.views.send_invoice'),
    (r'^/invoice/send/([0-9]{1,11})/(1)/?$', 'wsgiadmin.invoices.views.send_invoice'),
	(r'^/invoice/payback/([0-9]{1,11})/?$', 'wsgiadmin.invoices.views.payback'),
	(r'^/invoice/item/add/([0-9]{1,11})/?$', 'wsgiadmin.invoices.views.add_item'),
	(r'^/invoice/item/update/([0-9]{1,11})/?$', 'wsgiadmin.invoices.views.update_item'),
)

