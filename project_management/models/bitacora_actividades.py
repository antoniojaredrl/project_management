from odoo import models, fields, api, _

class BitacoraActividades(models.Model):
    _name='bitacora.actividades'
    _description='Bitacora de Actividades'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name="name"

    # Seccion: Relaciones
    sale_order_id = fields.Many2one(
        'sale.order',
        string="Orden de Venta",
        help="Orden de venta relacionada con la actividad a reportar.",
        tracking=True,
        related="task_id.sale_order_id"
    )

    project_id = fields.Many2one(
        'project.project',
        string="Proyecto",
        help="Proyecto relacionado con la actividad a reportar.",
        tracking=True,
        related="task_id.project_id"
    )

    task_id = fields.Many2one(
        'project.task',
        string="Tarea",
        help="Tarea relacionada con la actividad a reportar.",
        tracking=True,
    )

    # Seccion: Campos
    name = fields.Char(
        string="Identificador",
        default=lambda self: self.env['ir.sequence'].next_by_code('secuencia.bitacora') or '/',
        readonly=True,
    )

    cliente = fields.Many2one(
        'res.partner',
        string="Cliente",
        related="task_id.cliente",
    )


    # Datos Internos


    # Seccion: Métodos