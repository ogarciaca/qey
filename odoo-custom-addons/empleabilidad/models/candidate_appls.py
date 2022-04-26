
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from random import randint

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError

class Job(models.Model):
    _name = "company.jobs"
    #_inherit = ["mail.alias.mixin", "hr.job"]
    _inherit = [ "hr.job"]
    _order = "state desc, name asc"

    @api.model
    def _default_address_id(self):
        return self.env.company.partner_id

    def _get_default_appls_favorite_user_ids(self):
        return [(6, 0, [self.env.uid])]    

    address_id = fields.Many2one(
        'res.partner', "Lugar del trabajo", default=_default_address_id,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Lugar donde se trabajará")
        

    application_count = fields.Integer(compute='_compute_application_count', string="Application Count")
    all_application_count = fields.Integer(compute='_compute_all_application_count', string="All Application Count")
    new_application_count = fields.Integer(
        compute='_compute_new_application_count', string="New Application",
        help="Number of applications that are new in the flow (typically at first step of the flow)")
    manager_id = fields.Many2one('hr.employee') 
    #related='department_id.manager_id', string="Department Manager",  readonly=True, store=True)
    user_id = fields.Many2one('res.users', "Recruiter", tracking=True)
    hr_responsible_id = fields.Many2one(
        'res.users', "HR Responsible", tracking=True,
        help="Person responsible of validating the employee's contracts.")
    document_ids = fields.One2many('ir.attachment', compute='_compute_document_ids', string="Documents")
    documents_count = fields.Integer(compute='_compute_document_ids', string="Document Count")
    alias_id = fields.Many2one(
        'mail.alias', "Alias email", 
        help="Email alias for this job position. New emails will automatically create new applicants for this job position.")
    color = fields.Integer("Color Index")
    is_favorite = fields.Boolean(compute='_compute_is_favorite', inverse='_inverse_is_favorite')
    favorite_user_ids = fields.Many2many('res.users', 'appls_favorite_user_rel', 'job_id', 'user_id', default=_get_default_appls_favorite_user_ids)

    #Sapplication_ids = fields.One2many('candidate.appls', 'job_id', "Aplicaciones")

    def _compute_all_application_count(self):
        read_group_result = self.env['account.appls'].with_context(active_test=False).read_group([('job_id', 'in', self.ids)], ['job_id'], ['job_id'])
        result = dict((data['job_id'][0], data['job_id_count']) for data in read_group_result)
        for job in self:
            job.all_application_count = result.get(job.id, 0)

    def _compute_document_ids(self):
        applicants = self.mapped('application_ids').filtered(lambda self: not self.emp_id)
        app_to_job = dict((applicant.id, applicant.job_id.id) for applicant in applicants)
        attachments = self.env['ir.attachment'].search([
            '|',
            '&', ('res_model', '=', 'hr.job'), ('res_id', 'in', self.ids),
            '&', ('res_model', '=', 'candidate.appls'), ('res_id', 'in', applicants.ids)])
        result = dict.fromkeys(self.ids, self.env['ir.attachment'])
        for attachment in attachments:
            if attachment.res_model == 'candidate.appls':
                result[app_to_job[attachment.res_id]] |= attachment
            else:
                result[attachment.res_id] |= attachment    

    def _compute_is_favorite(self):
        for job in self:
            job.is_favorite = self.env.user in job.favorite_user_ids 

    def _compute_application_count(self):
        read_group_result = self.env['candidate.appls'].read_group([('job_id', 'in', self.ids)], ['job_id'], ['job_id'])
        result = dict((data['job_id'][0], data['job_id_count']) for data in read_group_result)
        for job in self:
            job.application_count = result.get(job.id, 0)

    def _compute_all_application_count(self):
        read_group_result = self.env['candidate.appls'].with_context(active_test=False).read_group([('job_id', 'in', self.ids)], ['job_id'], ['job_id'])
        result = dict((data['job_id'][0], data['job_id_count']) for data in read_group_result)
        for job in self:
            job.all_application_count = result.get(job.id, 0)  

    def _compute_new_application_count(self):
        for job in self:
            job.new_application_count = self.env["candidate.appls"].search_count(
                [("job_id", "=", job.id), ("stage_id", "=", job._get_first_stage().id)]
            ) 

