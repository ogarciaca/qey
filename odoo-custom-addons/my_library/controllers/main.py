# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

"""
class Main(http.Controller):
    @http.route('/books', type='http', auth="none", website=True)
    def library_books(self):
        return request.render(
            'my_library.books', {
                'books': request.env['library.book'].search([]),
            })
"""
# @http.route tiene varios parametros
#     el primer parametro es la ruta donde estan los modelos. Pueden poner varios path separados por coma(,)
#      '/path1','/path2'
#       El parametro "type" (default = http) determina que tipo de respueta dar. tambuen puede ser json
#       CUnado es type='hhtp' indica a odoo que devuelva un string en formato HTML
#        
class Main(http.Controller):
    @http.route('/books', type='http', auth='none' )
    def books(self):
        books = request.env['library.book'].sudo().search([])
        html_result = '<html><body><ul>'
        for book in books:
            html_result += "<li> %s </li>" % book.name
        html_result += '</ul></body></html>'
        return html_result

    @http.route('/books/json', type='json', auth='none')
    def books_json(self):
        records = request.env['library.book'].sudo().search([])
        return records.read(['name'])