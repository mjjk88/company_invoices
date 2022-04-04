import copy
import unittest
from datetime import datetime

from company_invoices.db_model import Invoice, InvoiceItem
from company_invoices.invoices_mapper import _map_invoice


# Map DB Model to dict to be able to call equals on them as default model contains extra fields that fail matching
# This is ugly hack just for tests
def row_to_dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = getattr(row, column.name)

    return d


EXAMPLE_DATA = {'id': '539', 'customer_id': '1mkVvx7QVBYMKxqiD', 'subscription_id': '2smoc97SQVBnuRFtlI',
                'status': 'posted',
                'date': 1632301999, 'due_date': 1633597999,
                'credits_applied': 0,
                'object': 'invoice',
                'recurring': True,
                'line_items': [
                    {'id': 'li_16A6PlSjjIqxy17f9', 'date_from': 1632301999, 'date_to': 1634893999,
                     'unit_amount': 7900,
                     'quantity': 1, 'amount': 7900, 'pricing_model': 'flat_fee', 'is_taxed': False,
                     'tax_amount': 0,
                     'object': 'line_item', 'subscription_id': '2smoc97SQVBnuRFtlI',
                     'customer_id': '1mkVvx7QVBYMKxqiD',
                     'description': 'Essential 25 Monthly', 'entity_type': 'plan',
                     'entity_id': 'essential-25-monthly', 'tax_exempt_reason': 'customer_exempt',
                     'discount_amount': 0, 'item_level_discount_amount': 0}]
                }


# Atomicity tests: either the invoice row is push to both tables or to None
# We have to have consistent information about invoice and invoice item in both tables.
# We should test if:
#  - the info about the invoice is saved to both - the invoice and invoice_items (which are later committed to db)
#  - in case of errors, both are not saved saved
class TestAtomicityOfInvoicesMapper(unittest.TestCase):

    def test_should_map_invoice_and_items(self):
        test_data = copy.deepcopy(EXAMPLE_DATA)

        invoice, invoice_items = _map_invoice(test_data)

        expected_invoice = Invoice(invoice_id="539",
                                   customer_id="1mkVvx7QVBYMKxqiD",
                                   subscription_id="2smoc97SQVBnuRFtlI",
                                   status="posted",
                                   issue_date=datetime.fromtimestamp(1632301999),
                                   due_date=datetime.fromtimestamp(1633597999),
                                   credits_applied=0)
        expected_item = InvoiceItem(item_id="li_16A6PlSjjIqxy17f9",
                                    invoice_id="539",
                                    customer_id="1mkVvx7QVBYMKxqiD",
                                    subscription_id="2smoc97SQVBnuRFtlI",
                                    object="line_item",
                                    unit_amount=7900,
                                    quantity=1,
                                    amount=7900,
                                    discount_amount=0)
        self.assertEqual(row_to_dict(invoice), row_to_dict(expected_invoice))
        self.assertListEqual([row_to_dict(i) for i in invoice_items], [row_to_dict(expected_item)])

    def test_should_not_map_anything_if_invoice_has_missing_field(self):
        test_data = copy.deepcopy(EXAMPLE_DATA)
        del test_data['subscription_id']

        with self.assertRaises(KeyError):
            _map_invoice(test_data)

    def test_should_not_map_anything_if_invoice_has_incorrect_field(self):
        test_data = copy.deepcopy(EXAMPLE_DATA)
        test_data['subscription_id'] = ""

        with self.assertRaises(ValueError):
            _map_invoice(test_data)

    def test_should_not_map_anything_if_invoice_item_has_incorrect_field(self):
        test_data = copy.deepcopy(EXAMPLE_DATA)
        test_data['line_items'][0]['amount'] = 0

        with self.assertRaises(ValueError):
            _map_invoice(test_data)


if __name__ == '__main__':
    unittest.main()
