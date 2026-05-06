from odoo import models, fields, api, _
from datetime import datetime


class InheritProjectTask(models.Model):
    _inherit='project.task'

    #Seccion: Campos 
    es_tarea_obra = fields.Boolean(
        string="Es tarea de Obra",
        help="Muestra si una tarea sera parte de un proceso de obra o no.",
        default=False,
    )

    # Datos Generales:
    fecha_creacion = fields.Datetime(
        string="Fecha de Creación",
        default=lambda self: fields.Datetime.now(),
        readonly=True,
    )

    cliente = fields.Many2one(
        'res.partner',
        string="Cliente",
        help="Cliente al que se le realizara la actividad.",
        domain="[('category_id', '=', 'Cliente')]",
        tracking=True,
    )

    disciplina = fields.Many2one(
        'disciplina.obra',
        string="Disciplina",
        help="Disciplina a la que pertenece la actividad.",
        tracking=True,
    )

    planta = fields.Many2one(
        'plantas.obra',
        string="Planta",
        help="Planta donde se ejecutara la actividad.",
        tracking=True,
    )

    area_trabajo = fields.Char(
        string="Area de Trabajo",
        help="Area de trabajo de la actividad o Tag del equipo.",
        tracking=True,
    )

    licencia_om = fields.Char(
        string="Licencia/OM",
        tracking=True,
    )

    supervisor_int = fields.Many2one(
        'hr.employee',
        string="Supervisor Interno",
        help="Supervisor Interno de la actividad. (AYASA)",
        tracking=True,
    )

    supervisor_ext = fields.Many2one(
        'res.partner',
        string="Supervisor Cliente",
        help="Supervisor Externo de la actividad. (Cliente)",
        domain="[('category_id', '=', 'Supervisor')]",
        tracking=True,
    )

    # Ejecución Operativa
    producto = fields.Many2one(
        'product.template',
        string="Producto",
        help="Producto relacionado a la actividad.",
        tracking=True,
        domain="[('type', '=', 'service'), ('sale_ok', '=',True)]"
    )

    cantidad_sol = fields.Integer(
        string="Cantidad Solicitada",
        help="Cantidad solicitada a ejecutar dentro de la actividad.",
        tracking=True,
    )

    valor_uni = fields.Float(
        string="Valor Unitario",
        help="Valor unitario del producto relacionado a la actividad (Esta valor es sin IVA).",
        tracking=True,
        related="producto.list_price",
    )

    valor_total = fields.Float(
        string="Valor Total",
        help="Valor total en base a la cantidad solicitada y su precio unitario.",
        compute="_calcular_valor_total",
    )

    # Avance
    cantidad_entregada = fields.Float(
        string="Cantidad Entregada",
        help="Cantidad entregada dentro de la actividad.",
    )

    progreso_ava = fields.Float(
        string="Progreso Ejecución",
        help="Progreso entregado en base a lo solicitado."
    )

    tarea_terminada = fields.Boolean(
        string="Tarea Terminada",
        default=False,
    )


    #Seccion: Metodos

    # Método para calcular el valor total de una actividad a realizar.
    @api.depends('cantidad_sol','valor_uni')
    def _calcular_valor_total(self):
        for record in self:
            record.valor_total = record.cantidad_sol * record.valor_uni