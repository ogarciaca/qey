# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import unslug


class Main(http.Controller):
    @http.route('/books', type='http', auth="public", website=True)
    def library_books(self):
        return request.render(
            'my_library.books', {
                'books': request.env['library.book'].search([]),
            })

# @http.route tiene varios parametros
#     el primer parametro es la ruta donde estan los modelos. Pueden poner varios path separados por coma(,)
#      '/path1','/path2'
#       El parametro "type" (default = http) determina que tipo de respueta dar. tambuen puede ser json
#       CUnado es type='hhtp' indica a odoo que devuelva un string en formato HTML
# 
# 
     
class Main(http.Controller):
    """  
    @http.route('/books', type='http', auth='none' )
    def books(self):
        books = request.env['library.book'].sudo().search([])
        html_result = '<html><body><ul>'
        for book in books:
            html_result += "<li> %s </li>" % book.name
        html_result += '</ul></body></html>'
        return html_result
"""
# Se hizo la prueba con postman 
#    curl -i -X POST -H "Content-Type: application/json" -d "{}" 192.168.0.30:8069/my_library/books/json
#    y devuelve un JSON con los datos de los libros

    @http.route('/my_library/books/json', type='json', auth='none')
    def books_json(self):
        records = request.env['library.book'].sudo().search([])
        return records.read(['name'])

    @http.route('/my_library/all-books', type='http', auth='none')
    def all_books(self):
        books = request.env['library.book'].sudo().search([])
        html_result = '<html><body><ul>'
        for book in books:
            html_result += "<li> %s </li>" % book.name
        html_result += '</ul></body></html>'
        return html_result

    @http.route('/my_library/all-books/mark-mine', type='http', auth='public')
    def all_books_mark_mine(self):
        books = request.env['library.book'].sudo().search([])
        html_result = '<html><body><ul>'
        for book in books:
            if request.env.user.partner_id.id in book.author_ids.ids:
                html_result += "<li> <b>%s</b> </li>" % book.name
            else:
                html_result += "<li> %s </li>" % book.name
        html_result += '</ul></body></html>'
        return html_result    

    @http.route('/my_library/all-books/mine', type='http', auth='user')
    def all_books_mine(self):
        books = request.env['library.book'].search([
            ('author_ids', 'in', request.env.user.partner_id.ids),
        ])
        html_result = '<html><body><ul>'
        for book in books:
            html_result += "<li> %s </li>" % book.name
        html_result += '</ul></body></html>'
        return html_result

    # Este ejemplo es servir a una página Web para mostrar un libro en específico con el ID
    # auth="none" que significa que no habrá validación de usuario.
    # type="http"  que el request será un html
    # Aca el "book_id" se pasa como un parametro
    # como : xx.xx.xx.xx:8069/my_library/book_details?book_id=1

    @http.route('/my_library/book_details', type='http', auth='none')
    def book_details(self, book_id):
        record = request.env['library.book'].sudo().browse(int(book_id))
        return u'<html><body><h1>%s</h1>Authors: %s' % (
            record.name, u', '.join(record.author_ids.mapped('name')) or 'none',
        )

    # Este ejemplo es servir a una página Web para mostrar un libro en específico con el ID
    # auth="none" que significa que no habrá validación de usuario.
    # type="http"  que el request será un html
    # Aca el "book_id" se pasa como un parametro en la url
    # como : xx.xx.xx.xx:8069/my_library/book_details/1

    @http.route("/my_library/book_details_inpath/<model('library.book'):book>", type='http', auth='none')
    def book_details_in_path(self, book):
        return self.book_details(book.id)

# Esta clase se crea como ejemplo para mostrar los recursos estáticos. ej una imagen
# La imagen se pone en la ruta /my_library/static/src/image/odoo.png
    @http.route('/demo_page', type='http', auth='none')
    def books(self):
        image_url = '/my_library/static/scr/image/odoo.png'
        html_result = """<html>
            <body>
                <img src="%s"/>
            </body>
        </html>""" % image_url
        return html_result


    @http.route(['/partners/<partner_id>'], type='http', auth="public", website=True)
    def partners_detail(self, partner_id, **post):
        _, partner_id = unslug(partner_id)
        if partner_id:
            partner_sudo = request.env['res.partner'].sudo().browse(partner_id)
            is_website_publisher = request.env['res.users'].has_group('website.group_website_publisher')
            if partner_sudo.exists() and (partner_sudo.website_published or is_website_publisher):
                values = {
                    'main_object': partner_sudo,
                    'partner': partner_sudo,
                    'edit_page': False
                }
                return request.render("website_partner.partner_page", values)
        return request.not_found()