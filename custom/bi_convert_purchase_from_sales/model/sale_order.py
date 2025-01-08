from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'



    purchase_order_count = fields.Integer( string= "Number of Purchase Order Generated",compute='_compute_purchase_order_count',groups='purchase.group_purchase_user')

    @api.depends('order_line.purchase_line_ids.order_id')
    def _compute_purchase_order_count(self):
        for order in self:
            order.purchase_order_count = len(order._get_purchase_orders())


    def action_open_purchase_order(self):
        tree_id = self.env.ref("purchase.purchase_order_kpis_tree").id
        form_id = self.env.ref("purchase.purchase_order_form").id
        return {
            "name": _("Requests for Quotation"),
            "view_mode": "tree,form",
            'views': [(tree_id, 'tree'),(form_id,'form')],
            "res_model": "purchase.order",
            "domain":[('origin', '=', self.name)],
            "type": "ir.actions.act_window",
            "target": "current",
            "incoterm_id":self.incoterm,
        }

    def _get_po(self):

        for orders in self:
            purchase_ids = self.env['purchase.order'].search([('origin', '=', self.name)])
        orders.po_count = len(purchase_ids)

    po_count = fields.Integer(string='Purchase Order', compute='_get_po' )
