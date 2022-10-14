# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
from errno import EMEDIUMTYPE
import functools
import json
import logging
import math
import re
import unicodedata
import base64
from base64 import b64decode, b64encode
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


from werkzeug import urls

from odoo import fields as odoo_fields, http, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError, AccessDenied
from odoo.http import content_disposition, Controller, request, route
from odoo.tools import consteq

# --------------------------------------------------
# Misc tools
# --------------------------------------------------

_logger = logging.getLogger(__name__)

def pager(url, total, page=1, step=30, scope=5, url_args=None):
    """ Generate a dict with required value to render `website.pager` template. This method compute
        url, page range to display, ... in the pager.
        :param url : base url of the page link
        :param total : number total of item to be splitted into pages
        :param page : current page
        :param step : item per page
        :param scope : number of page to display on pager
        :param url_args : additionnal parameters to add as query params to page url
        :type url_args : dict
        :returns dict
    """
    # Compute Pager
    page_count = int(math.ceil(float(total) / step))

    page = max(1, min(int(page if str(page).isdigit() else 1), page_count))
    scope -= 1

    pmin = max(page - int(math.floor(scope/2)), 1)
    pmax = min(pmin + scope, page_count)

    if pmax - pmin < scope:
        pmin = pmax - scope if pmax - scope > 0 else 1

    def get_url(page):
        _url = "%s/page/%s" % (url, page) if page > 1 else url
        if url_args:
            _url = "%s?%s" % (_url, urls.url_encode(url_args))
        return _url

    return {
        "page_count": page_count,
        "offset": (page - 1) * step,
        "page": {
            'url': get_url(page),
            'num': page
        },
        "page_first": {
            'url': get_url(1),
            'num': 1
        },
        "page_start": {
            'url': get_url(pmin),
            'num': pmin
        },
        "page_previous": {
            'url': get_url(max(pmin, page - 1)),
            'num': max(pmin, page - 1)
        },
        "page_next": {
            'url': get_url(min(pmax, page + 1)),
            'num': min(pmax, page + 1)
        },
        "page_end": {
            'url': get_url(pmax),
            'num': pmax
        },
        "page_last": {
            'url': get_url(page_count),
            'num': page_count
        },
        "pages": [
            {'url': get_url(page_num), 'num': page_num} for page_num in range(pmin, pmax+1)
        ]
    }

def  _SkillSearch (js,search_term): 
    for i in js:
        if int(i["skill_id"]) == search_term:
            return i
    return False

def _SkillWrite(pjs,v_id):
    s = request.env['candidate.vacant.skill'].sudo().search([('vacant_id','=',v_id)])
    # Eliminar los que no vienen en el json pjs
    if s.id:
        for i in s:
            val = _SkillSearch(pjs,i.skill_id.id)
            if not val:
                # print("Update",val)
            #else:
                qry ="DELETE FROM candidate_vacant_skill WHERE ID = " + str(i.id)
                request.cr.execute(qry)
                print("Delete",i.id)

    for i in pjs:
        val = request.env['candidate.vacant.skill'].sudo().search([('vacant_id','=',v_id),('skill_id','=',int(i["skill_id"]))])
        if val.id:
            qry ="UPDATE candidate_vacant_skill SET skill_level_id=" + i["skill_level_id"] + " WHERE ID = " + str(val.id)
            print("update",val.id,i)
        else:
            qry ="INSERT INTO candidate_vacant_skill (vacant_id,skill_id,skill_level_id,skill_type_id) \
                    VALUES (" + str(v_id) + "," + i["skill_id"] + "," + i["skill_level_id"] +  "," + i["skill_type_id"]  + ")"
            print("Insert ", v_id,i)
        request.cr.execute(qry)
      

def _SkillWriteHV(pjs,p_id):
    s = request.env['candidate.skill'].sudo().search([('partner_id','=',p_id)])
    # Eliminar los que no vienen en el json pjs
    if s.id:
        for i in s:
            val = _SkillSearch(pjs,i.skill_id.id)
            if not val:
                # print("Update",val)
            #else:
                qry ="DELETE FROM candidate_skill WHERE ID = " + str(i.id)
                request.cr.execute(qry)
                print("Delete",i.id)

    for i in pjs:
        val = request.env['candidate.skill'].sudo().search([('partner_id','=',p_id),('skill_id','=',int(i["skill_id"]))])
        if val.id:
            qry ="UPDATE candidate_skill SET skill_level_id=" + i["skill_level_id"] + " WHERE ID = " + str(val.id)
            print("update",val.id,i)
        else:
            qry ="INSERT INTO candidate_skill (partner_id,skill_id,skill_level_id,skill_type_id) \
                    VALUES (" + str(p_id) + "," + i["skill_id"] + "," + i["skill_level_id"] +  "," + i["skill_type_id"]  + ")"
            print("Insert ", p_id,i)
        request.cr.execute(qry)

def  _ESTSearch (js,search_term): 
    for i in js:
        if int(i["popupest_edu_id"]) == search_term:
            return i
    return False

def _ESTWriteHV(pjs,p_id):
    s = request.env['candidate.edus'].sudo().search([('partner_id','=',p_id)])
    # Eliminar los que no vienen en el json pjs
    if s.id:
        for i in s:
            val = _ESTSearch(pjs,i.id)
            if not val:
                qry ="DELETE FROM candidate_edus WHERE ID = " + str(i.id)
                request.cr.execute(qry)
                print("Delete",i.id)

    for i in pjs:
        val = request.env['candidate.edus'].sudo().search([('partner_id','=',p_id),('id','=',int(i["popupest_edu_id"]))])
        if val.id:
            qry ="UPDATE candidate_edus SET edu_title='" + i["popupest_edu_title"] + "', name = '" +  i["popupest_name"] + "', date_start = '" +   i["popupest_date_start"]  + "', date_end = '" +   i["popupest_date_end"] + "', display_type = '" +   i["popupest_edu_type"] + "' WHERE ID = " + str(val.id)
            print("update",val.id,i)
        else:
            qry ="INSERT INTO candidate_edus (partner_id,edu_title, name, date_start, date_end, display_type) \
                    VALUES (" + str(p_id) + ",'" + i["popupest_edu_title"] + "','" + i["popupest_name"] + "','" + i["popupest_date_start"] + "','" + i["popupest_date_end"] + "','" + i["popupest_edu_type"] + "')"
            print("Insert ", p_id,i)
        request.cr.execute(qry)        

def  _EXPearch(js,search_term): 
    for i in js:
        if int(i["popupexp_job_id"]) == search_term:
            return i
    return False

