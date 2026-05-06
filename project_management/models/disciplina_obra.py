from odoo import models, fields, api, _

class DisciplinaObra(models.Model):
    _name='disciplina.obra'
    _description=""
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name="nombre_disciplina"


    # Seccion: Relaciones

    # Seccion: Campos
    nombre_disciplina = fields.Char(
        string="Disciplina",
        help="Debera especificar el nombre de la disciplina.",
        tracking=True,
    )
    # Seccion: Metodos