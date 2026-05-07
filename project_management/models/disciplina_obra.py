from odoo import models, fields, api, _

class DisciplinaObra(models.Model):
    _name='disciplina.obra'
    _description="Disciplina de obra"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name="nombre_disciplina"


    # Seccion: Relaciones
    tarea_relacionada = fields.One2many(
        'project.task',
        'disciplina',
        string="Tareas Relacionadas"
    )

    # Seccion: Campos
    nombre_disciplina = fields.Char(
        string="Disciplina",
        help="Debera especificar el nombre de la disciplina.",
        tracking=True,
    )

    cliente_rela = fields.Many2one(
        'res.partner',
        string="Cliente Rel.",
        help="Asigna un cliente a la disciplina.",
        domain="[('category_id.name', '=', 'Cliente')]",
        tracking=True,
    )

    # Seccion: Metodos
