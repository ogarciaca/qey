# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from email.policy import default
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CandidateJobs(models.Model):
    _name = 'candidate.jobs'
    _description = "Experiencias de los candidatos"
    _order = "date_start desc"

    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')

    job_title = fields.Char("Cargo", required=True)
    name = fields.Char("Nombre de la Compañia")
    date_start = fields.Date("Fecha inicio", required=True)
    date_end = fields.Date("Fecha retiro")
    functions = fields.Text(string="Funciones")
    Achievements = fields.Text(string="Logros")
    line_type_id = fields.Integer("line_type_id", default=1)
    description = fields.Text(string="Descripcion")
    display_type = fields.Selection([('classic', 'Classic')], string="Display Type", default='classic')

    _sql_constraints = [
        ('date_check', "CHECK ((date_start <= date_end OR date_end = NULL))", "La fecha de inicio debe ser anterior a la de retiro"),
    ]

