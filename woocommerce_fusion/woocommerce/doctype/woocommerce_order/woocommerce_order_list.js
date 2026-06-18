// Copyright (c) 2024, Dirk van der Laarse and contributors
// For license information, please see license.txt

frappe.listview_settings["WooCommerce Order"] = {
	add_fields: ["status", "woocommerce_server", "total", "currency", "date_created"],
	get_indicator: function (doc) {
		const statusColorMap = {
			pending: "orange",
			"on-hold": "grey",
			failed: "red",
			cancelled: "red",
			processing: "blue",
			refunded: "grey",
			completed: "green",
			"ready-pickup": "yellow",
			pickup: "light-green",
			delivered: "green",
			"processing-lp": "purple",
			"checkout-draft": "grey",
			"gplsquote-req": "grey",
			trash: "red",
			"partial-shipped": "light-blue",
			"dispatched-pickup": "purple",
		};
		const color = statusColorMap[doc.status] || "grey";
		return [__(doc.status), color, "status,=," + doc.status];
	},
	onload: function (listview) {
		listview.page.add_action_item(__("Sync Selected to ERPNext"), function () {
			const selected = listview.get_checked_items();
			if (!selected.length) {
				frappe.msgprint(__("Please select at least one WooCommerce Order to sync."));
				return;
			}

			const order_names = selected.map((item) => item.name);

			frappe.confirm(
				__("Sync {0} selected order(s) to ERPNext?", [order_names.length]),
				function () {
					frappe.dom.freeze(__("Queuing orders for sync..."));
					frappe.call({
						method: "woocommerce_fusion.tasks.sync_sales_orders.bulk_sync_woocommerce_orders",
						args: {
							order_names: order_names,
						},
						callback: function (r) {
							frappe.dom.unfreeze();
							if (r.message) {
								frappe.show_alert(
									{
										message: __(
											"{0} order(s) queued for sync. Check background jobs for progress.",
											[r.message.enqueued]
										),
										indicator: "green",
									},
									7
								);
							}
							listview.clear_checked_items();
							listview.refresh();
						},
						error: function () {
							frappe.dom.unfreeze();
							frappe.show_alert(
								{
									message: __(
										"There was an error processing the request. See Error Log."
									),
									indicator: "red",
								},
								5
							);
						},
					});
				}
			);
		});
	},
};
