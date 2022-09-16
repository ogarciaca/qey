# -*- coding: utf-8 -*-
import logging
from sre_parse import State
from datetime import datetime

from odoo import api, fields, models
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _
from odoo.tests.common import Form

logger = logging.getLogger(__name__)

AVAILABLE_PRIORITIES = [
    ('1', 'Baja'),
    ('2', 'Media'),
    ('3', 'Alta')
]


# es la copia de hr_recruitment
class Works(models.Model):
    _name = "candidate.vacant"
    _description = "Aplicaciones"
    _order = "priority desc, id desc"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char("Asunto / Nombre de la Vacante", required=True, help="Asunto en el email para el trabajo")
    active = fields.Boolean("Activo", default=True, 
            help="Si el trabajo es puesto en falso, el sistema lo esconde sin eliminarlo")
    description = fields.Text("Descripcion")
    email_from = fields.Char("Email", size=128, help="Email del contacto en la empresa", compute='_compute_partner_phone_email',
            inverse='_inverse_partner_email', store=True)    
    probability = fields.Float("Probabilidad")
    partner_id = fields.Many2one('res.partner', "Contacto", copy=False)
    create_date = fields.Datetime("Fecha de Creacion", readonly=True, index=True)
    # Revisar el stage_id y last_stage
    stage_id = fields.Many2one('hr.recruitment.stage', 'Stage', ondelete='restrict', tracking=True,
                               compute='_compute_stage', store=True, readonly=False,
                               domain="['|', ('job_ids', '=', False), ('job_ids', '=', job_id)]",
                               copy=False, index=True,
                               group_expand='_read_group_stage_ids')
    last_stage_id = fields.Many2one('hr.recruitment.stage', "Last Stage",
                                    help="Stage of the applicant before being in the current stage. Used for lost cases analysis.")
    categ_ids = fields.Many2many('res.partner.category', string="Categorias")
    company_id = fields.Many2one('res.company', "Company", compute='_compute_company', store=True, readonly=False, tracking=True)
    user_id = fields.Many2one('res.users', "Recruiter", compute='_compute_user',
        tracking=True, store=True, readonly=False)
    date_open = fields.Datetime("Asignado")
    date_closed = fields.Datetime("Abierto", compute='_compute_date_closed', store=True, index=True)
    date_last_stage_update = fields.Datetime("Last Stage Update", index=True, default=fields.Datetime.now)
    priority = fields.Selection(AVAILABLE_PRIORITIES, "Appreciation", default='0')
    # Revisar los trabajos
    job_id = fields.Many2one('hr.job', "Applied Job", domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=True)
    salary_proposed_extra = fields.Char("Propuesta de salario Extra", help="Salary Proposed by the Organisation, extra advantages", tracking=True)
    salary_expected_extra = fields.Char("Salario esperado Extra", help="Salary Expected by Applicant, extra advantages", tracking=True)
    salary_proposed = fields.Float("Propuesta de salario", group_operator="avg", help="Salary Proposed by the Organisation", tracking=True)
    salary_expected = fields.Float("Salario esperado", group_operator="avg", help="Salary Expected by Applicant", tracking=True)
    availability = fields.Date("Disponibilidad de la vancate", help="The date at which the applicant will be available to start working", tracking=True) 
    partner_name = fields.Char("Applicant's Name")
    partner_phone = fields.Char("Phone", size=32, compute='_compute_partner_phone_email',
        inverse='_inverse_partner_phone', store=True)
    partner_mobile = fields.Char("Mobile", size=32, compute='_compute_partner_phone_email',
        inverse='_inverse_partner_mobile', store=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    # Revisar el titulo universitario
    type_id = fields.Many2one('hr.recruitment.degree', "Nivel Académico")
    # Revisar el departamento de la vacante
    department_id = fields.Many2one(
        'hr.department', "Department", compute='_compute_department', store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=True)
    day_open = fields.Float(compute='_compute_day', string="Days to Open", compute_sudo=True)
    day_close = fields.Float(compute='_compute_day', string="Days to Close", compute_sudo=True)
    delay_close = fields.Float(compute="_compute_day", string='Delay to Close', readonly=True, group_operator="avg", help="Number of days to close", store=True)
    color = fields.Integer("Color Index", default=0)
   # Enlace con los candidatos
    emp_id = fields.Many2one('res.partner', string="Candidatos", help="Candidatos enlazados con la vacante", copy=False)
    user_email = fields.Char(related='user_id.email', string="User Email", readonly=True)   
    attachment_number = fields.Integer(compute='_get_attachment_number', string="Numero de anexos")
    website_published = fields.Boolean("PublicadoEnWeb", default=True)
    # Revisar el employee_name
    employee_name = fields.Char(related='emp_id.name', string="Employee Name", readonly=False, tracking=False)    
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'candidate.vacant')], string='Attachments')
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='Kanban State',
        copy=False, default='normal', required=True)
    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked')
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid')
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing')
    application_count = fields.Integer(compute='_compute_application_count', help='Applications with the same email')
    meeting_count = fields.Integer(compute='_compute_meeting_count', help='Meeting Count')   
    refuse_reason_id = fields.Many2one('hr.applicant.refuse.reason', string='Refuse Reason', tracking=True)
    vacant_skill_ids = fields.One2many('candidate.vacant.skill', 'vacant_id', string="Skills")
    vacant_appls_ids = fields.One2many('vacant.appls', 'vacant_ids', string="Educations")
 
    @api.depends('partner_id')
    def _compute_partner_phone_email(self):
        for applicant in self:
            applicant.partner_phone = applicant.partner_id.phone
            applicant.partner_mobile = applicant.partner_id.mobile
            applicant.email_from = applicant.partner_id.email

    def _inverse_partner_email(self):
        for applicant in self.filtered(lambda a: a.partner_id and a.email_from and not a.partner_id.email):
            applicant.partner_id.email = applicant.email_from

    def _inverse_partner_phone(self):
        for applicant in self.filtered(lambda a: a.partner_id and a.partner_phone and not a.partner_id.phone):
            applicant.partner_id.phone = applicant.partner_phone

    def _inverse_partner_mobile(self):
        for applicant in self.filtered(lambda a: a.partner_id and a.partner_mobile and not a.partner_id.mobile):
            applicant.partner_id.mobile = applicant.partner_mobile 

    @api.depends('job_id', 'department_id')
    def _compute_company(self):
        for applicant in self:
            company_id = False
            if applicant.department_id:
                company_id = applicant.department_id.company_id.id
            if not company_id and applicant.job_id:
                company_id = applicant.job_id.company_id.id
            applicant.company_id = company_id or self.env.company.id                       

    @api.depends('stage_id')
    def _compute_date_closed(self):
        for applicant in self:
            if applicant.stage_id and applicant.stage_id.fold:
                applicant.date_closed = fields.datetime.now()
            else:
                applicant.date_closed = False

    @api.depends('job_id')
    def _compute_user(self):
        for applicant in self:
            applicant.user_id = applicant.job_id.user_id.id or self.env.uid     


    @api.depends('date_open', 'date_closed')
    def _compute_day(self):
        for applicant in self:
            if applicant.date_open:
                date_create = applicant.create_date
                date_open = applicant.date_open
                applicant.day_open = (date_open - date_create).total_seconds() / (24.0 * 3600)
            else:
                applicant.day_open = False
            if applicant.date_closed:
                date_create = applicant.create_date
                date_closed = applicant.date_closed
                applicant.day_close = (date_closed - date_create).total_seconds() / (24.0 * 3600)
                applicant.delay_close = applicant.day_close - applicant.day_open
            else:
                applicant.day_close = False

    def _get_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'candidate.vacant'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = dict((res['res_id'], res['res_id_count']) for res in read_group_res)
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0)

    def _compute_application_count(self):
        #appl_count = len(self.env['vacant.appls'].search([('vacant_ids','=',4),('active','=','True')]))
        #
        for r in self:
            r.application_count = len(r.vacant_appls_ids)
        
 
    @api.model
    def _delete_tags_from_candidate(self, vac_id, cat_id):

        if (not vac_id ) and (not cat_id):
            # Nothing to do, then!
            return
                
        self.env.cr.execute("""
            delete from candidate_vacant_res_partner_category_rel
            where candidate_vacant_id = """ + str(vac_id) + """ and res_partner_category_id = """ + str(cat_id))

    def _insert_tags_to_candidate(self, vac_id, cat_id):

        if (not vac_id ) and (not cat_id):
            # Nothing to do, then!
            return
                
        self.env.cr.execute("""
            insert into candidate_vacant_res_partner_category_rel (candidate_vacant_id, res_partner_category_id) 
            values ( """ + "'" + str(vac_id) + "'" , "'" + str(cat_id) +"'" )


    """
        def _compute_application_count(self):
            application_data = self.env['candidate.vacant'].with_context(active_test=False).read_group([
                ('email_from', 'in', list(set(self.mapped('email_from'))))], ['email_from'], ['email_from'])
            application_data_mapped = dict((data['email_from'], data['email_from_count']) for data in application_data)
            applicants = self.filtered(lambda applicant: applicant.email_from)
            for applicant in applicants:
                applicant.application_count = application_data_mapped.get(applicant.email_from, 1) - 1
            (self - applicants).application_count = False   
    """        
        

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