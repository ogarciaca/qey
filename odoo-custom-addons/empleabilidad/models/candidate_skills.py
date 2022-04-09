# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CandidateSkill(models.Model):
    _name = 'candidate.skill'
    _description = "Skill de los candidatos"
    _rec_name = 'skill_id'
    _order = "skill_level_id"

    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    skill_id = fields.Many2one('hr.skill', required=True)
    skill_level_id = fields.Many2one('hr.skill.level', string="Nivel", required=True)
    skill_type_id = fields.Many2one('hr.skill.type', required=True)
    level_progress = fields.Integer("level_progress", related='skill_level_id.level_progress')
    #related='skill_level_id.level_progress')

    _sql_constraints = [
        ('_unique_skill', 'unique (partner_id, skill_id)', "Dos niveles de habilidades no son permitidos")
        #Two levels for the same skill is not allowed"),
    ]

    @api.constrains('skill_id', 'skill_type_id')
    def _check_skill_type(self):
        for record in self:
            if record.skill_id not in record.skill_type_id.skill_ids:
                raise ValidationError(_("La habilidad %(name)s y el tipo %(type)s no concuerdan", name=record.skill_id.name, type=record.skill_type_id.name))
               #raise ValidationError(_("The skill %(name)s and skill type %(type)s doesn't match", name=record.skill_id.name, type=record.skill_type_id.name))

    @api.constrains('skill_type_id', 'skill_level_id')
    def _check_skill_level(self):
        for record in self:
            if record.skill_level_id not in record.skill_type_id.skill_level_ids:
                raise ValidationError(_("El nivel de habilidades %(level)s is not valid for skill type: %(type)s", level=record.skill_level_id.name, type=record.skill_type_id.name))
                #raise ValidationError(_("The skill level %(level)s is not valid for skill type: %(type)s", level=record.skill_level_id.name, type=record.skill_type_id.name))


