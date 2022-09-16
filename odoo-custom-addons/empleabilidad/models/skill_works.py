# -*- coding: utf-8 -*-
import logging
from sre_parse import State
from datetime import datetime

from odoo import api, fields, models
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _
from odoo.tests.common import Form
from odoo import  tools

logger = logging.getLogger(__name__)


class skills_view(models.Model):
    _name = "candidate.skills.view"
    _description = "skill view model"
    _auto = False

    #id = fields.Many2one('hr.skill', string='id')
    type_id = fields.Many2one('hr_skill_type', string='type_id', readonly=True)
    name_type = fields.Many2one('hr_skill_type', string='name_type', readonly=True)
    skill_id = fields.Many2one('hr.skill', string='skill_id', readonly=True)
    name_skill = fields.Many2one('hr.skill', string='name_skill', readonly=True)
    level_id = fields.Many2one('hr.skill.type', string='level_id', readonly=True)
    name_level = fields.Many2one('hr.skill.type', string='name_level', readonly=True)
    level_progress = fields.Many2one('hr.skill.type', string='level_progress', readonly=True)

    def init(self):
        # tools.drop_view_if_exists(self._cr, 'candidate_skill_view')
        tools.drop_view_if_exists(self.env.cr, self._table)

        self._cr.execute(""" CREATE VIEW candidate_skills_view AS (
                    select 
                    row_number() over () as id,
                    t.id as type_id, 
                    t.name as name_type,
                    s.id as skill_id, 
                    s.name as name_skill,
                    l.id as level_id, 
                    l.name as name_level,
                    l.level_progress as level_progress
                    from hr_skill_type t
                    left join hr_skill s on s.skill_type_id = t.id
                    left join hr_skill_level l on l.skill_type_id = t.id
        )""")