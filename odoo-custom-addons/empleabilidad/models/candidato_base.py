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

def get_years():
    year_list = []
    fin = int(datetime.today().strftime("%Y")) + 1
    inicio = fin - 50
    for i in range(1900, fin):
        year_list.append((str(i), str(i)))
    return year_list   

#    _name = 'candidatos.base'
#    _description = 'Candidatos base'
class candidate(models.Model):

    _inherit = 'res.partner'


    cand_progress = fields.Integer('progreso',compute="_compute_cand_progress")
    salary = fields.Integer('Salario Mensual')
    gender = fields.Selection([('male', 'Male'),('female', 'Female'),('other', 'Other')], 'Gender')
    marital = fields.Selection([
                ('single', 'Single'),
                ('married', 'Married'),
                ('cohabitant', 'Legal Cohabitant'),
                ('widower', 'Widower'),
                ('divorced', 'Divorced')],
                'marital')
    birthday = fields.Date('Date of Birth')
    link_linkedin = fields.Char('link linkedin')
    link_twitter = fields.Char('link twitter')
    link_side = fields.Char('link side')
    profile = fields.Text('Profile')
    cover =  fields.Text('cover')
    partner_skill_ids = fields.One2many('candidate.skill', 'partner_id', string="Skills")
    partner_jobs_ids = fields.One2many('candidate.jobs', 'partner_id', string="jobs")
    partner_edus_ids = fields.One2many('candidate.edus', 'partner_id', string="Educations")
    partner_vacant_appls_ids = fields.One2many('vacant.appls', 'partner_id', string="Aplicaciones")

    def _compute_cand_progress(self):
            for record in self:
                record.cand_progress = 0
                if record.profile:
                    record.cand_progress = record.cand_progress + 10
                if record.cover:
                    record.cand_progress = record.cand_progress + 5 
                if record.salary > 0 :
                    record.cand_progress = record.cand_progress + 5                      
                if record.partner_skill_ids:
                    record.cand_progress = record.cand_progress + 30       
                if record.partner_edus_ids:
                    record.cand_progress = record.cand_progress + 30  
                                                                              


class candidateEstudio(models.Model):
    _name = 'candidate.estudio'
    _inherits = {'res.partner': 'partner_id'}

    _description = 'Candidate Studies'

    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    date_start = fields.Date('Start date')
    date_end = fields.Date('End date')
    institution = fields.Char('Institution')
    titulo = fields.Char('Titulo')
    degree = fields.Many2one('hr.recruitment.degree', string='Grado' )
    ended = fields.Boolean(string='Finalizado', default=True)
    start_month = fields.Selection([('01', 'Enero'), ('02', 'Febrero'), ('03', 'Marzo'), ('04', 'Abril'),
                          ('05', 'Mayo'), ('06', 'Junio'), ('07', 'Julio'), ('08', 'Agosto'), 
                          ('09', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre') ], 
                          string='InicioMes' )
    start_year = fields.Selection(get_years(), string='InicioAño')
    end_month = fields.Selection([('01', 'Enero'), ('02', 'Febrero'), ('03', 'Marzo'), ('04', 'Abril'),
                          ('05', 'Mayo'), ('06', 'Junio'), ('07', 'Julio'), ('08', 'Agosto'), 
                          ('09', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre') ], 
                          string='FinMes')
    end_year = fields.Selection(get_years(), string='FinAño')


    """
    @api.model
    # Metodo para encontrar el costo promedio. C05.13
    # la funcion "_get_average_cost" usa la funcion de odoo "read_group" el cual contiene : dominio, campos para accesar y agrupacion
    # dominio son las restricciones. en este ejemplo es que el costo "cost_price" tenga valor o no sea falso
    # campos para acceder : son los campos que traera la consulta. para este ejemplo traera la categoria "categori_id" y el promedio del costo "cost_price"
    # agrupacion : es por cual de los campos se agrupara.
    # select category_id,avg(cost_price) from library_boook group by category_id 
    #
  
    
    
    
    def _compute_dates_start(self):
        for rec in self:
            if rec.start_year == False:    # Sino contiene nada se pone 1900
                rec.start_year='1900'
            if rec.start_month == False:   # Si no contiene nada se pone 01
                rec.start_month='01'     
            rec.date_start = datetime.strptime(rec.start_year+rec.start_month+'01', '%Y%m%d')

            if rec.end_year == False:    # Sino contiene nada se pone 1900
                rec.end_year='1900'
            if rec.end_month == False:   # Si no contiene nada se pone 01
                rec.start_month='01'     
            rec.date_end = datetime.strptime(rec.end_year+rec.end_month+'01', '%Y%m%d')

    """
    @api.constrains('date_end')
    def _check_release_date(self):
        for rec in self:
            if rec.ended == True:
                if rec.date_start != False and rec.date_end != False and rec.date_start > rec.date_end:
                    raise models.ValidationError(
                        'Fechas no corresponden')
            else:
                if rec.date_start == False:
                    raise models.ValidationError('Fecha inicio nula')



