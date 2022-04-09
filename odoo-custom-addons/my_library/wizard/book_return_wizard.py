# -*- coding: utf-8 -*-
from odoo import models, fields, api


class LibraryReturnWizard(models.TransientModel):
    _name = 'library.return.wizard'
    _description = "Lib return wizard"

    borrower_id = fields.Many2one('res.partner', string='Member')
    book_ids = fields.Many2many('library.book', string='Books')

    def books_returns(self):
        loanModel = self.env['library.book.rent']
        for rec in self:
            loans = loanModel.search(
                [('state', '=', 'ongoing'),
                 ('book_id', 'in', rec.book_ids.ids),
                 ('borrower_id', '=', rec.borrower_id.id)]
            )
            for loan in loans:
                loan.book_return()

    @api.onchange('borrower_id')
    def onchange_member(self):
        rentModel = self.env['library.book.rent']
        # En la varibale rentModel se pasa el modelo library.book.rent (tabla library_book_rent)
        # Luego se busca en esa modelo (tabla) los que tengan el estado ongoing ('state', '=', 'ongoing') y ('borrower_id', '=', self.borrower_id.id)
        # 
        books_on_rent = rentModel.search(
            [('state', '=', 'ongoing'),
             ('borrower_id', '=', self.borrower_id.id)]
        )
        # Se mapean solo los id del lobro (book_id) y se pasan al conexto self que es lo que esta cargado 
        # en la memoria y la interface de usuario

        self.book_ids = books_on_rent.mapped('book_id')
