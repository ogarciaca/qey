from re import X
from . import models 
from . import controllers 
from . import wizard
from . import security 

from odoo import api, fields, SUPERUSER_ID

"""
En el archivo __manifest__.py esta el llamado al metodo "def add_book_hook"
Con la linea 
        'post_init_hook': 'add_book_hook'

Tambien existen, adicional al "post_init_hook" los siguientes hooks

pre_init_hook  --> Para ejecutar acciones antes de instalar o actualizar el modelo
Uninsstall_hook --> Para cuando deseas desintalar el modelo y quieres elimnar los datos de la instalaccion

Todos van acompañado del nombre del método que hara la ejecucion.

"""
def add_book_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    book_data1 = {'name': 'Book 1 desde hook', 'date_release': fields.Date.today()}
    book_data2 = {'name': 'Book 2 desde hook', 'date_release': fields.Date.today()}
    env['library.book'].create([book_data1, book_data2])