def _EXPWriteHV(pjs,p_id):
    s = request.env['candidate.jobs'].sudo().search([('partner_id','=',p_id)])
    # Eliminar los que no vienen en el json pjs
    if s.id:
        for i in s:
            val = _EXPearch(pjs,i.id)
            if not val:
                qry ="DELETE FROM candidate_jobs WHERE ID = " + str(i.id)
                request.cr.execute(qry)
                print("Delete",i.id)

    for i in pjs:
        val = request.env['candidate.jobs'].sudo().search([('partner_id','=',p_id),('id','=',int(i["popupexp_job_id"]))])
        if val.id:
            qry ="UPDATE candidate_jobs SET job_title='" + i["popupexp_job_title"] + "', name = '" +  i["popupexp_name"] + "', date_start = '" +   i["popupexp_date_start"]  + "', date_end = '" +   i["popupexp_date_end"] + "', functions = '" +   i["popupexp_functions"] + "', achievements = '" +   i["popupexp_achievements"] + "' WHERE ID = " + str(val.id)
            print("update",val.id,i)
        else:
            qry ="INSERT INTO candidate_jobs (partner_id,job_title, name, date_start, date_end, functions, achievements) \
                    VALUES (" + str(p_id) + ",'" + i["popupexp_job_title"] + "','" + i["popupexp_name"] + "','" + i["popupexp_date_start"] + "','" + i["popupexp_date_end"] + "','" + i["popupexp_functions"] + "','" + i["popupexp_achievements"] + "')"
            print("Insert ", p_id,i)
        request.cr.execute(qry)

def get_records_pager(ids, current):
    if current.id in ids and (hasattr(current, 'website_url') or hasattr(current, 'access_url')):
        attr_name = 'access_url' if hasattr(current, 'access_url') else 'website_url'
        idx = ids.index(current.id)
        return {
            'prev_record': idx != 0 and getattr(current.browse(ids[idx - 1]), attr_name),
            'next_record': idx < len(ids) - 1 and getattr(current.browse(ids[idx + 1]), attr_name),
        }
    return {}


def _build_url_w_params(url_string, query_params, remove_duplicates=True):
    """ Rebuild a string url based on url_string and correctly compute query parameters
    using those present in the url and those given by query_params. Having duplicates in
    the final url is optional. For example:

     * url_string = '/my?foo=bar&error=pay'
     * query_params = {'foo': 'bar2', 'alice': 'bob'}
     * if remove duplicates: result = '/my?foo=bar2&error=pay&alice=bob'
     * else: result = '/my?foo=bar&foo=bar2&error=pay&alice=bob'
    """
    url = urls.url_parse(url_string)
    url_params = url.decode_query()
    if remove_duplicates:  # convert to standard dict instead of werkzeug multidict to remove duplicates automatically
        url_params = url_params.to_dict()
    url_params.update(query_params)
    return url.replace(query=urls.url_encode(url_params)).to_url()


