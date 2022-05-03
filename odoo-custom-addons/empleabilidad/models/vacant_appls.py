
# -*- coding: utf-8 -*-
import logging
from sre_parse import State
from datetime import datetime

from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _
from odoo.tests.common import Form

logger = logging.getLogger(__name__)


APLICATION_PRIORITIES = [
    ('1', 'Baja'),
    ('2', 'Media'),
    ('3', 'Alta')
]

class Applicant(models.Model):
    _name = "vacant.appls"
    _description = "Aplicaciones de Candidatos"
    _order = "priority desc, id desc"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']

    active = fields.Boolean("Activo", default=True, help="Si el trabajo es puesto en falso, el sistema lo esconde sin eliminarlo")
    detail = fields.Text("Detalle")
    partner_id = fields.Many2one('res.partner', "Candidato", copy=False)
    probability = fields.Float("Probability")
    vacant_ids = fields.Many2one('candidate.vacant', string='Vacante', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=True)
    refuse_reason_id = fields.Many2one('hr.applicant.refuse.reason', string='Razon de rechazo', tracking=True)
    stage_id = fields.Many2one('hr.recruitment.stage', 'Stage', ondelete='restrict', tracking=True,
                               store=True, readonly=False,
                               copy=False, index=True,
                               group_expand='_read_group_stage_ids')
    last_stage_id = fields.Many2one('hr.recruitment.stage', "Last Stage",
                                    help="Stage of the applicant before being in the current stage. Used for lost cases analysis.")
    user_id = fields.Many2one(
        'res.users', "Recruiter",
        tracking=True, store=True, readonly=False)
    create_date = fields.Datetime("Creation Date", readonly=True, index=True)
    date_closed = fields.Datetime("Closed", compute='_compute_date_closed', store=True, index=True)
    date_open = fields.Datetime("Assigned", readonly=True, index=True)
    date_last_stage_update = fields.Datetime("Last Stage Update", index=True, default=fields.Datetime.now)
    priority = fields.Selection(APLICATION_PRIORITIES, "Appreciation", default='1')
    color = fields.Integer("Color Index", default=0)
    attachment_number = fields.Integer(compute='_get_attachment_number', string="Number of Attachments")
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'vacant.appls')], string='Attachments')
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='Kanban State',
        copy=False, default='normal', required=True)
    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked')
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid')
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing')
    meeting_count = fields.Integer(compute='_compute_meeting_count', help='Meeting Count')
    application_count = fields.Integer(help='Applications with the same email')  
    refuse_reason_id = fields.Many2one('hr.applicant.refuse.reason', string='Refuse Reason', tracking=True)
    
    
    def _compute_meeting_count(self):
        if self.ids:
            meeting_data = self.env['calendar.event'].sudo().read_group(
                [('applicant_id', 'in', self.ids)],
                ['applicant_id'],
                ['applicant_id']
            )
            mapped_data = {m['applicant_id'][0]: m['applicant_id_count'] for m in meeting_data}
        else:
            mapped_data = dict()
        for applicant in self:
            applicant.meeting_count = mapped_data.get(applicant.id, 0)    

    #def _compute_application_count(self):
    #    application_data = self.env['vacant.appls'].with_context(active_test=False).read_group([
    #        ('email_from', 'in', list(set(self.mapped('email_from'))))], ['email_from'], ['email_from'])
    #    application_data_mapped = dict((data['email_from'], data['email_from_count']) for data in application_data)
    #    applicants = self.filtered(lambda applicant: applicant.email_from)
    #    for applicant in applicants:
    #        applicant.application_count = application_data_mapped.get(applicant.email_from, 1) - 1
    #    (self - applicants).application_count = False  
 
    @api.depends('stage_id')
    def _compute_date_closed(self):
        for applicant in self:
            if applicant.stage_id and applicant.stage_id.fold:
                applicant.date_closed = fields.datetime.now()
            else:
                applicant.date_closed = False

    #@api.depends('stage_id')
    #def _compute_stage(self):
    #    for applicant in self:
    #        if applicant.job_id:
    #            if not applicant.stage_id:
    #                stage_ids = self.env['hr.recruitment.stage'].search([
    #                    '|',
    #                    ('job_ids', '=', False),
    #                    ('job_ids', '=', applicant.job_id.id),
    #                    ('fold', '=', False)
    #                ], order='sequence asc', limit=1).ids
    #                applicant.stage_id = stage_ids[0] if stage_ids else False
    #        else:
    #            applicant.stage_id = False
   
    def _get_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'vacant.appls'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = dict((res['res_id'], res['res_id_count']) for res in read_group_res)
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0) 

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        # retrieve job_id from the context and write the domain: ids + contextual columns (job or default)
        #search_domain = [('id', 'in', stages.ids)] 
        search_domain = [] 
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)        


    def action_makeMeeting(self):
        """ This opens Meeting's calendar view to schedule meeting on current applicant
            @return: Dictionary value for created Meeting view
        """
        self.ensure_one()
        partners = self.partner_id | self.user_id.partner_id 

        category = self.env.ref('hr_recruitment.categ_meet_interview')
        res = self.env['ir.actions.act_window']._for_xml_id('calendar.action_calendar_event')
        res['context'] = {
            'default_applicant_id': self.id,
            'default_partner_ids': partners.ids,
            'default_user_id': self.env.uid,
            'default_name': "Nota desde el kanban de aplicaciones",
            'default_categ_ids': category and [category.id] or False,
        }
        return res        