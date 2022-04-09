# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _
from odoo.tests.common import Form

logger = logging.getLogger(__name__)

"""
_name --> Nombre de la tabla en la base de datos.
_description --> Descripcion larga del uso de la tabla y su contenido. Lo llaman la descripción del modelo.
_rec_name --> Para poner el título del campo o regristro.
_order  --> El orden en que los campos son mostrados. Es igual a un "order by"

"""

# Clase que se crea para el ejemplod e herencia abstracta
# Se pasa como parametro a la nueva clase models.AbstractModel para diferenciarlos de las otras clases (modelos)
#


class BaseArchive(models.AbstractModel):
    _name = 'base.archive'
    _description = 'Abstract Archive'

    active = fields.Boolean(default=True)

    def do_archive(self):
        for record in self:
            record.active = not record.active


# creación o modificación del modelo "library.book"
class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _inherit = ['base.archive']
    _order = 'date_release desc, name'

    name = fields.Char('Title', required=True, index=True)
    isbn = fields.Char('ISBN')
    id = fields.Integer('id', readonly=True)
    short_name = fields.Char('Short Title', translate=True, index=True)
    notes = fields.Text('Internal Notes')
    state = fields.Selection(
        [('draft', 'Not Available'),
         ('available', 'Available'),
         ('borrowed', 'Borrowed'),
         ('lost', 'Lost')],
        'State', default="draft")
    description = fields.Html('Description', sanitize=True, strip_style=False)
    cover = fields.Binary('Book Cover')
    out_of_print = fields.Boolean('Out of Print?')
    date_release = fields.Date('Release Date')
    date_updated = fields.Datetime('Last Updated', copy=False)
    pages = fields.Integer('Number of Pages',
                           groups='base.group_user',
                           states={'lost': [('readonly', True)]},
                           help='Total book page count',
                           company_dependent=False
                           )
    reader_rating = fields.Float(
        'Reader Average Rating',
        digits=(14, 4),  # Optional precision (total, decimals),
    )
    author_ids = fields.Many2many('res.partner', string='Authors')
    # Ver en Configuración--> Tecnica --> Precision Decimal.
    cost_price = fields.Float('Book Cost', digits='Book Price')
    # Esta relacionado con la tabla res_currency
    currency_id = fields.Many2one('res.currency', string='Currency')
    # optional attribute: currency_field='currency_id' incase currency field have another name then 'currency_id'
    retail_price = fields.Monetary('Retail Price')
    publisher_id = fields.Many2one('res.partner', string='Publisher',
                                   # optional:
                                   # Esto indica que pasa cuando el dato relacionado (publicador) es borrado. El capo queda nulo
                                   ondelete='set null',
                                   # "set null", "restrict" (no permite el borrado del publicador), "cascade" que hace borrado en cascada desde el publicador.
                                   context={},
                                   domain=[],
                                   # context= Para que cuando en la vista se haga clic en el campo aparezca el regisdtro relacionado
                                   # domain= Es un filtro que limita la busqueda en los regisdtros relacionados.
                                   )

    publisher_city = fields.Char(
        'Publisher City', related='publisher_id.city', readonly=True, copy=False)
    publisher_web = fields.Char(
        'Publisher Web', related='publisher_id.website', readonly=True, copy=False)
    category_id = fields.Many2one('library.book.category')
    age_days = fields.Float(
        string='Days Since Release',
        # Calcula los dias de acuerdo a la fecha del release.
        compute='_compute_age',
        # Para que calcule la fecha de release cambiando los dias.
        inverse='_inverse_age',
        search='_search_age',   # Como se activa la busqueda "_search_age", la descripcion en "string" aparecerá en el filtro de la pantalla como filtro personalizado. Si store=True no necesita el "search" porque se almacena en la base de datos y todo en base de datos se puede buscar
        store=False,
        # Se pone en true para que si hay un dato el cual el usuario no tiene permiso, lo pueda calcular
        compute_sudo=True,
    )
    ref_doc_id = fields.Reference(
        selection='_referencable_models', string='Reference Document')
    manager_remarks = fields.Text('Manager Remarks')
    old_edition = fields.Many2one('library.book', string='Old Edition')


    # Decorador que extiende la funcionalidad "create" y "write" c05.11
    @api.model
    def create(self, values):
        logger.info('values into manager_remarks : %s', values)
        # Se usa el metodo "user_has_groups" para determinar si pertenece al grupo
        grp=self.user_has_groups('my_library.group_librarian')
        logger.info('create metodo user_has_groups: %s', grp)
        if not self.user_has_groups('my_library.group_librarian'):
            if 'manager_remarks' in values:
                raise UserError(
                    'You are not allowed to modify '
                    'manager_remarks'
                )
        return super(LibraryBook, self).create(values)

    def write(self, values):
        """
        grp=self.user_has_groups('my_library.group_librarian')
        logger.info('write metodo user_has_groups: %s', grp)        
        logger.info('values into manager_remarks : %s', values)
        grp=self.env.ref('base.group_user')
        logger.info('write self.env.ref(base.group_user): %s', grp) 
        logger.info('base group name : %s', self.pool.get('res.users'))
        if not self.user_has_groups('my_library.group_librarian'):
            if 'manager_remarks' in values:
                raise UserError(
                    'You are not allowed to modify '
                    'manager_remarks'
                )
        """
        return super(LibraryBook, self).write(values)

    # Metodo de busqueda por diferentes campos. C05.12
    def name_get(self):
        result = []
        for book in self:
            authors = book.author_ids.mapped('name')
            name = '%s (%s)' % (book.name, ', '.join(authors))
            result.append((book.id, name))
        return result

    # Metodo de busqueda por diferentes campos. C05.12
    # el metodo "_name_search" es un estandar de odoo para buscar por el nombre del campo en que esta parado.
    # Pero se puede sobre-escribir (overwrite) el metodo de tal forma que incluyas otros campos de busqueda.
    # En el ejemplo, en el campo "old_edition" es Many2one contra la misma tabla "library_book". Pero con los campos que se pasan en "args" podra buscarse por isbn, author_name o short_name
    # la funcion "_name_search" se llama con campos Many2one o One2many y para encontrar registros en un CSV que se importa
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = [] if args is None else args.copy()
        if not(name == '' and operator == 'ilike'):
            args += ['|', '|', '|', '|',
                     ('name', operator, name),
                     ('isbn', operator, name),
                     ('author_ids.name', operator, name),
                     ('short_name', operator, name)
                     ]
        return super(LibraryBook, self)._name_search(
            name=name, args=args, operator=operator,
            limit=limit, name_get_uid=name_get_uid)

    @api.model      # Decorate
    def _referencable_models(self):
        models = self.env['ir.model'].search(
            [('field_id.name', '=', 'message_ids')])
        return [(x.model, x.name) for x in models]

    # Metodo que cambia el estado de los libros en transicion.. que estado le sigue al otro
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'available'),
                   ('available', 'borrowed'),
                   ('borrowed', 'available'),
                   ('available', 'lost'),
                   ('borrowed', 'lost'),
                   ('lost', 'available')]
        return (old_state, new_state) in allowed

    # Metodo que valida el cambio del estado de transicion.
    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state, new_state):
                book.state = new_state
            else:
                # continue
                # Esta es la forma de como enviar mensajes de Error al usuarios.
                # importar los odoo.exception, construir el mensaje (message=) y raise el mensaje.
                # Usa la funcion de nombre estraño _() para trasladar el mesanje a la Web en tiempo de ejecución por odoo.tools.translate
                message = _('Moving from %s to %s is not allowd') % (
                    book.state, new_state)
                raise UserError(message)

    # Metodo que cambia el estado de los libros.
    def make_available(self):
        self.change_state('available')

    def make_borrowed(self):
        self.change_state('borrowed')

    #def make_lost(self):
    #    self.change_state('lost')

    def make_lost(self):
        self.ensure_one()
        self.state = 'lost'
        if not self.env.context.get('avoid_deactivate'):
            self.active = False    

    def book_rent(self):
        self.ensure_one()
        if self.state != 'available':
            raise UserError(_('Book is not available for renting'))
        rent_as_superuser = self.env['library.book.rent'].sudo()
        rent_as_superuser.create({
            'book_id': self.id,
            'borrower_id': self.env.user.partner_id.id,
        })
    

    # El siguiente metodo es usado para traes un recorset vacio de library.member
    def log_all_library_members(self):
        # This is an empty recordset of model library.member
        library_member_model = self.env['library.member']
        all_members = library_member_model.search([])
        print("ALL MEMBERS:", all_members)
        return True

    # Metodo para crear un registro en la tabla "library_book_category" c05.4
    # Una vez creada la variabel Json, se crea el registro en base de datos usando self.env[<model>].create()
    # Los tipos de datos usados y su comparación con python
    #   Type    PythonType
    #   Text    String
    #   Float   float
    #   Integer Interger
    #   Boolean boolean
    #   Date    datetime.date
    #   Binary  encodebytes(bytestring)
    # (0,0,dictionary)  Tuple
    def create_categories(self):
        categ1 = {
            'name': 'Child category 1',
            'description': 'Description for child 1'
        }
        categ2 = {
            'name': 'Child category 2',
            'description': 'Description for child 2'
        }
        parent_category_val = {
            'name': 'Parent category',
            'description': 'Description for parent category',
            'child_ids': [
                (0, 0, categ1),
                (0, 0, categ2),
            ]
        }
        # Total 3 records (1 parent and 2 child) will be craeted in library.book.category model
        record = self.env['library.book.category'].create(parent_category_val)
        return True

    # Metodo para actualizar un campo c05.5
    # Este se dispara desde un boton
    def change_release_date(self):
        self.ensure_one()  # Este metodo se asegura que el recorset solo tenga un registro. De lo contrario se ira a una excepcion. No se quire que se actualice en todos los registros del recorset
        # En caso de querer actualizar todos los registros del recorset, se debe hacer un loop del recorset
        # Otra forma es usar el metodo self.update(val). Tambien para un solo registro. "val" debe tener la estructura {"date":fields.Datetime.now(),"otroscampos":"otros valores"}
        self.date_release = fields.Date.today()

    # Para para encontrar un registro. c05.6
    # Es necesario "import logging" y adicionar la linea "logger = logging.getLogger(__name__)"
    def find_book(self):
        domain = [
            '|',
            '&', ('name', 'ilike', 'Book Name'),
            ('category_id.name', '=', 'Category Name'),
            '&', ('name', 'ilike', 'Book Name 2'),
            ('category_id.name', '=', 'Category Name 2')
        ]
        #domain = [('name', 'ilike', 'todo')]
        #message = _(domain)
        #raise UserError(message)
        books = self.search(domain)
        # Esta instruccion agrega una linea en el log de odoo. puede usarse como logger.debug, looger.error, logger.warning, logger.critical y logger.info
        logger.info('Books found: %s', books)
        return True

    # Filter recordset
    # Filtrado de un recorset. c05.8
    def filter_books(self):
        all_books = self.search([])
        filtered_books = self.books_with_multiple_authors(all_books)
        logger.info('Filtered Books: %s', filtered_books)

    @api.model
    # Filtrado de un recorset. c05.8
    def books_with_multiple_authors(self, all_books):
        def predicate(book):
            if len(book.author_ids) > 1:
                return True
        return all_books.filtered(predicate)

    # Traversing recordset with mapped c05.9
    # Estos metodos es para traer la información reacionada en otras tablas.
    # Al metodo "get_author_names" se le pasa el recorset y devuelve los nombres de autor de todos los registros del recorset
    # Es importante revisar que en el view/xml hay un boton de accion que llama a la funcion "mapped_books"
    # Este metodo no es bueno en perfformance.. recomiendan search() o ejeccutando un SQL

    def mapped_books(self):
        all_books = self.search([])
        books_authors = self.get_author_names(all_books)
        logger.info('Books Authors: %s', books_authors)

    @api.model
    def get_author_names(self, all_books):
        return all_books.mapped('author_ids.name')

    # Sorting recordset c05.10
    # Este metodo es para ordernar los registros del recordset.
    # se llama la funcion "sort_books_by_date" pasando el recorset actual (sin filtro) y se imprime odoo.log el ordenamiento.
    # Es importante revisar que en el view/xml hay un boton de accion que llama a la funcion "sort_books"
    # Como se puede ver el ordenamiento se lleva a otro dataset
    # en la función "sorted" se puede pasar el argumento reverse=True
    # En caso en que la "sorted" no lleve argumentos, se ordenara por el atributo "_sort" del modelo que al final lo hace la base de datos.
    def sort_books(self):
        all_books = self.search([])
        books_sorted = self.sort_books_by_date(all_books)
        logger.info('Books before sorting: %s', all_books)
        logger.info('Books after sorting: %s', books_sorted)
        base_group = self.env.ref('base.group_user')
        logger.info('base.group_user : %s', base_group)
        g_librarian = self.user_has_groups('my_library.group_librarian')
        logger.info('g_librarian : %s', g_librarian)

    @api.model
    def sort_books_by_date(self, all_books):
        return all_books.sorted(key='date_release')

    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                delta = today - book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 0

    # This reverse method of _compute_age. Used to make age_days field editable
    # It is optional if you don't want to make compute field editable then you can remove this
    def _inverse_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            book.date_release = d

    # This used to enable search on compute fields
    # It is optional if you don't want to make enable search then you can remove this
    def _search_age(self, operator, value):
        today = fields.Date.today()
        value_days = timedelta(days=value)
        value_date = today - value_days
        # convert the operator:
        # book with age > value have a date < value_date
        operator_map = {
            '>': '<', '>=': '<=',
            '<': '>', '<=': '>=',
        }
        new_op = operator_map.get(operator, operator)
        return [('date_release', new_op, value_date)]

    def name_get(self):
        # This method used to customize display name of the record
        result = []
        for record in self:
            rec_name = "%s (%s)" % (record.name, record.date_release)
            result.append((record.id, rec_name))
        return result

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)', 'Book title must be unique.'),
        ('positive_page', 'CHECK(pages > 0)', 'No of pages must be positive')
    ]

    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError(
                    'Release date must be in the past')



    # Traer datos agrupados
    # Metodo para encontrar el costo promedio. C05.13
    # el metodo "grouped_data" es llamada desde un boton en la view "library_book.xml"  
    def grouped_data(self):
        data = self._get_average_cost()
        logger.info("Groupped Data %s" % data)  # imprime el dato de la agrupacion en el log
        #for data1 in data:
        #    if data1.category_id == self.category_id:
        #        logger.info("Groupped Data %s" % data1)  # imprime el dato de la agrupacion en el log

    @api.model
    # Metodo para encontrar el costo promedio. C05.13
    # la funcion "_get_average_cost" usa la funcion de odoo "read_group" el cual contiene : dominio, campos para accesar y agrupacion
    # dominio son las restricciones. en este ejemplo es que el costo "cost_price" tenga valor o no sea falso
    # campos para acceder : son los campos que traera la consulta. para este ejemplo traera la categoria "categori_id" y el promedio del costo "cost_price"
    # agrupacion : es por cual de los campos se agrupara.
    # select category_id,avg(cost_price) from library_boook group by category_id 
    #(
    def _get_average_cost(self):
        grouped_result = self.read_group(
            [('cost_price', "!=", False)], # Domain
            ['category_id', 'cost_price:avg'], # Fields to access
            ['category_id'] # group_by
            )
        return grouped_result   


    def average_book_occupation(self):
        self.flush()   # Para sincronizar los datos del cache (env) con los de la base de datos.
        sql_query = """
            SELECT
                lb.name,
                avg((EXTRACT(epoch from age(return_date, rent_date)) / 86400))::int
            FROM
                library_book_rent AS lbr
            JOIN
                library_book as lb ON lb.id = lbr.book_id
            WHERE lbr.state = 'returned'
            GROUP BY lb.name;"""
        self.env.cr.execute(sql_query)   # Ejecutar el query
        result = self.env.cr.fetchall() # traer los datos del query
        logger.info("Average book occupation: %s", result)

    def return_all_books(self):
        self.ensure_one()
        wizard = self.env['library.return.wizard']
        with Form(wizard) as return_form:
            return_form.borrower_id = self.env.user.partner_id
            record = return_form.save()
            record.books_returns()

         

