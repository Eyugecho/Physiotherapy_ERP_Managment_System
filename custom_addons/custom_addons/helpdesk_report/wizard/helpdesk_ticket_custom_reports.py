from odoo import models, api, fields, exceptions

class HelpdeskTicketCustomReportWizard(models.TransientModel):
    _name = 'helpdesk.ticket.wizard.report'
    _description = 'Custom Helpdesk Ticket Wizard Report'
    
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    user_template_id = fields.Many2one('res.users', string="User")

    def helpdesk_ticket_by_employee(self):
        result = []
        domain = []
        
        if self.date_from:
            domain.append(('create_date', '>=', self.date_from))
            
        if self.date_to:
            domain.append(('create_date', '<=', self.date_to))
        
        if self.user_template_id:
            domain.append(('user_id', '=', self.user_template_id.id))
        
        try:
            users = self.env['helpdesk.ticket'].search(domain).mapped('user_id')
            
            for user in users:
                total_tickets = self.env['helpdesk.ticket'].search_count(domain + [('user_id', '=', user.id)])
                open_tickets = self.env['helpdesk.ticket'].search_count(domain + [('user_id', '=', user.id), ('stage_id.name', '=', "New")])
                bad_tickets = self.env['helpdesk.ticket'].search_count(domain + [('user_id', '=', user.id), ('rating_last_text', '=', 'ko')])
                good_tickets = self.env['helpdesk.ticket'].search_count(domain + [('user_id', '=', user.id), ('rating_last_text', '=', 'ok')])
                satisfied_tickets = self.env['helpdesk.ticket'].search_count(domain + [('user_id', '=', user.id), ('rating_last_text', '=', 'top')])
                not_rated = self.env['helpdesk.ticket'].search_count(domain + [('user_id', '=', user.id), ('rating_last_text', '=', 'none')])
                closed_tickets = self.env['helpdesk.ticket'].search_count(domain + [('user_id', '=', user.id), ('stage_id.name', 'in', ["Done", "Solved"])])
                
               
                
                result.append({
                    'user': user.name,
                    'total_tickets': total_tickets,
                    'total_open_tickets': open_tickets,
                    'total_closed_tickets': closed_tickets,
                    'total_good_tickets': good_tickets,
                    'total_bad_tickets': bad_tickets,
                    'total_satisfied_tickets': satisfied_tickets,
                    'total_not_rated_tickets': not_rated,
                })
        except exceptions.UserError as e:
            # Log the error for debugging purposes
            self.env['ir.logging'].create({
                'name': 'Error in helpdesk_ticket_by_employee',
                'type': 'error',
                'message': str(e),
            })
            # Return an empty list or a default response to prevent a 204 error
            return []

        return result

    def generate_helpdesk_ticket_report(self):
        return self.env.ref('helpdesk_report.helpdesk_ticket_report_report').report_action(self)
