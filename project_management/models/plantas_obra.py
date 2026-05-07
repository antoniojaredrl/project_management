from odoo import models, fields, api, _

class PlantasObra(models.Model):
    _name='plantas.obra'
    _description='Planta donde se ejecuta la actividad.'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name="nombre_planta"

    # Seccion: Relaciones
    tarea_relacionada = fields.One2many(
        'project.task',
        'planta',
        string="Tareas Relacionadas"
    )

    # Seccion: Campos
    nombre_planta = fields.Char(
        string="Nombre de la Planta",
        help="Debera especificar el nombre de la planta relacionado a un cliente.",
        tracking=True,
    )

    cliente_rela = fields.Many2one(
        'res.partner',
        string="Cliente Rel.",
        help="Cliente relacionado a la planta.",
        domain="[('category_id.name', '=', 'Cliente')]",
        tracking=True,
    )

    # Seccion: Metodos
