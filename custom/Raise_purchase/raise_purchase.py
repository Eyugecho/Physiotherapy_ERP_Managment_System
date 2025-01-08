from odoo import models,fields,_,api


class account_move(models.Model):
    _inherit = "account.move"

    order_sales_id = fields.Many2one('sale.order', string="Order From", compute='_compute_order_from')
    lc_number=fields.Char(string="LC Number")
    # place_delivery=fields.Char(string="Port Of Discharge")
    place_delivery = fields.Many2many(comodel_name="rise.port", string="Port of Discharge/Port of Loading", related="order_sales_id.port_discharge", readonly=True)




    
    api.depends('invoice_origin')
    def _compute_order_from(self):
        for record in self:
            recs = self.env['sale.order'].search([('name', '=', record.invoice_origin)])
            if recs:
                record.order_sales_id = recs[0].id
    
    
class ResPartner(models.Model):
    _inherit = "res.partner"
    condtact_p=fields.Char(string="Contact Person")

class ResCompany(models.Model):
    _inherit = "res.company"
    is_company_details_empty=fields.Boolean(string="Company")
    # contact_person = fields.Char('Contact Person')

# class StockPicking(models.Model):
    
#     _inherit = "stock.picking"

#     port_discharge=fields.Char(string="Port of Discharge")
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    stock_move_sms_validation = fields.Boolean(
        string='Enable SMS Validation for Stock Moves'
    )
    
    stock_sms_confirmation_template_id = fields.Many2one(
        'sms.template', string="SMS Template")

    digest_emails = fields.Boolean(string="Digest Emails", config_parameter='digest.default_digest_emails')
    digest_id = fields.Many2one('digest.digest', string='Digest Email', config_parameter='digest.default_digest_id')


class RaiseShipment(models.Model):
    _name="raise.product.packaging"

    name=fields.Char(string="Container")
    max_kg=fields.Float(sting="Maximum Kilogram")
    volume=fields.Float(string="Volume")
    max_volume=fields.Float(string="Max.Volume")
    safe_volume=fields.Float(string="Safe Volume")

class RaiseProduct(models.Model):
    _inherit="product.template" 


    service_to_purchase=fields.Boolean(string="Service to Purchase")
    add_packaging=fields.Boolean(string="Add Packaging")
    height=fields.Float(string="height")
    weight=fields.Float(string="Weight in KG")
    length=fields.Float(string="Length")
    width=fields.Float(string="Width")
    hs_code=fields.Char(string="HS Code")
    
    volume=fields.Float(string="Volume",compute="_compute_volume",readonly=True)
    max_quantity=fields.Float(string="Max Quantity")
    
    field_name_ids = fields.One2many('product.packaging', 'product_id', string='Pakaging')
    manufacturer = fields.Many2one(
        'rise.manufacturer',
        string='',
        )
    
    @api.depends('weight','length','height')
    def _compute_volume(self):
        for record in self:
            record.volume=record.height*record.width*record.length
class RaiseProduckPakaging(models.Model):
    _inherit='product.packaging'
    _rec_name='description'
    name=fields.Char(string="Pakaging name")
    height=fields.Float(string="height",digits=(4, 8))
    weight=fields.Float(string="Weight in KG",digits=(4, 8))
    length=fields.Float(string="Length",digits=(4, 8))
    width=fields.Float(string="Width",digits=(4, 8))
    hs_code=fields.Char(string="HS Code")
    volume=fields.Float(string="Volume",compute="_compute_volume",readonly=True,digits=(4, 8))
    max_quantity=fields.Float(string="Max Quantity")
    description=fields.Char(string="Pakage",compute="_compute_volume")
    
    
    product_id = fields.Many2one(
        string='product',
        comodel_name='product.template',
        ondelete='restrict',
    )
    # @api.depends('volume','product_id')
    # def _compute_volume(self):
    #     for record in self:
    #         record.name=record.product_id.name+"  :"+ str(record.volume)
    
    
    @api.depends('weight','length','height')
    def _compute_volume(self):
        for record in self:
            record.volume=record.height*record.width*record.length
            record.description=str(record.name)+"  "+str(record.product_id.name)+"  :"+ str(record.volume)
            
