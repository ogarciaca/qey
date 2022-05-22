from odoo import http, _
import pdb
from odoo.addons.http_routing.models.ir_http import slug
from odoo.http import request
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

        Vacantes = env['candidate.vacant']
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


        return request.render("empleabilidad.detalle", {
            'job': job,
            'main_object': job,
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
