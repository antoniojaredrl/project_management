from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class BitacoraActividades(models.Model):
    """Linea operativa de avance capturada dentro de una bitacora."""

    _name='bitacora.actividades'
    _description='Bitacora de Actividades'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name="name"

    # Relaciones principales. La bitacora agrupa; la tarea define proyecto,
    # orden de venta, producto y datos base del trabajo.
    bitacora_id = fields.Many2one(
        'bitacora.bitacora',
        string="Bitacora",
        ondelete='cascade',
        tracking=True,
    )

    sale_order_id = fields.Many2one(
        'sale.order',
        string="Orden de Servicio",
        help="OS relacionada con la actividad a reportar.",
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

    #! Seccion: Campos
    name = fields.Char(
        string="Identificador",
        default="Nuevo",
        readonly=True,
    )

    cliente = fields.Many2one(
        'res.partner',
        string="Cliente",
        related="task_id.cliente",
        tracking=True,
    )

    especialidad_venta = fields.Many2many(
        'crm.tag',
        string="Especialidad OS",
        related="sale_order_id.tag_ids",
        tracking=True,
    )

    # Datos Generales
    oc_pedido = fields.Char(
        string="OC/Pedido",
        help="",
        tracking=True,
    )

    fecha_creacion = fields.Datetime(
        string="Fecha de Creación",
        default=lambda self: fields.Datetime.now(),
        readonly=True,
    )

    centro_trabajo = fields.Char(
        string="CT",
        help="Centro de trabajo donde se ejecuta la actividad a reportar.",
        tracking=True,
    )

    or_rfq = fields.Char(
        string="OR/RFQ",
        help="Solicitud de Cotización",
        tracking=True,
    )

    especialidad_trabajo = fields.Many2one(
        'disciplina.obra',
        string="Disciplina",
        related="task_id.disciplina",
        tracking=True,
    )
    
    no_cotizacion = fields.Char(
        string="No. Cotización",
        tracking=True,
    )

    # Descripción detallada del trabajo.
    hora_inicio = fields.Datetime(
        string="Hora Inicio",
        tracking=True,
        help="Inicio de la jornada de trabajo reportada en esta bitacora.",
    )

    hora_termino = fields.Datetime(
        string="Hora Término",
        tracking=True,
        help="Término de la jornada de trabajo reportada en esta bitacora.",
    )

    planta_trabajo = fields.Many2one(
        'plantas.obra',    
        string="Planta",
        related="task_id.planta",
        help="Planta donde se esta realizando el trabajo a reportar en esta bitacora.",
        tracking=True
    )

    licencia_om = fields.Char(
        string="Licencia/OM",
        help="Licencia proporcionada por el centro de trabajo para poder realizar el trabajo o avances reportado en esta bitacora.",
        tracking=True,
    )

    supervisor_cliente = fields.Many2one(
        'res.partner',
        string="Supervisor (CLIENTE)",
        tracking=True,
        domain="[('category_id.name', '=', 'Supervisor')]",
        related="task_id.supervisor_ext",
    )

    supervisor_ayasa = fields.Many2one(
        'hr.employee',
        string="Supervisor (AYASA)",
        tracking=True,
        related="task_id.supervisor_int",
    )

    sale_order_line_id = fields.Many2one(
        'sale.order.line',
        string="Linea de Venta",
        related="task_id.sale_line_id",
    )

    producto = fields.Many2one(
        'product.template',
        string="Producto",
        related="task_id.producto",
    )

    valor_unitario = fields.Float(
        string="Valor Unitario",
        related="task_id.valor_uni",
    )

    cantidad_total = fields.Float(
        string="Unidades a Entregar",
        compute="_compute_cantidades_avance",
        digits="Product Unit",
    )

    cantidad_anterior = fields.Float(
        string="Entregado Anterior",
        compute="_compute_cantidades_avance",
        digits="Product Unit",
    )

    cantidad_avance = fields.Float(
        string="Avance a Entregar",
        tracking=True,
        digits="Product Unit",
    )

    cantidad_acumulada = fields.Float(
        string="Entregado Acumulado",
        compute="_compute_cantidades_avance",
        digits="Product Unit",
    )

    porcentaje_avance = fields.Float(
        string="Avance Actual",
        compute="_compute_cantidades_avance",
        help="Valor en formato ratio para el widget percentage: 0.25 se muestra como 25%.",
    )

    importe_avance = fields.Float(
        string="Importe del Avance",
        compute="_compute_cantidades_avance",
    )

    @api.depends('task_id', 'task_id.cantidad_sol', 'cantidad_avance', 'bitacora_id.state')
    def _compute_cantidades_avance(self):
        """Calcula avance del corte y acumulados confirmados de la tarea.

        El avance anterior solo considera lineas de bitacoras confirmadas;
        una linea en borrador muestra una proyeccion sin afectar aun la tarea.
        """
        for record in self:
            cantidad_anterior = 0.0
            if record.task_id:
                domain = [
                    ('task_id', '=', record.task_id.id),
                    ('bitacora_id.state', '=', 'confirmed'),
                ]
                if record.id:
                    domain.append(('id', '!=', record.id))
                cantidad_anterior = sum(self.search(domain).mapped('cantidad_avance'))

            cantidad_total = float(record.task_id.cantidad_sol or 0.0)
            cantidad_acumulada = cantidad_anterior + (record.cantidad_avance or 0.0)

            record.cantidad_total = cantidad_total
            record.cantidad_anterior = cantidad_anterior
            record.cantidad_acumulada = cantidad_acumulada
            record.porcentaje_avance = (record.cantidad_avance / cantidad_total) if cantidad_total else 0.0
            record.importe_avance = (record.cantidad_avance or 0.0) * (record.valor_unitario or 0.0)

    @api.constrains('cantidad_avance')
    def _check_cantidad_avance(self):
        for record in self:
            if record.cantidad_avance < 0:
                raise ValidationError(_("Las unidades del avance no pueden ser negativas."))

    @api.model_create_multi
    def create(self, vals_list):
        """Asigna el folio de avance solo al guardar la linea."""
        for vals in vals_list:
            if vals.get('name', 'Nuevo') in ('Nuevo', '/'):
                vals['name'] = self.env['ir.sequence'].next_by_code('secuencia.bitacora.actividades') or '/'
        return super().create(vals_list)