class RaisePurchaise(models.Model):
    _inherit="purchase.order"

    container=fields.Many2one(comodel_name="raise.product.packaging")

    safe_volume=fields.Float(related='container.safe_volume',string="Safe Volume")
    max_volume=fields.Float(related='container.max_volume',string="Maximum Volume")
    remaining_volume=fields.Float(compute="_compute_total_remaining", string="Remaining Volume")
    total_volume=fields.Float(compute="_compute_total_remaining", string="Total Volume")

    country_orgin=fields.Many2one(comodel_name="res.country",string="Country of Origin	")
    country_destination=fields.Many2one(comodel_name="res.country",string="Country of Destination")
    payment_term=fields.Many2one(comodel_name="raise.payment.term",string="Payment Term")
    incoterm_id=fields.Many2one(comodel_name="raise.incoterm", string="Incoterm")
    

    @api.depends('max_volume','order_line')
    def _compute_total_remaining(self):
        for record in self:
            volume=0
            for record_order in record.order_line:
                volume+=record_order.total_volume
            record.total_volume=volume
            record.remaining_volume=record.max_volume-record.total_volume

    # add total volume from purchase.order.line+ get total volume the sumestion of all total volumes from purchase order line
    # and remaining volume by substraction fro safe volume and max volume

class RaisePurchaiseLine(models.Model):
    _inherit="purchase.order.line"

  

    volume=fields.Float(string="Volume",related='product_id.volume',)
    height=fields.Float(string="height",related='product_id.height')
    weight=fields.Float(string="Weight",related='product_id.weight')
    length=fields.Float(string="Length",related='product_id.length')
    max_quantity=fields.Float(string="Max Quantity",related='product_id.max_quantity')
    remaining_quantity=fields.Float(string="Remaining Quantity",compute="_calculate_remaning")
    total_volume=fields.Float(string="T.CBM",compute="_calculate_remaning")

    @api.depends('max_quantity','product_qty')
    def _calculate_remaning(self):
        for records in self:
            remaining_quantity=0
            volume=records.height*records.weight*records.length
            order_volume=0
            ratio_add=0
            quantity_ratio=0
            # quantity=records.volume
            quantity=records.product_qty
            max_quantity=records.max_quantity
            if max_quantity>0 :
                quantity_ratio=int(quantity/max_quantity)
                if quantity>max_quantity:

                    remaining_quantity= quantity% max_quantity#(quantity_ratio+1)*volume
                else :
                    remaining_quantity=max_quantity-quantity
                

                if remaining_quantity >0:
                    order_volume=  (quantity_ratio+1)*volume
                else:
                    order_volume=  quantity_ratio*volume

                   
            records.remaining_quantity
            records.total_volume=order_volume 


            
            # amount=



            

    #geting packaging volume and assigne callculated value in 
    #pakaging volume max quantity it can hold 
    #remaning for max packaging quantity

class RaisePaymentTerm(models.Model):
    _name="raise.payment.term"

    name=fields.Char(string="Payment Term")
    code=fields.Char(string="Payment Term Code")

class RaisePaymentTerm(models.Model):
    _name="raise.incoterm"
    name=fields.Char(string="Incoterm")
    code=fields.Char(string="Incoterm Code")  
   
class RiseManufacturer(models.Model):
    _name="rise.manufacturer"
    name=fields.Char(string="Manufacturer")
    city=fields.Char('City')
    sub_city=fields.Char(string="Sub City")
    street=fields.Char('St')
    state=fields.Char(string="State")
    phone=fields.Char('Phone')
    email=fields.Char(string="email")
    
     
class RisePort(models.Model):
    _name="rise.port"
    name=fields.Char(string="Port")
    code=fields.Char(string="Port Code")        