class CustomerPortal(http.Controller):

    MANDATORY_BILLING_FIELDS = ["name", "phone", "email", "street", "city", "country_id","gender","marital","birthday"]
    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name","link_linkedin","link_twitter","link_side","profile","cover","partner_edus_ids"]



    _items_per_page = 20

    def _prepare_portal_layout_values(self):
        """Values for /my/* templates rendering.

        Does not include the record counts.
        """




        # get customer sales rep
        sales_user = False
        partner = request.env.user.partner_id
        vacant = request.env['candidate.vacant']
        if partner.user_id and not partner.user_id._is_public():
            sales_user = partner.user_id

        return {
            'sales_user': sales_user,
            'page_name': 'home',
        }

    def _prepare_home_portal_values(self, counters):
        """Values for /my & /my/home routes template rendering.

        Includes the record count for the displayed badges.
        where 'coutners' is the list of the displayed badges
        and so the list to compute.
        """
        return {}

    @route(['/my/counters'], type='json', auth="user", website=True)
    def counters(self, counters, **kw):
        return self._prepare_home_portal_values(counters)

    @route(['/mi/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        values = self._prepare_portal_layout_values()
        cand_progress = request.env.user.cand_progress
        image_1920 = request.env.user.image_1920
        partner_id = request.env.user.partner_id.id
        if request.env.user.is_company:
            values.update({
            'cand_progress': cand_progress,'image_1920': image_1920 , 'is_company': request.env.user.is_company, 'partner_id': partner_id
            })
            return request.render("empleabilidad.portal_my_company", values)
        else:
            values.update({
                'cand_progress': cand_progress,'image_1920': image_1920 , 'is_company': request.env.user.is_company, 'partner_id': partner_id
                })
            return request.render("empleabilidad.portal_my_home", values)

    @http.route('/mi/listaoportunidad/oportunidad/Cat/<cat_id>', type='http', auth='user', website=True,methods=['POST','GET'])
    def EmpresaCandidateCat(self,cat_id,redirect=None, **post):
        categories = request.env['res.partner.category'].sudo().search([])
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        vacant_id = request.session['vacant_id']
        if int(vacant_id) > 0:
            vacant = request.env['candidate.vacant']
        else:
            vacant = request.env['candidate.vacant'].sudo().browse(int(vacant_id))
        if post:
            values = post
            values['partner_id'] = partner.id

            if 'Cancelar' in post:
                return request.redirect('/mi/listaoportunidad/oportunidad/'+ str(vacant['id']))
            else:
                if int(values['category_id']) not in vacant.categ_ids.ids:
                    qry ="INSERT INTO candidate_vacant_res_partner_category_rel (candidate_vacant_id,res_partner_category_id) VALUES (" + str(vacant['id']) + "," + post['category_id'] + ")"
                    request.cr.execute(qry)

                return request.redirect('/mi/listaoportunidad/oportunidad/'+ str(vacant['id']))
        else:
            if int(cat_id)>0: 
                #vacant.categ_ids
                qry ="DELETE FROM candidate_vacant_res_partner_category_rel WHERE candidate_vacant_id=" + str(vacant['id'])   + " and res_partner_category_id=" + cat_id 
                request.cr.execute(qry)
                return request.redirect('/mi/listaoportunidad/oportunidad/'+ str(vacant['id']))

        #partner = request.env.user.partner_id
        #cat = request.env['res_partner_res_partner_category_rel']
        #cat.update({'partner_id':partner.id})
        cat={}
        cat['partner_id']=partner.id
        cat['category_id']=''
        values.update({
            'cat': cat,
            'redirect': redirect,
            'page_name': 'cargos',
            'categories': categories
        })
        response = request.render("empleabilidad.CandidateVacanteCat", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response


    @http.route('/mi/cuenta/CandidateCat/<cat_id>', type='http', auth='user', website=True,methods=['POST','GET'])
    def CandidateCat(self,cat_id, redirect=None, **post):
        #tuple([tuple(row) for row in myarray])  convertir un arregl en tupla
        categories = request.env['res.partner.category'].sudo().search([])
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        if post:
            if 'Cancelar' in post:
                return request.redirect('/mi/cuenta')
            else:
                #partner = request.env.user.partner_id
                values = post
                values['partner_id'] = partner.id
                #list=request.env['res.partner'].sudo().search([('partner_id','=',partner.id)]).category_id
                if int(values['category_id']) not in partner.category_id.ids:
                    qry ="INSERT INTO res_partner_res_partner_category_rel VALUES (" + values['category_id'] + "," + str(values['partner_id']) + ")"
                    request.cr.execute(qry)
                return request.redirect('/mi/cuenta')
        else:
            if int(cat_id)>0: 
                qry ="DELETE FROM res_partner_res_partner_category_rel WHERE category_id=" + cat_id + " and partner_id=" + str(partner.id) 
                print(qry)
                request.cr.execute(qry)
                return request.redirect('/mi/cuenta')

        #partner = request.env.user.partner_id
        #cat = request.env['res_partner_res_partner_category_rel']
        #cat.update({'partner_id':partner.id})
        cat={}
        # cat = request.env['res.partner.res.partner.category.rel']
        #cat = request.env['res.partner']
        cat['partner_id']=partner.id
        

        #cat.update({'partner_id':partner.id})
        cat['category_id']=''
        values.update({
            'cat': cat,
            'redirect': redirect,
            'page_name': 'cargos',
            'categories': categories
        })
        response = request.render("empleabilidad.CandidateCat", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/mi/postulacion'], type='http', auth='user', website=True)
    def postulacion(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })

        if post:
            if 'Cancelar' in post:
                return request.redirect('/mi/home')


        values.update({
            'partner': partner,
            'redirect': redirect,
            'page_name': 'Postulacion',
        })

        response = request.render("empleabilidad.CandidatePostulaciones", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response




    @http.route('/mi/cuenta/skills/<sk_id>', type='http', auth='user', website=True,methods=['POST','GET'])
    def CandidateSkill(self, sk_id,redirect=None, **post):
        #tuple([tuple(row) for row in myarray])  convertir un arregl en tupla
        habilidad = request.env['hr.skill.type'].sudo().search([])
        Subhabilidad = request.env['hr.skill'].sudo().search([])
        nivel = request.env['hr.skill.level'].sudo().search([])
        values = self._prepare_portal_layout_values()
        if post:
            if 'Borrar' in post:
                if post['id']:
                    #values = self._prepare_portal_layout_values()
                    skill_id = post['id']
                    skill = request.env['candidate.skill'].sudo().browse(int(post['id']))
                    skill.sudo().unlink()
                return request.redirect('/mi/cuenta')

            elif 'Cancelar' in post:
                return request.redirect('/mi/cuenta')
            else:
                if post['id']:
                    skill_id = post['id']
                    skill = request.env['candidate.skill'].sudo().browse(int(post['id']))
                    values = post
                    values['partner_id'] = skill['partner_id'].id
                    skill.sudo().write(values)
                else:
                    partner = request.env.user.partner_id
                    values = post
                    values['skill_level_id'] = int(post['skill_level_id'])
                    values['skill_id'] = int(post['skill_level_id'])
                    if post['skill_id']:
                        sk = request.env['hr.skill'].sudo().search([('id','=',post['skill_id'])])
                        values['skill_type_id'] = sk.skill_type_id.id
                    values['partner_id'] = partner.id
                    skill = request.env['candidate.skill']
                    skill.sudo().create(values)

                return request.redirect('/mi/cuenta')

        if (int(sk_id)>0):
            skill = request.env['candidate.skill'].sudo().browse(int(sk_id))
            partner = request.env.user.partner_id
            values.update({
                        'skill': skill,
                        'redirect': redirect,
                        'page_name': 'skill',
                        'habilidad': habilidad,
                        'Subhabilidad':Subhabilidad,
                        'nivel':nivel
                    })
        else:
            partner = request.env.user.partner_id
            skill = request.env['candidate.skill']
            skill.update({'partner_id':partner.id})
            

            values.update({
                'skill': skill,
                'redirect': redirect,
                'page_name': 'skill',
                'habilidad': habilidad,
                'Subhabilidad':Subhabilidad,
                'nivel':nivel
            })
        response = request.render("empleabilidad.CandidateSkill", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route('/mi/cuenta/jobs/<job_id>', type='http', auth='user', website=True,methods=['POST','GET'])
    def CandidateJob(self, job_id, **post):
        values = self._prepare_portal_layout_values()
        if post:
            if 'Borrar' in post:
                if post['id']:
                    #values = self._prepare_portal_layout_values()
                    job_id = post['id']
                    job = request.env['candidate.jobs'].sudo().browse(int(post['id']))
                    job.sudo().unlink()
                return request.redirect('/mi/cuenta')

            elif 'Cancelar' in post:
                return request.redirect('/mi/cuenta')
            else:
                if post['id']:
                    job_id = post['id']
                    job = request.env['candidate.jobs'].sudo().browse(int(post['id']))
                    values = post
                    values['partner_id'] = job['partner_id'].id
                    job.sudo().write(values)
                else:
                    partner = request.env.user.partner_id
                    values = post
                    values['partner_id'] = partner.id
                    job = request.env['candidate.jobs']
                    job.sudo().create(values)

                return request.redirect('/mi/cuenta')

        if (int(job_id)>0):
            job = request.env['candidate.jobs'].sudo().browse(int(job_id))
            partner = request.env.user.partner_id
            values.update({
                        'job': job,
                        'redirect': '/mi/cuenta',
                        'page_name': 'job',
                    })
        else:
            partner = request.env.user.partner_id
            job = request.env['candidate.jobs']
            job.update({'partner_id':partner.id})

            values.update({
                'job': job,
                'redirect': '/mi/cuenta',
                'page_name': 'job',
            })
        response = request.render("empleabilidad.portal_mi_jobs", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response


    @http.route('/mi/cuenta/edu/<edu_id>', type='http', auth='user', website=True,methods=['POST','GET'])
    def CandidateEdu(self, edu_id, **post):

        values = self._prepare_portal_layout_values()
        TipoEdu = [('classic', 'Classic'),('Bachillerato','Bachillerato'),('Tecnico','Tecnico'),('Tecnologo','Tecnologo'),('Profesional','Profesional'),('Especializacion','Especializacion'),('Maestria','Maestria'),('Doctorado','Doctorado')]
        if post:
            if 'Borrar' in post:
                if post['id']:
                    values = self._prepare_portal_layout_values()
                    edu_id = post['id']
                    edu = request.env['candidate.edus'].sudo().browse(int(post['id']))
                    #request.env['candidate.edus'].sudo().remove(edu_id)
                    edu.sudo().unlink()
                return request.redirect('/mi/cuenta')

            elif 'Cancelar' in post:
                return request.redirect('/mi/cuenta')
            else:
                if post['id']:
                    edu_id = post['id']
                    edu = request.env['candidate.edus'].sudo().browse(int(post['id']))
                    values = post
                    values['partner_id'] = edu['partner_id'].id
                    edu.sudo().write(values)
                else:
                    partner = request.env.user.partner_id
                    values = post
                    values['partner_id'] = partner.id
                    edu = request.env['candidate.edus']
                    edu.sudo().create(values)

                return request.redirect('/mi/cuenta')

        #if post.partner.partner_edus_ids.id:
        if (int(edu_id)>0):
            #edu = request.env['candidate.edus'].sudo().browse(int(post.partner.partner_edus_ids.id))
            edu = request.env['candidate.edus'].sudo().browse(int(edu_id))
            partner = request.env.user.partner_id
            #_logger.info(post.partner.partner_edus_ids.id)    
            #_logger.info(edu)  
            #                        'partner': partner,
            values.update({
                        'TipoEdu' : TipoEdu,
                        'edu': edu,
                        'redirect': '/mi/cuenta',
                        'page_name': 'edu',
                    })
        else:
            partner = request.env.user.partner_id
            edu = request.env['candidate.edus']
            edu.update({'partner_id':partner.id})
            values.update({
                'TipoEdu' : TipoEdu,
                'edu': edu,
                'redirect': '/mi/cuenta',
                'page_name': 'edu',
            })
        response = request.render("empleabilidad.portal_mi_edu", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route('/mi/listaoportunidad/oportunidad/<id>', type='http', auth='user', website=True,methods=['POST','GET'])
    def EmpresaCandidateOportunidad(self, id, **post):
        values = self._prepare_portal_layout_values()
        prioridad = [ ('1', 'Baja'), ('2', 'Media'), ('3', 'Alta')]
        TipoEdu = request.env['hr.recruitment.degree'].sudo().search([])
        skill_Total1 = request.env['candidate.skills.view'].sudo().search([])
        skill_Total = []
        for l in skill_Total1:
            x_skill_dict={}
            x_skill_dict["type_id"] = l.type_id.id
            x_skill_dict["name_type"] = l.name_type.id
            x_skill_dict["skill_id"] = l.skill_id.id
            x_skill_dict["name_skill"] = l.name_skill.id
            x_skill_dict["level_id"] = l.level_id.id
            x_skill_dict["name_level"] = l.name_level.id
            x_skill_dict["level_progress"] = l.level_progress.id
            skill_Total.append(x_skill_dict)

        req = request.params
        x_categ_Totals = []
        x_categ_ids = request.env['res.partner.category'].sudo().search([])
        for l in x_categ_ids:
            x_categ_dict={}
            
            x_categ_dict["name"] = l.name
            #x_categ_dict["partner_id"] = '' #partner.id
            #x_categ_dict["candidate_vacant_id"] = '' #vacant.id
            x_categ_dict["res_partner_category_id"] = l.id

            x_categ_Totals.append(x_categ_dict)

        

        if post:
            if 'Borrar' in post:
                if post['id']:
                    vacant = request.env['candidate.vacant'].sudo().browse(int(id))
                    vacant.sudo().unlink()
                return request.redirect('/mi/listaoportunidad')

            elif 'Cancelar' in post:
                return request.redirect('/mi/listaoportunidad')
            elif 'AdicionaVacanteCat' in post:
                vacant = request.env['candidate.vacant'].sudo().browse(req['id'])
                #request.session.update({'vacant':vacant})
                return request.redirect('/mi/listaoportunidad/oportunidad/Cat/-1')


            else:
                vacant_id = post['vacant_id']
                if vacant_id:
                    vacant = request.env['candidate.vacant'].sudo().browse(int(vacant_id))
                    if 'csrf_token' in values:
                        del values['csrf_token']


                    
                    values = {}
                    
                    values['name'] = post['name']
                    values['description'] = post['description']
                    values['email_from'] = post['email_from']
                    values['date_open'] = post['date_open']
                    values['date_closed'] = post['date_closed']
                    values['priority'] = post['priority']
                    values['city'] = post['city']
                    values['probability'] = post['probability']
                    values['type_id'] = post['type_id']
                    values['salary_proposed'] = post['salary_proposed']
                    values["priority"] = post["vacant.priority"]

                    _logger.info("post['priority'] ",post['priority'])
                    #_logger.info("post.vacant.priority ",post.vacant.priority)

                    _logger.info("post[x_categ_dicts] ",post["x_categ_dicts"])

                    x_categ_ids=json.loads(json.loads(post["x_categ_dicts"]))
                    if (x_categ_ids):
                        list = []
                        for x in x_categ_ids:
                            list.append(int(x["category_id"]))
                        values["categ_ids"]=list
                    if int(post['vacant_id']) > 0:
                        values['id'] = post['vacant_id']
                        vacant.sudo().write(values)
                    else:
                        values['website_published'] = False
                        values['partner_id'] = int(post['partner_id'])
                        id=vacant.sudo().create(values)
                        post['vacant_id'] = id.id


                    
                    # Definimos s para el link con la tabla candidate.vacant.skill
                    s=request.env['candidate.vacant.skill'].sudo()
                    # Borrado de todos los skill del cliente
                    #for x in request.env['candidate.vacant'].sudo().browse(int(post['vacant_id'])).vacant_skill_ids:
                    #    s.sudo().write({'id': [3,x.id]})
                    # Cargue de los nuevos skill
                    #v = {}
                    x_skill_ids = json.loads(json.loads(post["x_skill_ids"]))
                    # Function to write JSON x_skill_ids into database
                    _SkillWrite(x_skill_ids,int(post['vacant_id']))

                    #for x in x_skill_ids:
                    #    v["skill_type_id"] = x["skill_type_id"]
                    #    v["vacant_id"] = post['vacant_id']
                    #    v["skill_id"] = x["skill_id"]
                    #    v["skill_level_id"] = x["skill_level_id"]
                    #    b=s.sudo().search([('vacant_id','=',int(post['vacant_id'])),('skill_id','=',int(x["skill_id"])),('skill_type_id','=',int(x["skill_type_id"]))])
                    #    if (b.ids):
                    #        s.sudo().write((1,b.ids,{'skill_level_id': int(x["skill_level_id"])}))
                    #    else:
                    #        s.sudo().create(v)
                        
                else:
                    partner = request.env.user.partner_id
                    values = post
                    values['partner_id'] = partner.id
                    #vacant = request.env['candidate.vacant']
                    vacant.sudo().create(values)

                return request.redirect('/mi/listaoportunidad')

        if (int(id)>0):
            vacant = request.env['candidate.vacant'].sudo().browse(int(id))
            partner = request.env.user.partner_id
            partner_id = partner.id
            vacant.update({'partner_id':partner.id})
            vacant_id = id
            cat_id = ''
            #x_categ_ids = [ ('4', 'Cuatro'), ('17', 'Diecisiete'), ('2', 'Dos')]
            x_categ_ids = []
            x_categ_dicts = []
            #x_categ_dict = {'partner_id': '','candidate_vacant_id': '','res_partner_category_id':'','name':''};
            for l in vacant.categ_ids:
                x_categ_dict={}
                x_categ_dict["name"] = l.name
                #x_categ_dict["partner_id"] = partner.id
                #x_categ_dict["candidate_vacant_id"] = vacant.id
                x_categ_dict["res_partner_category_id"] = l.id
                
                x_categ_dicts.append(x_categ_dict)

            x_skill_ids = []
            x_skill_dict = []
            #x_categ_dict = {'partner_id': '','candidate_vacant_id': '','res_partner_category_id':'','name':''};
            for l in vacant.vacant_skill_ids:
                x_skill_dict={}
                x_skill_dict["skill_id"] = l.skill_id.id
                x_skill_dict["skill_name"] = l.skill_id.name

                x_skill_dict["skill_type_id"] = l.skill_type_id.id
                x_skill_dict["skill_type_name"] = l.skill_type_id.name

                x_skill_dict["skill_level_id"] = l.skill_level_id.id
                x_skill_dict["skill_level_name"] = l.skill_level_id.name

                x_skill_dict["level_progress"] = l.level_progress
                
                x_skill_ids.append(x_skill_dict)

            #x_categ_ids = { 'Cuatro', 'Diecisiete' ,'Dos' }

            values.update({
                        'vacant': vacant,
                        'prioridad': prioridad,
                        'TipoEdu': TipoEdu,
                        'cat_id' : cat_id,
                        'vacant_id': vacant_id,
                        'partner_id': partner_id,
                        'x_categ_ids' : x_categ_ids,
                        'x_categ_dicts' : x_categ_dicts,
                        'x_categ_Totals': x_categ_Totals,
                        'skill_Total' : skill_Total,
                        'x_skill_ids' : x_skill_ids,
                        'redirect': '/mi/creaoportunidad',
                        'page_name': 'EmpresaCandidateOportunidad',
                    })


        else:
            partner = request.env.user.partner_id
            partner_id = partner.id
            vacant_id = -1
            vacant = request.env['candidate.vacant'].sudo()
            #vacant.update({'vacant_id':id})
            vacant.update({'partner_id':partner.id})
            cat_id = ''
            #x_categ_ids = { 'Cuatro', 'Diecisiete' ,'Dos' }
            x_categ_ids = {}
            x_skill_ids = {}
            x_categ_dicts = {}
            values.update({
                'vacant': vacant,
                'prioridad': prioridad,
                'TipoEdu' :TipoEdu,
                'cat_id' : cat_id,
                'vacant_id': vacant_id,
                'partner_id': partner_id,
                'x_categ_ids' : x_categ_ids,
                'x_categ_dicts' : x_categ_dicts,
                'x_categ_Totals': x_categ_Totals,
                'skill_Total' : skill_Total,   
                'x_skill_ids' : x_skill_ids,             
                'redirect': '/mi/listaoportunidad',
                'page_name': 'EmpresaCandidateOportunidad',
            })


        response = request.render("empleabilidad.portal_mi_vacant", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route('/mi/listaoportunidad', type='http', auth='user', website=True,methods=['POST','GET'])
    def MiListaOportunidad(self, **post):
        values = self._prepare_portal_layout_values()
        prioridad = [ ('1', 'Baja'), ('2', 'Media'), ('3', 'Alta')]
        TipoEdu = request.env['hr.recruitment.degree'].sudo().search([])

        if post:
            if 'Borrar' in post:
                if post['id']:
                    job_id = post['id']
                    vacant = request.env['candidate.vacant'].sudo().browse(int(post['id']))
                    vacant.sudo().unlink()
                return request.redirect('/mi/listaoportunidad')

            elif 'Cancelar' in post:
                return request.redirect('/mi/listaoportunidad')
            elif 'Volver' in post:
                return request.redirect('/mi/home')                
            elif 'AdicionaVacanteCat' in post:
                vacant = request.env['candidate.vacant'].sudo().browse(int(id))
                return request.redirect('/mi/cuentaempresa/CandidateCat/-1')
            elif 'AdicionaOportunidad' in post:
                vacant = request.env['candidate.vacant']
                request.session['vacant_id']='-1'
                return request.redirect('/mi/listaoportunidad/oportunidad/-1')
            else:
                if post['id']:
                    job_id = post['id']
                    job = request.env['candidate.vacant'].sudo().browse(int(post['id']))
                    values = post
                    values['partner_id'] = job['partner_id'].id
                    vacant.sudo().write(values)
                else:
                    partner = request.env.user.partner_id
                    values = post
                    values['partner_id'] = partner.id
                    vacant = request.env['candidate.vacant']
                    vacant.sudo().create(values)

                return request.redirect('/mi/creaoportunidad/lista')

        else:
            partner = request.env.user.partner_id
            vacant = request.env['candidate.vacant'].sudo().search([('partner_id','=',partner.id)])
            vacant.update({'partner_id':partner.id})
            #'redirect': '/mi/listaoportunidad',
            values.update({
                'vacant': vacant,
                'prioridad': prioridad,
                'TipoEdu' :TipoEdu,
                'redirect': '/mi/home',
                'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
                'page_name': 'Candidate',
            })
        response = request.render("empleabilidad.portal_my_oportunidad", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/account'], type='http', auth='user', website=True)
    def micuentaempresa(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                for field in set(['country_id', 'state_id']) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                    except:
                        values[field] = False
                values.update({'zip': values.pop('zipcode', '')})
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                #return request.redirect('/my/home')
                return request.redirect('/my/account')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
        })

        response = request.render("empleabilidad.portal_my_details_company", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response



    @route(['/mi/cuenta'], type='http', auth='user', website=True)
    def micuentapersona(self, redirect=None, **post):
        TipoEdu = [('classic', 'Classic'),('Bachillerato','Bachillerato'),('Tecnico','Tecnico'),('Tecnologo','Tecnologo'),('Profesional','Profesional'),('Especializacion','Especializacion'),('Maestria','Maestria'),('Doctorado','Doctorado')]
        # Caso 5  Inicio de llenado de todos los skill
        skill_Total1 = request.env['candidate.skills.view'].sudo().search([])
        skill_Total = []
        for l in skill_Total1:
            x_skill_dict={}
            x_skill_dict["type_id"] = l.type_id.id
            x_skill_dict["name_type"] = l.name_type.id
            x_skill_dict["skill_id"] = l.skill_id.id
            x_skill_dict["name_skill"] = l.name_skill.id
            x_skill_dict["level_id"] = l.level_id.id
            x_skill_dict["name_level"] = l.name_level.id
            x_skill_dict["level_progress"] = l.level_progress.id
            skill_Total.append(x_skill_dict)

        x_categ_Totals = []
        x_categ_ids = request.env['res.partner.category'].sudo().search([])
        for l in x_categ_ids:
            x_categ_dict={}
            
            x_categ_dict["name"] = l.name
            #x_categ_dict["partner_id"] = '' #partner.id
            #x_categ_dict["candidate_vacant_id"] = '' #vacant.id
            x_categ_dict["res_partner_category_id"] = l.id

            x_categ_Totals.append(x_categ_dict)    

        # Caso 5  Fin de llenado de todos los skill

        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        x_photo = partner.image_1920
        values.update({
            'error': {},
            'error_message': [],
        })
        if post and request.httprequest.method == 'POST':
            if 'AdicionaEdu' in post:
                print('Existe')
                return request.redirect('/mi/cuenta/edu/-1')
            elif 'AdicionaJob' in post:
                return request.redirect('/mi/cuenta/jobs/-1')
            #elif 'AdicionaSkill' in post:
            #    return request.redirect('/mi/cuenta/skills/-1')       
            elif 'AdicionaCat' in post:
                return request.redirect('/mi/cuenta/CandidateCat/-1')                           
            else:
                #error, error_message = self.details_form_validate(post)
                error = ''                
                #_logger.info('An INFO error and error_message')
                #_logger.info(error)
                #_logger.info(error_message)
                #values.update({'error': error, 'error_message': error_message})
                values.update(post)
                if not error:
                    values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                    values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                    for field in set(['country_id', 'state_id','salary']) & set(values.keys()):
                        try:
                            values[field] = int(values[field])
                        except:
                            values[field] = False
                    values.update({'zip': values.pop('zipcode', 'image_1920')})
                    values['salary'] = int(post['salary'])
                    values['l10n_latam_identification_type_id'] = int(post['l10n_latam_identification_type_id'])
                    values.update({'image_1920': x_photo})
                    x_photo = post["x_photo"]
                    if 'jpeg' in x_photo:
                        x_photo = x_photo.replace('data:image/jpeg;base64,','')
                    if 'png' in x_photo:
                        x_photo = x_photo.replace('data:image/png;base64,','')
                    
                    x_photo = unicodedata.normalize('NFKD', x_photo).encode('ascii', 'ignore')
                    values["image_1920"] = x_photo
                    # Poner las categorias
                    #x_categ_ids=json.loads(json.loads(post["x_categ_dicts"]))
                    x_categ_ids=json.loads(post["x_categ_dicts"])
                    if len(x_categ_ids) > 0:
                        x_categ_ids=json.loads(x_categ_ids)
                        if (x_categ_ids):
                            list = []
                            for x in x_categ_ids:
                                list.append(int(x["res_partner_category_id"]))
                            values["category_id"]=list
                        # salvar los datos en partner    
                    partner.sudo().write(values)    

                    # poner aca la actualziacion de skill
                    #x_skill_ids = json.loads(json.loads(post["x_skill_ids"]))
                    x_skill_ids = json.loads(post["x_skill_ids"])
                    if len(x_skill_ids) > 0:
                        x_skill_ids=json.loads(x_skill_ids)
                    # Function to write JSON x_skill_ids into database
                    _SkillWriteHV(x_skill_ids,partner.id)
                    # poner aca la actualziacion de estudios
                    x_estrudios_ids=json.loads(post["x_estudios_ids"])
                    if len(x_estrudios_ids) > 0:
                        x_estrudios_ids=json.loads(x_estrudios_ids)
                    _ESTWriteHV(x_estrudios_ids,partner.id)
                    # pponer a la actualizacion de la experiencia
                    x_experiencia_ids=json.loads(post["x_experiencia_ids"])
                    if len(x_experiencia_ids) > 0:
                        x_experiencia_ids=json.loads(x_experiencia_ids)                    
                    _EXPWriteHV(x_experiencia_ids,partner.id)


                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/mi/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        identification_types = request.env['l10n_latam.identification.type'].sudo().search([])

        genders = [('male', 'Male'),('female', 'Female'),('other', 'Other')]
        maritals = [('single', 'Single'),('married', 'Married'),('cohabitant', 'Legal Cohabitant'),('widower', 'Widower'),('divorced', 'Divorced')]

        # Caso 4  Inicio Llenado del arreglo de los skill de la persona
        x_skill_ids = []
        x_skill_dict = []
        for l in partner.partner_skill_ids:
            x_skill_dict={}
            x_skill_dict["skill_id"] = l.skill_id.id
            x_skill_dict["skill_name"] = l.skill_id.name

            x_skill_dict["skill_type_id"] = l.skill_type_id.id
            x_skill_dict["skill_type_name"] = l.skill_type_id.name

            x_skill_dict["skill_level_id"] = l.skill_level_id.id
            x_skill_dict["skill_level_name"] = l.skill_level_id.name

            x_skill_dict["level_progress"] = l.level_progress
            
            x_skill_ids.append(x_skill_dict)

        x_categ_ids = []
        x_categ_dicts = []
        #x_categ_dict = {'partner_id': '','candidate_vacant_id': '','res_partner_category_id':'','name':''};
        for l in partner.category_id:
            x_categ_dict={}
            x_categ_dict["name"] = l.name
            #x_categ_dict["partner_id"] = partner.id
            #x_categ_dict["candidate_vacant_id"] = vacant.id
            x_categ_dict["res_partner_category_id"] = l.id
            
            x_categ_dicts.append(x_categ_dict)    

        # Caso 4  Fin Llenado del arreglo de los skill de la persona

        values.update({
            'partner': partner,
            'x_skill_ids': x_skill_ids,   # se renderiza los skill de la persona
            'skill_Total' : skill_Total,  # se renderiza TODOS los skill
            'x_categ_ids' : x_categ_ids,
            'x_categ_dicts' : x_categ_dicts,
            'x_categ_Totals': x_categ_Totals, # Lista total de Categorias
            'countries': countries,
            'states': states,
            'genders': genders,
            'maritals': maritals,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'cuenta',
            'TipoEdu' : TipoEdu,
            'x_photo': x_photo,
            "identification_types" : identification_types
        })

        response = request.render("empleabilidad.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
        
    @route('/mi/hvpdf/<id>', type='http', auth='user', website=True, methods=['GET'])
    def mihvpdf(self, id, redirect=None, **post):
        # Averiguar si es un cliente el id
        partner = request.env['res.partner'].sudo().search([('id','=',id)])
        if not partner:        
            if redirect:
                return request.redirect(redirect)
            return request.redirect('/mi/home')

        TipoEdu = [('classic', 'Classic')]
        # Caso 5  Inicio de llenado de todos los skill
        skill_Total1 = request.env['candidate.skills.view'].sudo().search([])
        skill_Total = []
        for l in skill_Total1:
            x_skill_dict={}
            x_skill_dict["type_id"] = l.type_id.id
            x_skill_dict["name_type"] = l.name_type.id
            x_skill_dict["skill_id"] = l.skill_id.id
            x_skill_dict["name_skill"] = l.name_skill.id
            x_skill_dict["level_id"] = l.level_id.id
            x_skill_dict["name_level"] = l.name_level.id
            x_skill_dict["level_progress"] = l.level_progress.id
            skill_Total.append(x_skill_dict)

        x_categ_Totals = []
        x_categ_ids = request.env['res.partner.category'].sudo().search([])
        for l in x_categ_ids:
            x_categ_dict={}
            
            x_categ_dict["name"] = l.name
            #x_categ_dict["partner_id"] = '' #partner.id
            #x_categ_dict["candidate_vacant_id"] = '' #vacant.id
            x_categ_dict["res_partner_category_id"] = l.id

            x_categ_Totals.append(x_categ_dict)    

        # Caso 5  Fin de llenado de todos los skill

        values = self._prepare_portal_layout_values()
        #partner = request.env.user.partner_id
        x_photo = partner.image_1920
        values.update({
            'error': {},
            'error_message': [],
        })
        if post and request.httprequest.method == 'POST':
            if redirect:
                return request.redirect(redirect)
            return request.redirect('/mi/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        identification_types = request.env['l10n_latam.identification.type'].sudo().search([])

        genders = [('male', 'Male'),('female', 'Female'),('other', 'Other')]
        maritals = [('single', 'Single'),('married', 'Married'),('cohabitant', 'Legal Cohabitant'),('widower', 'Widower'),('divorced', 'Divorced')]

        # Caso 4  Inicio Llenado del arreglo de los skill de la persona
        x_skill_ids = []
        x_skill_dict = []
        for l in partner.partner_skill_ids:
            x_skill_dict={}
            x_skill_dict["skill_id"] = l.skill_id.id
            x_skill_dict["skill_name"] = l.skill_id.name

            x_skill_dict["skill_type_id"] = l.skill_type_id.id
            x_skill_dict["skill_type_name"] = l.skill_type_id.name

            x_skill_dict["skill_level_id"] = l.skill_level_id.id
            x_skill_dict["skill_level_name"] = l.skill_level_id.name

            x_skill_dict["level_progress"] = l.level_progress
            
            x_skill_ids.append(x_skill_dict)

        x_categ_ids = []
        x_categ_dicts = []
        #x_categ_dict = {'partner_id': '','candidate_vacant_id': '','res_partner_category_id':'','name':''};
        for l in partner.category_id:
            x_categ_dict={}
            x_categ_dict["name"] = l.name
            #x_categ_dict["partner_id"] = partner.id
            #x_categ_dict["candidate_vacant_id"] = vacant.id
            x_categ_dict["res_partner_category_id"] = l.id
            
            x_categ_dicts.append(x_categ_dict)    

        # Caso 4  Fin Llenado del arreglo de los skill de la persona

        values.update({
            'partner': partner,
            'x_skill_ids': x_skill_ids,   # se renderiza los skill de la persona
            'skill_Total' : skill_Total,  # se renderiza TODOS los skill
            'x_categ_ids' : x_categ_ids,
            'x_categ_dicts' : x_categ_dicts,
            'x_categ_Totals': x_categ_Totals, # Lista total de Categorias
            'countries': countries,
            'states': states,
            'genders': genders,
            'maritals': maritals,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'cuenta',
            'TipoEdu' : TipoEdu,
            'x_photo': x_photo,
            "identification_types" : identification_types
        })

        response = request.render("empleabilidad.hvpdf", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    def _contract_get_page_view_values(self, contract, access_token, **kwargs):
        values = {
            "page_name": "Contracts",
            "contract": contract,
        }
        return self._get_page_view_values(
            contract, access_token, values, "my_contracts_history", False, **kwargs
        )
        
    def _get_filter_domain(self, kw):
        return []

    @http.route(["/mis/contratos"], type="http",  auth="user",  website=True )
    def portal_mis_contratos(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        contract_obj = request.env["contract.contract"]
        # Avoid error if the user does not have access.
        if not contract_obj.check_access_rights("read", raise_exception=False):
            return request.redirect("/mi/home")
        domain = self._get_filter_domain(kw)
        searchbar_sortings = {
            "date": {"label": _("Date"), "order": "recurring_next_date desc"},
            "name": {"label": _("Name"), "order": "name desc"},
            "code": {"label": _("Reference"), "order": "code desc"},
        }
        # default sort by order
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]
        # count for pager
        contract_count = contract_obj.search_count(domain)
        # pager
        pager = portal_pager(
            url="/mis/contractos",
            url_args={
                "date_begin": date_begin,
                "date_end": date_end,
                "sortby": sortby,
            },
            total=contract_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager and archive selected
        contracts = contract_obj.search(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        )
        request.session["my_contracts_history"] = contracts.ids[:100]
        values.update(
            {
                "date": date_begin,
                "contracts": contracts,
                "page_name": "Contracts",
                "pager": pager,
                "default_url": "/mis/contratos",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render("empleabilidad.portal_mis_contratos", values)

    @http.route(
        ["/mi/contrato/<int:contract_contract_id>"],
        type="http",
        auth="public",
        website=True,
    )
    def portal_mi_contracto_detalle(self, contract_contract_id, access_token=None, **kw):
        try:
            contract_sudo = self._document_check_access(
                "contract.contract", contract_contract_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/mi/home")
        values = self._contract_get_page_view_values(contract_sudo, access_token, **kw)
        return request.render("empleabilidad.portal_contrato_pagina", values)


    @route('/my/security', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def security(self, **post):
        values = self._prepare_portal_layout_values()
        values['get_error'] = get_error

        if request.httprequest.method == 'POST':
            values.update(self._update_password(
                post['old'].strip(),
                post['new1'].strip(),
                post['new2'].strip()
            ))

        return request.render('portal.portal_my_security', values, headers={
            'X-Frame-Options': 'DENY'
        })

    def _update_password(self, old, new1, new2):
        for k, v in [('old', old), ('new1', new1), ('new2', new2)]:
            if not v:
                return {'errors': {'password': {k: _("You cannot leave any password empty.")}}}

        if new1 != new2:
            return {'errors': {'password': {'new2': _("The new password and its confirmation must be identical.")}}}

        try:
            request.env['res.users'].change_password(old, new1)
        except UserError as e:
            return {'errors': {'password': e.name}}
        except AccessDenied as e:
            msg = e.args[0]
            if msg == AccessDenied().args[0]:
                msg = _('The old password you provided is incorrect, your password was not changed.')
            return {'errors': {'password': {'old': msg}}}

        # update session token so the user does not get logged out (cache cleared by passwd change)
        new_token = request.env.user._compute_session_token(request.session.sid)
        request.session.session_token = new_token

        return {'success': {'password': True}}

    @http.route('/portal/attachment/add', type='http', auth='public', methods=['POST'], website=True)
    def attachment_add(self, name, file, res_model, res_id, access_token=None, **kwargs):
        """Process a file uploaded from the portal chatter and create the
        corresponding `ir.attachment`.

        The attachment will be created "pending" until the associated message
        is actually created, and it will be garbage collected otherwise.

        :param name: name of the file to save.
        :type name: string

        :param file: the file to save
        :type file: werkzeug.FileStorage

        :param res_model: name of the model of the original document.
            To check access rights only, it will not be saved here.
        :type res_model: string

        :param res_id: id of the original document.
            To check access rights only, it will not be saved here.
        :type res_id: int

        :param access_token: access_token of the original document.
            To check access rights only, it will not be saved here.
        :type access_token: string

        :return: attachment data {id, name, mimetype, file_size, access_token}
        :rtype: dict
        """
        try:
            self._document_check_access(res_model, int(res_id), access_token=access_token)
        except (AccessError, MissingError) as e:
            raise UserError(_("The document does not exist or you do not have the rights to access it."))

        IrAttachment = request.env['ir.attachment']
        access_token = False

        # Avoid using sudo or creating access_token when not necessary: internal
        # users can create attachments, as opposed to public and portal users.
        if not request.env.user.has_group('base.group_user'):
            IrAttachment = IrAttachment.sudo().with_context(binary_field_real_user=IrAttachment.env.user)
            access_token = IrAttachment._generate_access_token()

        # At this point the related message does not exist yet, so we assign
        # those specific res_model and res_is. They will be correctly set
        # when the message is created: see `portal_chatter_post`,
        # or garbage collected otherwise: see  `_garbage_collect_attachments`.
        attachment = IrAttachment.create({
            'name': name,
            'datas': base64.b64encode(file.read()),
            'res_model': 'mail.compose.message',
            'res_id': 0,
            'access_token': access_token,
        })
        return request.make_response(
            data=json.dumps(attachment.read(['id', 'name', 'mimetype', 'file_size', 'access_token'])[0]),
            headers=[('Content-Type', 'application/json')]
        )

    @http.route('/portal/attachment/remove', type='json', auth='public')
    def attachment_remove(self, attachment_id, access_token=None):
        """Remove the given `attachment_id`, only if it is in a "pending" state.

        The user must have access right on the attachment or provide a valid
        `access_token`.
        """
        try:
            attachment_sudo = self._document_check_access('ir.attachment', int(attachment_id), access_token=access_token)
        except (AccessError, MissingError) as e:
            raise UserError(_("The attachment does not exist or you do not have the rights to access it."))

        if attachment_sudo.res_model != 'mail.compose.message' or attachment_sudo.res_id != 0:
            raise UserError(_("The attachment %s cannot be removed because it is not in a pending state.", attachment_sudo.name))

        if attachment_sudo.env['mail.message'].search([('attachment_ids', 'in', attachment_sudo.ids)]):
            raise UserError(_("The attachment %s cannot be removed because it is linked to a message.", attachment_sudo.name))

        return attachment_sudo.unlink()

    def details_form_validate(self, data):
        error = dict()
        error_message = []

        # Validation
        for field_name in self.MANDATORY_BILLING_FIELDS:
            if not data.get(field_name):
                error[field_name] = 'missing'
                #_logger.info('An INFO error and error_message missing')
                #_logger.info(field_name)


        # email validation
        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = 'error'
            error_message.append(_('Invalid Email! Please enter a valid email address.'))

        # vat validation
        partner = request.env.user.partner_id
        if data.get("vat") and partner and partner.vat != data.get("vat"):
            if partner.can_edit_vat():
                if hasattr(partner, "check_vat"):
                    if data.get("country_id"):
                        data["vat"] = request.env["res.partner"].fix_eu_vat_number(int(data.get("country_id")), data.get("vat"))
                    partner_dummy = partner.new({
                        'vat': data['vat'],
                        'country_id': (int(data['country_id'])
                                       if data.get('country_id') else False),
                    })
                    try:
                        partner_dummy.check_vat()
                    except ValidationError:
                        error["vat"] = 'error'
            else:
                error_message.append(_('Changing VAT number is not allowed once document(s) have been issued for your account. Please contact us directly for this operation.'))

        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        """
        unknown = [k for k in data if k not in self.MANDATORY_BILLING_FIELDS + self.OPTIONAL_BILLING_FIELDS]
        if unknown:
            error['common'] = 'Unknown field'
            error_message.append("Unknown field '%s'" % ','.join(unknown))
        """
        return error, error_message

    def _document_check_access(self, model_name, document_id, access_token=None):
        document = request.env[model_name].browse([document_id])
        document_sudo = document.with_user(SUPERUSER_ID).exists()
        if not document_sudo:
            raise MissingError(_("This document does not exist."))
        try:
            document.check_access_rights('read')
            document.check_access_rule('read')
        except AccessError:
            if not access_token or not document_sudo.access_token or not consteq(document_sudo.access_token, access_token):
                raise
        return document_sudo

    def _get_page_view_values(self, document, access_token, values, session_history, no_breadcrumbs, **kwargs):
        if access_token:
            # if no_breadcrumbs = False -> force breadcrumbs even if access_token to `invite` users to register if they click on it
            values['no_breadcrumbs'] = no_breadcrumbs
            values['access_token'] = access_token
            values['token'] = access_token  # for portal chatter

        # Those are used notably whenever the payment form is implied in the portal.
        if kwargs.get('error'):
            values['error'] = kwargs['error']
        if kwargs.get('warning'):
            values['warning'] = kwargs['warning']
        if kwargs.get('success'):
            values['success'] = kwargs['success']
        # Email token for posting messages in portal view with identified author
        if kwargs.get('pid'):
            values['pid'] = kwargs['pid']
        if kwargs.get('hash'):
            values['hash'] = kwargs['hash']

        history = request.session.get(session_history, [])
        values.update(get_records_pager(history, document))

        return values

    def _show_report(self, model, report_type, report_ref, download=False):
        if report_type not in ('html', 'pdf', 'text'):
            raise UserError(_("Invalid report type: %s", report_type))

        report_sudo = request.env.ref(report_ref).with_user(SUPERUSER_ID)

        if not isinstance(report_sudo, type(request.env['ir.actions.report'])):
            raise UserError(_("%s is not the reference of a report", report_ref))

        if hasattr(model, 'company_id'):
            report_sudo = report_sudo.with_company(model.company_id)

        method_name = '_render_qweb_%s' % (report_type)
        report = getattr(report_sudo, method_name)([model.id], data={'report_type': report_type})[0]
        reporthttpheaders = [
            ('Content-Type', 'application/pdf' if report_type == 'pdf' else 'text/html'),
            ('Content-Length', len(report)),
        ]
        if report_type == 'pdf' and download:
            filename = "%s.pdf" % (re.sub('\W+', '-', model._get_report_base_filename()))
            reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))
        return request.make_response(report, headers=reporthttpheaders)

def get_error(e, path=''):
    """ Recursively dereferences `path` (a period-separated sequence of dict
    keys) in `e` (an error dict or value), returns the final resolution IIF it's
    an str, otherwise returns None
    """
    for k in (path.split('.') if path else []):
        if not isinstance(e, dict):
            return None
        e = e.get(k)

    return e if isinstance(e, str) else None
