import frappe
from frappe.tests import UnitTestCase

from woocommerce_fusion.tasks.sync_sales_orders import SynchroniseSalesOrder


class TestMarkTaxesIncludedInRate(UnitTestCase):
	def _sales_order(self, *charge_types):
		taxes = [
			frappe._dict(charge_type=charge_type, included_in_print_rate=0) for charge_type in charge_types
		]
		return frappe._dict(taxes=taxes)

	def test_marks_net_total_and_previous_row_amount_rows_when_prices_include_tax(self):
		sales_order = self._sales_order("On Net Total", "On Previous Row Amount")

		SynchroniseSalesOrder.mark_taxes_included_in_rate(sales_order, frappe._dict(prices_include_tax=1))

		self.assertEqual([tax.included_in_print_rate for tax in sales_order.taxes], [1, 1])

	def test_skips_rows_erpnext_cannot_treat_as_inclusive(self):
		sales_order = self._sales_order("Actual", "On Previous Row Total", "On Item Quantity")

		SynchroniseSalesOrder.mark_taxes_included_in_rate(sales_order, frappe._dict(prices_include_tax=1))

		self.assertEqual([tax.included_in_print_rate for tax in sales_order.taxes], [0, 0, 0])

	def test_leaves_rows_untouched_when_prices_exclude_tax(self):
		sales_order = self._sales_order("On Net Total")

		SynchroniseSalesOrder.mark_taxes_included_in_rate(sales_order, frappe._dict(prices_include_tax=0))

		self.assertEqual(sales_order.taxes[0].included_in_print_rate, 0)