class RaiseSales(models.Model):
    _inherit="sale.order"



    purchase_order_count = fields.Integer( string= "Number of Purchase Order Generated",groups='purchase.group_purchase_user')




    container=fields.Many2one(comodel_name="raise.product.packaging")
    benfi_bank=fields.Many2one(comodel_name="res.bank",string="Benficiary Bank")

    safe_volume=fields.Float(related='container.safe_volume',string="Safe Volume")
    max_volume=fields.Float(related='container.max_volume',string="Maximum Volume")
    remaining_volume=fields.Float(compute="_compute_total_remaining", string="Remaining Volume")
    total_volume=fields.Float(compute="_compute_total_remaining", string="T.CBM")
    num_container=fields.Integer(string="Num. Container")
    port_discharge=fields.Many2many(comodel_name="rise.port", string="Port of Discharge/ Port of loading" )

    # mode_shipment= fields.Selection(
    #     selection=[
    #         ('Air', 'Air'),
    #         ('Sea', 'Sea')
    #     ],string="Mode of Shipment", 
    #     default='Air'
        
    # )
    mode_shipment= fields.Char(
        
            compute='_compute_mdoe_shipment' 
        
        
        ,string="Mode of Shipment", 
        
        
    )
    hs_code=fields.Char(string="HS Code")
    country_orgin=fields.Many2one(comodel_name="res.country",string="Country of Origin	")
    country_destination=fields.Many2one(comodel_name="res.country",string="Country of Destination")
    payment_term=fields.Many2one(comodel_name="raise.payment.term",string="Payment Term")
    inconterm=fields.Many2one(comodel_name="raise.incoterm", string="Incoterm")
    loding_port=fields.Many2one(comodel_name="rise.port", string="Port of Loading")
    destination_port=fields.Many2one(comodel_name="rise.port", string="Destination Port")
    # manufacturer=fields.Char(string="Manufacturer")
    manufacturer = fields.Many2one(
        'rise.manufacturer',
        string='',
        )
    lc_number=fields.Char(string="LC Number")  
    place_delivery=fields.Char(string="Port of Discharge") 
    tin_num=fields.Char(string="TIN Number")
    @api.depends('inconterm')
    def _compute_mdoe_shipment(self):
        for records in self:
            abc=records.inconterm.name
            if records.inconterm.name == "FOB":
                
                records.mode_shipment="Sea"
            else:
                records.mode_shipment="Air"    
                
    @api.depends('max_volume','order_line')
    def _compute_total_remaining(self):
        for record in self:
            volume=0
            num_container=0.000000000000000000000000000000
            remaning=0
           
            for record_order in record.order_line:
                volume+=record_order.total_volume
           
            if record.max_volume>0:
                num_container=volume/record.max_volume
                if num_container>int(num_container):
                    num_container=num_container+1
            remaning=int(num_container)*record.max_volume-volume 
            record.total_volume=volume
            record.num_container=int(num_container)
            record.remaining_volume=remaning
            
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
        }

    def _get_po(self):

        for orders in self:
            purchase_ids = self.env['purchase.order'].search([('origin', '=', self.name)])
        orders.po_count = len(purchase_ids)

    po_count = fields.Integer(compute='_get_po', string='Purchase Order')           