# se crea un modelo en el que se pueda hacer la relacion de publicador One2Many (Un publicador tiene mas de un libro)
# Tambien que un libro tenga muchos autores y autores tengan muchos libros


class ResPartner(models.Model):
    _inherit = 'res.partner'

    published_book_ids = fields.One2many(
        'library.book', 'publisher_id', string='Published Books')
    authored_book_ids = fields.Many2many(
        'library.book',
        string='Authored Books',
        # relation='library_book_res_partner_rel'  # optional
    )
    count_books = fields.Integer(
        'Number of Authored Books', compute='_compute_count_books')

    @api.depends('authored_book_ids')
    def _compute_count_books(self):
        for r in self:
            r.count_books = len(r.authored_book_ids)

# Ejemplo de herencia usando DELEGACION el cual consiste en agregar campos a modelos existente pero que no
# que no dañan el modelo original.
# en este caso el modelo original es "res.partner" y el modelo nuevo "library.member"
# Crea una tabla con los nuevos campos con la llave de enlace "partner_id"
# recuerda que se usa la funcion _inherits con (s) al final que diferencia de la otra funcion _inherit


class LibraryMember(models.Model):
    _name = 'library.member'
    _inherits = {'res.partner': 'partner_id'}

    _description = 'Library Member'

    partner_id = fields.Many2one(
        'res.partner', required=True, ondelete='cascade')
    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date')
    member_number = fields.Char()
    date_of_birth = fields.Date('Date of birth')



class BookCategory(models.Model):
    _name = 'library.book.category'
    name = fields.Char('Category')
    description = fields.Text('Description')      
