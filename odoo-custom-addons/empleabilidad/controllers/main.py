from odoo import http, _
import pdb
from odoo.addons.http_routing.models.ir_http import slug
from odoo.http import request,content_disposition, Controller, request, route
from werkzeug.exceptions import NotFound
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class WebsiteEmplWorks(http.Controller):
    def sitemap_jobs(env, rule, qs):
        if not qs or qs.lower() in '/vacantes':
            yield {'loc': '/vacantes'}

    @http.route([
        '/vacantes'   ], 
        type='http', auth="public", 
        website=True
        , sitemap=sitemap_jobs
        )
    def vacantes(self, country=None, department=None, office_id=None, **kwargs):
        _logger.debug("Ingreso en def vacantes ! ")
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))

        Vacantes = env['candidate.vacant'].sudo()
        _logger.debug("Cargo variables de ambiente candidate.vacant ")
        #_logger.debug("Vacantes : " + Vacantes)
        # List jobs available to current UID
        domain = request.website.website_domain()
        domain = ['&',("website_published","=",True),("active","=",True)]
        _logger.debug("Cargo el domain ")
        job_ids = Vacantes.search(domain,order="create_date desc").ids
        # Browse jobs as superuser, because address is restricted
        jobs = Vacantes.sudo().browse(job_ids)
        # Render page
        return request.render("empleabilidad.vacantes", {
            'jobs': jobs
        })

    @http.route('''/vacantes/detalle/<model("candidate.vacant"):job>''', type='http', auth="public", website=True, sitemap=True)
    def vacantes_detalle(self, job, **kwargs):
        partner = request.env.user.partner_id
        
        partner_activo=False
        if partner:
            if partner.cand_progress >= 99:
                partner_activo=True


        return request.render("empleabilidad.detalle", {
            'job': job,
            'main_object': job,
            'partner_activo' : partner_activo,
        })

    @http.route('''/jobs/apply/<model("hr.job"):job>''', type='http', auth="public", website=True, sitemap=True)
    def jobs_apply(self, job, **kwargs):
        if not job.can_access_from_current_website():
            raise NotFound()

        error = {}
        default = {}
        if 'website_hr_recruitment_error' in request.session:
            error = request.session.pop('website_hr_recruitment_error')
            default = request.session.pop('website_hr_recruitment_default')
        return request.render("website_hr_recruitment.apply", {
            'job': job,
            'error': error,
            'default': default,
        })

    @http.route('/candidate_webform_basic', type='http', auth="public", website=True, sitemap=True)
    def candidate_webform(self, **kwargs):
        return request.render("empleabilidad.candidate_website_form_basic",{})


    @http.route('/create/webcandidate', type='http', auth="public", website=True, sitemap=True)
    def create_web_candidate(self, **kwargs):
        print("Candidato creado----------------",kwargs)
        request.env['empleabilidad.res.partner'].sudo().create(kwargs)
        return request.render("empleabilidad.candidate_thanks")

"""
class CustomerPortal(Controller):

    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
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
                return request.redirect('/my/home')

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

        response = request.render("portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response        
"""