class RaiseSalesLine(models.Model):
    _inherit="sale.order.line"

    pakage=fields.Many2one(string="Pakage", comodel_name="product.packaging" ,)
   # domain="[('product_id.id', '=', product_template_id.id)]")
    
    weight=fields.Float(string="Weight in KG",related='pakage.volume')
    total_weight=fields.Float(string="Total Weight in KG",compute="_calculate_remaning")
    volume=fields.Float(string="Volume",related='pakage.volume',)
    box_qty=fields.Integer(string="Box Qty." ,compute="_calculate_remaning")
    width=fields.Float(string="width",related='pakage.width',digits=(4, 8))
    height=fields.Float(string="height",related='pakage.height',digits=(4, 8))
    weight=fields.Float(string="Weight",related='pakage.weight',digits=(4, 8))
    length=fields.Float(string="Length",related='pakage.length',digits=(4, 8))
    max_quantity=fields.Float(string="Max Quantity",related='pakage.max_quantity')
    remaining_quantity=fields.Float(string="Remaining Quantity",compute="_calculate_remaning")
    total_volume=fields.Float(string="T.CBM",compute="_calculate_remaning",digits=(4, 8))
    hs_code=fields.Char(string="HS Code",related='product_id.hs_code')
    product_int= fields.Integer(
        string='Product INt',compute="_int_product"
    )
    # order_id_manufacturer= fields.Many2one(related='order_id.manufacturer.name')
    
    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
        change_default=True, ondelete='restrict', check_company=True, index='btree_not_null',
        domain="[( ('manufacturer', '=', order_id.manufacturer), ('manufacturer', '=', False)), ('sale_ok', '=', True)]")
    
    manufacturer=fields.Many2one(related='product_id.manufacturer',string="Manufacturer")
    @api.depends('product_template_id')
    def _int_product(self):
        for records in self:
            records.product_int=int(records.product_template_id.id)


    @api.depends('max_quantity','product_uom_qty')
    def _calculate_remaning(self):
        for records in self:
            remaining_quantity=0
            volume=records.height*records.width*records.length
            order_volume=0
            ratio_add=0
            quantity_ratio=0
            produc_int=records.product_id
            product_te=records.product_template_id
            # quantity=records.volume
            quantity=records.product_uom_qty
            max_quantity=records.max_quantity
            weight=0
            multiplier=0
            bqty=0
            if max_quantity>0 and records.product_uom_qty>0 :
                                   
                bqty=quantity/max_quantity
                if bqty >int(bqty):
                    bqty=bqty+1
                quantity_ratio=int(quantity/max_quantity)
                remaning=quantity% max_quantity

                       
                
                if quantity>max_quantity:
                    if  quantity%max_quantity==0:
                        remaining_quantity=0
                    else:
                        remaining_quantity= max_quantity-(quantity% max_quantity)#(quantity_ratio+1)*volume
                else :
                    remaining_quantity=max_quantity-quantity
                #  correcting remaning quantity

               
                order_volume=  int(bqty)*volume
                weight=int(bqty)*records.weight
               
                   

                   
            records.remaining_quantity=remaining_quantity
            records.total_volume=order_volume 
            records.total_weight=weight

            records.box_qty=int(bqty)

# class CommercialInvoice(models.Model):
#     _name = 'account.move.commercial'
#     _description = 'Commercial Invoice'
#     _inherit = 'account.move'

#     # Additional fields for commercial invoices
#     country_origin = fields.Many2one('res.country', string='Country of Origin')
#     country_destination = fields.Many2one('res.country', string='Country of Destination')
#     # ... other fields specific to commercial invoices

#     @api.model
#     def action_export_pdf(self):
#         # Use the built-in report API to generate the PDF
#         docargs = {
#             'doc_ids': self.ids,
#             'doc_model': 'account.move.commercial',
#             'docs': self,
#         }
#         return self.env['ir.actions.report']._render_report('your_module.report_commercial_invoice', docargs)

# class InheritedAccountMOve(models.Model):
#     _inherit="account.move"
#     hs_code=fields.Char(string="HS Code")
#     country_orgin=fields.Many2one(comodel_name="res.country",string="Country of Origin	")
#     country_destination=fields.Many2one(comodel_name="res.country",string="Country of Destination")
    
    
#     loding_port=fields.Many2one(comodel_name="rise.port", string="Port of Loading")
#     destination_port=fields.Many2one(comodel_name="rise.port", string="Destination Port")
#     manufacturer=fields.Char(string="Manufacturer")

# stock.picking
# class InheritedStockPicking(models.Model):
#     _inherit="stock.picking.line"
#     ctn=fields.Integer(string="CTN",related='picking_id.sale_id.box_qty')

                
            # amount=



            

    #geting packaging volume and assigne callculated value in 
    #pakaging volume max quantity it can hold 
    #remaning for max packaging quantity
            

    # add total volume from purchase.order.line+ get total volume the sumestion of all total volumes from purchase order line
    # and remaining volume by substraction fro safe volume and max volume
    
