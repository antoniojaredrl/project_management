from odoo import models, fields, api, _


class InheritProjectTask(models.Model):
    """Extiende tareas de proyecto con control operativo de obra y avance."""

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
        domain="[('category_id.name', '=', 'Cliente')]",
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
        domain="[('category_id.name', '=', 'Supervisor')]",
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

    cantidad_sol = fields.Float(
        string="Cantidad Solicitada",
        help="Cantidad solicitada a ejecutar dentro de la actividad.",
        tracking=True,
        digits="Product Unit",
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
    bitacora_actividad_ids = fields.One2many(
        'bitacora.actividades',
        'task_id',
        string="Avances de Bitacora",
    )

    cantidad_entregada = fields.Float(
        string="Cantidad Entregada",
        help="Cantidad entregada dentro de la actividad.",
        compute="_compute_avance_bitacora",
        store=True,
    )

    progreso_ava = fields.Float(
        string="Progreso Ejecucion",
        help="Progreso entregado en base a lo solicitado.",
        compute="_compute_avance_bitacora",
        store=True,
    )

    cantidad_pendiente = fields.Float(
        string="Cantidad Pendiente",
        help="Cantidad pendiente por entregar en base a la cantidad solicitada y avances confirmados.",
        compute="_compute_avance_bitacora",
        store=True,
    )

    tarea_terminada = fields.Boolean(
        string="Tarea Terminada",
        compute="_compute_avance_bitacora",
        store=True,
        default=False,
    )

    #Seccion: Metodos

    # Método para calcular el valor total de una actividad a realizar.
    @api.depends('cantidad_sol','valor_uni')
    def _calcular_valor_total(self):
        for record in self:
            record.valor_total = record.cantidad_sol * record.valor_uni

    @api.depends(
        'cantidad_sol',
        'bitacora_actividad_ids.cantidad_avance',
        'bitacora_actividad_ids.bitacora_id.state',
    )
    def _compute_avance_bitacora(self):
        """Consolida avance oficial desde lineas de bitacora confirmadas."""
        for record in self:
            cantidad_entregada = sum(
                record.bitacora_actividad_ids.filtered(
                    lambda line: line.bitacora_id.state == 'confirmed'
                ).mapped('cantidad_avance')
            )
            record.cantidad_entregada = cantidad_entregada
            record.cantidad_pendiente = max((record.cantidad_sol or 0.0) - cantidad_entregada, 0.0)
            record.progreso_ava = (cantidad_entregada / record.cantidad_sol) * 100 if record.cantidad_sol else 0.0
            record.tarea_terminada = bool(record.cantidad_sol and cantidad_entregada >= record.cantidad_sol)

    def _get_bitacora_done_stage(self):
        """Obtiene o crea la etapa cerrada usada al completar la tarea por avance."""
        self.ensure_one()
        if not self.project_id:
            return False

        Stage = self.env['project.task.type']
        domain = [('project_ids', '=', self.project_id.id)]
        stage = Stage.search(domain + [('name', '=ilike', 'Listo')], limit=1)
        if not stage:
            stage = Stage.search(domain + [('name', '=ilike', 'Done')], limit=1)
        if not stage:
            stage = Stage.search(domain + [('fold', '=', True)], order='sequence, id', limit=1)
        if not stage:
            stage = Stage.create({
                'name': 'Listo',
                'sequence': 100,
                'fold': True,
                'project_ids': [(4, self.project_id.id)],
            })
        return stage

    def _sync_bitacora_completion(self):
        """Sincroniza estado de cierre segun avance confirmado."""
        for record in self:
            if not record.cantidad_sol:
                continue

            cantidad_entregada = sum(
                record.bitacora_actividad_ids.filtered(
                    lambda line: line.bitacora_id.state == 'confirmed'
                ).mapped('cantidad_avance')
            )
            if cantidad_entregada < record.cantidad_sol:
                if record.state == '1_done':
                    record.write({'state': '01_in_progress'})
                continue

            vals = {'state': '1_done'}
            stage = record._get_bitacora_done_stage()
            if stage:
                vals['stage_id'] = stage.id
            record.write(vals)
