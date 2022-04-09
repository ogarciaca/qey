
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from random import randint

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError

AVAILABLE_PRIORITIES = [
    ('0', 'Normal'),
    ('1', 'Bueno'),
    ('2', 'Muy Bueno'),
    ('3', 'Excelente')
]



class Applicant(models.Model):
    _name = "candidate.appls"
    _description = "Oportunidades"
    _order = "priority desc, id desc"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']

    # Nombre del asunto u oportunidad/vacante
    name = fields.Char("Asunto / Nombre de la oportunidad", required=True, 
                        help="Asunto del correo electrónico para las solicitudes enviadas por correo electrónico")
    # Estado de la vacante
    active = fields.Boolean("Activo", default=True, help="Si el campo se pone en false/desactivado, este se ocultará sin borrarlo")
    # Descripcion de la solicitud
    description = fields.Text("Descripcion")
    # Email del que registra la solicitud.
    # en caso de que el correo lo tenga un contacto (res.partner) se llenará automaticamente telefonos del solicitante
    # esto debido al compute.
    email_from = fields.Char("Email", size=128, help="email del solicitante", compute='_compute_partner_phone_email',
        inverse='_inverse_partner_email', store=True)
    # Valor de la probabilidad de ocupar la solicitud.    
    probability = fields.Float("Probabilidad")
    # Contacto que crea la solicitud.
    partner_id = fields.Many2one('res.partner', "Contacto", copy=False)
    # Fecha de creación de la solicitud
    create_date = fields.Datetime("Creation Date", readonly=True, index=True)
    # Etapa de avance en el reclutamiento de ls solicitud
    stage_id = fields.Many2one('hr.recruitment.stage', 'Nivel', ondelete='restrict', tracking=True,
                               compute='_compute_stage', store=True, readonly=False,
                               domain="['|', ('job_ids', '=', False), ('job_ids', '=', job_id)]",
                               copy=False, index=True,
                               group_expand='_read_group_stage_ids')
    # Etapa anterior en el reclutamiento de la solicitud
    last_stage_id = fields.Many2one('hr.recruitment.stage', "Etapa Anterior",
                                    help="Etapa anterior antes de ir a la nueva. Usada para el analisis de los casos perdidos.")
    # Categoria... ?? poner relacion con las categorias de res.partner
    categ_ids = fields.Many2many('candidate.appls.category', string="Tags")
    # compañia de la solicitud..?? cambiar por res.partner
    company_id = fields.Many2one('res.company', "Empresa", compute='_compute_company', store=True, readonly=False, tracking=True)
    # Usuario que registra la solicitudd
    user_id = fields.Many2one(
        'res.users', "Solicitante", compute='_compute_user',
        tracking=True, store=True, readonly=False)
    # Fecha de cierre
    date_closed = fields.Datetime("Cierre", compute='_compute_date_closed', store=True, index=True)
    # Fecha de apertura
    date_open = fields.Datetime("Fecha Solicitud", readonly=True, index=True)
    # Ultima fecha de cambio de etapa
    date_last_stage_update = fields.Datetime("Fecha de cambio de etapa", index=True, default=fields.Datetime.now)
    # Prioridad
    priority = fields.Selection(AVAILABLE_PRIORITIES, "Apreciacion", default='0')
    # Id del nombre del cargo. ?? No se si cambiaro por otra tabla de jobs
    job_id = fields.Many2one('hr.job', "Applied Job", domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=True)
    # Salario propuesto extra y esperado. Salario propuesto y esperado
    salary_proposed_extra = fields.Char("Extra salario ofrecido", help="Salario extra propuesto por la organizacion, adicional", tracking=True)
    salary_expected_extra = fields.Char("Extra salario propuesto", help="Salario extra esperado de los candidatos, adicional", tracking=True)
    salary_proposed = fields.Float("Salario propuesto", group_operator="avg", help="Salario propuesto por el solicitante", tracking=True)
    salary_expected = fields.Float("Salario esperado", group_operator="avg", help="Salario esperado de los candidatos", tracking=True)
    # fecha en que se habilita la solicitud.
    availability = fields.Date("Disponible", help="Fecha en la que inicia esta solicitud", tracking=True)
    # Nombre del solicitante. Se llena automaticamente por el compute
    partner_name = fields.Char("Nombre del solicitante")
    # Telefonos del solicitante. Se llena automaticamente por el compute
    partner_phone = fields.Char("Telefono", size=32, compute='_compute_partner_phone_email',
        inverse='_inverse_partner_phone', store=True)
    partner_mobile = fields.Char("Cel", size=32, compute='_compute_partner_phone_email',
        inverse='_inverse_partner_mobile', store=True)
    # Nivel de educación de la solicitud
    type_id = fields.Many2one('hr.recruitment.degree', "Nivel Educacion")
    # Departamento de la solicitud.. ?? cambiar
    department_id = fields.Many2one(
        'hr.department', "Department", compute='_compute_department', store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=True)
    # Numero de dias en que estará abierta la solicitud. calcula las fechas de apertura y cierre compute
    day_open = fields.Float(compute='_compute_day', string="Dias abierta", compute_sudo=True)
    day_close = fields.Float(compute='_compute_day', string="Dias de cierre", compute_sudo=True)
    delay_close = fields.Float(compute="_compute_day", string='Dias de demora', readonly=True, group_operator="avg", help="Numero de dias para el cierre", store=True)
    color = fields.Integer("Color Index", default=0)
    # Empleado relacionado con la solicitud
    emp_id = fields.Many2one('hr.employee', string="Employee", help="Empleado relacionado con la solicitud", copy=False)
    user_email = fields.Char(related='user_id.email', string="User Email", readonly=True)
    # Numero de adjuntos. camculado por el compute
    attachment_number = fields.Integer(compute='_get_attachment_number', string="Numero de adjuntos")
    # Empleado relacionado con la solicitud
    employee_name = fields.Char(related='emp_id.name', string="Nombre empleado", readonly=False, tracking=False)
    # Id relacionado con ls solicitud
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'hr.applicant')], string='Attachments')
    # Estado del camban con su respectivo color
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='Estado Kanban',
        copy=False, default='normal', required=True)
    #legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked')
    legend_blocked = fields.Char('Kanban Blocked')
    #legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid')
    legend_done = fields.Char('Kanban Valid')
    #legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing')
    legend_normal = fields.Char('Kanban Ongoing')
    # Conteo de las aplicaciones. calculado por el compute
    application_count = fields.Integer(compute='_compute_application_count', help='Aplicaciones con el mismo correo')
    meeting_count = fields.Integer(compute='_compute_meeting_count', help='Conteo de reuniones')
    refuse_reason_id = fields.Many2one('candidate.appls.refuse.reason', string='Razones Rechazos', tracking=True)


    
    @api.depends('partner_id')
    def _compute_partner_phone_email(self):
        for applicant in self:
            applicant.partner_phone = applicant.partner_id.phone
            applicant.partner_mobile = applicant.partner_id.mobile
            applicant.email_from = applicant.partner_id.email

    def _inverse_partner_email(self):
        for applicant in self.filtered(lambda a: a.partner_id and a.email_from and not a.partner_id.email):
            applicant.partner_id.email = applicant.email_from 

    @api.depends('job_id')
    def _compute_stage(self):
        for applicant in self:
            if applicant.job_id:
                if not applicant.stage_id:
                    stage_ids = self.env['hr.recruitment.stage'].search([
                        '|',
                        ('job_ids', '=', False),
                        ('job_ids', '=', applicant.job_id.id),
                        ('fold', '=', False)
                    ], order='sequence asc', limit=1).ids
                    applicant.stage_id = stage_ids[0] if stage_ids else False
            else:
                applicant.stage_id = False

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        # retrieve job_id from the context and write the domain: ids + contextual columns (job or default)
        job_id = self._context.get('default_job_id')
        search_domain = [('job_ids', '=', False)]
        if job_id:
            search_domain = ['|', ('job_ids', '=', job_id)] + search_domain
        if stages:
            search_domain = ['|', ('id', 'in', stages.ids)] + search_domain    

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
                applicant.delay_close = False            

    def _get_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'hr.applicant'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = dict((res['res_id'], res['res_id_count']) for res in read_group_res)
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0) 


    @api.depends('email_from')
    def _compute_application_count(self):
        application_data = self.env['hr.applicant'].with_context(active_test=False).read_group([
            ('email_from', 'in', list(set(self.mapped('email_from'))))], ['email_from'], ['email_from'])
        application_data_mapped = dict((data['email_from'], data['email_from_count']) for data in application_data)
        applicants = self.filtered(lambda applicant: applicant.email_from)
        for applicant in applicants:
            applicant.application_count = application_data_mapped.get(applicant.email_from, 1) - 1
        (self - applicants).application_count = False


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

    @api.depends('job_id', 'department_id')
    def _compute_company(self):
        for applicant in self:
            company_id = False
            if applicant.department_id:
                company_id = applicant.department_id.company_id.id
            if not company_id and applicant.job_id:
                company_id = applicant.job_id.company_id.id
            applicant.company_id = company_id or self.env.company.id          