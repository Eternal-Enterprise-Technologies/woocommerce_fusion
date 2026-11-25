import frappe


def execute():
	"""Set gst_state and gst_state_number on addresses used by WooCommerce Sales Orders."""
	if not frappe.get_meta("Address").has_field("gst_state_number"):
		return

	from india_compliance.gst_india.constants import STATE_NUMBERS

	sales_order = frappe.qb.DocType("Sales Order")

	address_names = set()
	for fieldname in ("customer_address", "shipping_address_name"):
		address_names.update(
			frappe.qb.from_(sales_order)
			.select(sales_order[fieldname])
			.where(sales_order.woocommerce_id.isnotnull() & (sales_order[fieldname].isnotnull()))
			.distinct()
			.run(pluck=True)
		)

	if not address_names:
		return

	addresses = frappe.get_all(
		"Address",
		filters={"name": ("in", list(address_names)), "country": "India"},
		fields=["name", "state", "gst_state_number"],
	)
	for row in addresses:
		if row.gst_state_number or row.state not in STATE_NUMBERS:
			continue
		frappe.db.set_value(
			"Address",
			row.name,
			{"gst_state": row.state, "gst_state_number": STATE_NUMBERS[row.state]},
			update_modified=False,
		)
