from odoo import _, api, fields, models
class maintenance_equipment_inherit(models.Model):
    _inherit = "maintenance.equipment"
    memory=fields.Integer(string="Memory")
    storage=fields.Integer(string="HDD")
    ssd=fields.Integer(string="SSD")
    storage_type=fields.Selection([('HDD', 'HDD'), ('SSD', 'SSD'), ('both', 'both')],string="Storage Type")
    processor=fields.Char(string="Proccessor")
    port=fields.Integer(string="Port Number")
    speed=fields.Integer(string="Speed")
    phone_number=fields.Char(string="Phone Number")
    ime=fields.Char(string="IMEI")
    qulity=fields.Integer(string="Quality")
    type=fields.Char(string="Type")
    equipment_type = fields.Selection(related='category_id.equipment_type',copy=True,store=True,readonly=True)
    stock=fields.Boolean(string="On Stock")
    com=fields.Char(compute="_compuiting_field")
    
    
    company=fields.Many2one(comodel_name="droga.equipment.companny",string="Company & Bussines unit")
    @api.onchange
    def _compuiting_field(self):
        for record in self:
            record.com=record.storage_type
class droga_equipment_companny(models.Model):
    _name = "droga.equipment.companny"
    name=fields.Char(string="Company")
class maintenance_equipment_category_inherit(models.Model):
    _inherit = "maintenance.equipment.category"
    cost=fields.Float(string="Cost",compute="_compute_total_coast" )
    equipment_type=fields.Selection([('Computer', 'Computer'), ('Phone', 'Phone'), ('SwithRouter', 'Swith&Router')
                                       ,('Camera', 'Camera') ,('Sim', 'Sim'),('HardDisk' , 'HardDisk'), ('Other', 'Other')],string="Equipment type",)
    #coast is the total sum of coasts in that categoy

    def _compute_total_coast(self):
        for record in self:
            tcoast=0.00000000
            for cost in record.equipment_ids:
                tcoast+=cost.cost
            record.cost=tcoast


    

