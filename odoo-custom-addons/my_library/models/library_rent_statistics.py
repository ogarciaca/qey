# -*- coding: utf-8 -*-
from odoo import models, api, fields, tools


class LibraryBookRentStatistics(models.Model):
    _name = 'library.book.rent.statistics'
    _auto = False

    book_id = fields.Many2one('library.book', 'Book', readonly=True)
    rent_count = fields.Integer(string="Times borrowed", readonly=True)
    average_occupation = fields.Integer(string="Average Occupation (DAYS)", readonly=True)
    publisher = fields.Text(string="publisher_id", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = """
        CREATE OR REPLACE VIEW library_book_rent_statistics AS (
        SELECT
                min(lbr.id) as id,
                lbr.book_id as book_id,
                rp.name as publisher,
                count(lbr.id) as rent_count,
                avg((EXTRACT(epoch from age(return_date, rent_date)) / 86400))::int as average_occupation

            FROM
                library_book_rent AS lbr
            JOIN
                library_book as lb ON lb.id = lbr.book_id
            LEFT JOIN 
                res_partner rp ON rp.id = lb.publisher_id
            WHERE lbr.state = 'returned'
            GROUP BY lbr.book_id,rp.name
        );
        """
        self.env.cr.execute(query)
