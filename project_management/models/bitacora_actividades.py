from odoo import models, fields, api, _

class BitacoraActividades(models.Model):
    _name='bitacora.actividades'
    _description='Bitacora de Actividades'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name="name"

    #! Seccion: Relaciones
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
        domain="[('category_id', '=', 'Supervisor')]",
        related="task_id.supervisor_ext",
    )

    supervisor_ayasa = fields.Many2one(
        'hr.employee',
        string="Supervisor (AYASA)",
        tracking=True,
        related="task_id.supervisor_int",
    )

    #! Seccion: Metodos

    # El metodo create() se ejecuta automaticamente al guardar un nuevo registro.
    # Odoo puede recibir un diccionario (1 registro) o una lista de diccionarios (varios).
    # Si el campo 'name' esta vacio, se genera el secuencial solo al momento de guardar.
    # Esto evita consumir numeros de secuencia cuando se cancela la creacion del registro.
    def create(self, vals_list):
        # Verificar si es una lista (multiples registros) o un diccionario (un solo registro)
        if isinstance(vals_list, list):
            # Iterar sobre cada registro en la lista
            for vals in vals_list:
                if not vals.get('name'):
                    # Obtener el siguiente numero de secuencia (ej: BAC-0001)
                    #Solo se consume aqui, al guardar en la base de datos
                    vals['name'] = self.env['ir.sequence'].next_by_code('secuencia.bitacora') or '/'
        else:
            # Un solo registro
            if not vals_list.get('name'):
                vals_list['name'] = self.env['ir.sequence'].next_by_code('secuencia.bitacora') or '/'
        # Llamar al metodo original de la clase padre para crear el registro
        return super().create(vals_list)