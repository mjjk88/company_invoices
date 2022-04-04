from datetime import datetime

from company_invoices.db_model import Invoice, InvoiceItem
from company_invoices.value_error_handler import handle_value_error


def batch_map_chargebee_response_to_internal_model(invoices):
    invoices_to_commit = []
    invoices_items_to_commit = []
    for invoice in invoices.response:
        internal_invoice = invoice['invoice']
        try:
            validated_invoice, validated_invoice_items = _map_invoice(internal_invoice)

            invoices_to_commit.append(validated_invoice)
            invoices_items_to_commit.extend(validated_invoice_items)

        except (ValueError, KeyError) as e:
            handle_value_error(internal_invoice, e)

    return invoices_to_commit, invoices_items_to_commit


def _map_invoice(internal_invoice):
    validated_invoice = Invoice(invoice_id=internal_invoice['id'],
                                customer_id=internal_invoice['customer_id'],
                                subscription_id=internal_invoice['subscription_id'],
                                status=internal_invoice['status'],
                                issue_date=datetime.fromtimestamp(internal_invoice['date']),
                                # timestamp will be converted to the datetime object and sqlalchemy will store
                                # them properly based on sql engine (for sqlite in Text based Date format in UTC)
                                due_date=datetime.fromtimestamp(internal_invoice['due_date']),
                                # timestamp will be converted to the datetime object and sqlalchemy will store
                                # them properly based on sql engine (for sqlite in Text based Date format in UTC)
                                credits_applied=internal_invoice['credits_applied']
                                )
    # It's more readable and safer to catch KeyError instead playing with None.
    # We could use 'get' method (e.g. internal_invoice.get('id')) to return None instead of KeyError,
    # but it would not resolve the problem with None in timestamp (datetime.fromtimestamp() will be crashed)
    # and we relay on extra Invoice validation.

    # I assume that invoice has to have at lease 1 item
    if not internal_invoice['line_items']:
        raise KeyError("'line_items' is empty")
    validated_invoice_items = []
    for item in internal_invoice['line_items']:
        validated_invoice_items.append(InvoiceItem(item_id=item['id'],
                                                   invoice_id=internal_invoice['id'],
                                                   customer_id=internal_invoice['customer_id'],
                                                   subscription_id=internal_invoice['subscription_id'],
                                                   object=item['object'],
                                                   unit_amount=item['unit_amount'],
                                                   quantity=item['quantity'],
                                                   amount=item['amount'],
                                                   discount_amount=item['discount_amount']
                                                   )
                                       )
    return validated_invoice, validated_invoice_items
