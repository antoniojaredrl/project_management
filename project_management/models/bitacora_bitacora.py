from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BitacoraBitacora(models.Model):
    """Documento/cabecera de bitacora que agrupa avances de trabajo."""

    _name = 'bitacora.bitacora'
    _description = 'Bitacora de Trabajo'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"
    _order = "fecha desc, id desc"

    name = fields.Char(
        string="Bitacora",
        default="Nuevo",
        readonly=True,
        copy=False,
        tracking=True,
    )

    fecha = fields.Date(
        string="Fecha",
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )

    responsable_id = fields.Many2one(
        'res.users',
        string="Responsable de Captura",
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )

    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('confirmed', 'Confirmado'),
            ('cancel', 'Cancelado'),
        ],
        string="Estado",
        default='draft',
        required=True,
        tracking=True,
        copy=False,
    )

    observacion = fields.Text(
        string="Observacion General",
        tracking=True,
    )

    actividad_ids = fields.One2many(
        'bitacora.actividades',
        'bitacora_id',
        string="Lineas de Avance",
        copy=True,
    )

    line_count = fields.Integer(
        string="Avances",
        compute="_compute_line_count",
    )

    @api.depends('actividad_ids')
    def _compute_line_count(self):
        for record in self:
            record.line_count = len(record.actividad_ids)

    @api.model_create_multi
    def create(self, vals_list):
        """Asigna el folio de bitacora solo al guardar el registro."""
        for vals in vals_list:
            if vals.get('name', 'Nuevo') in ('Nuevo', '/'):
                vals['name'] = self.env['ir.sequence'].next_by_code('secuencia.bitacora.bitacora') or '/'
        return super().create(vals_list)

    def action_confirm(self):
        """Valida y oficializa los avances de la bitacora.

        Solo las bitacoras confirmadas impactan el avance acumulado de la
        tarea y la cantidad entregada de la linea de venta relacionada.
        """
        for record in self:
            if not record.actividad_ids:
                raise ValidationError(_("Agrega al menos una linea de avance antes de confirmar."))

            # Validacion minima por linea antes de considerar el avance como oficial.
            for line in record.actividad_ids:
                if not line.task_id:
                    raise ValidationError(_("La linea %s no tiene una tarea asignada.") % line.name)
                if line.cantidad_avance <= 0:
                    raise ValidationError(_("La linea %s debe tener una cantidad de avance mayor a cero.") % line.name)

            # Valida por tarea para cubrir varias lineas de la misma tarea en el mismo corte.
            for task in record.actividad_ids.mapped('task_id'):
                cantidad_previa = sum(self.env['bitacora.actividades'].search([
                    ('task_id', '=', task.id),
                    ('bitacora_id.state', '=', 'confirmed'),
                    ('bitacora_id', '!=', record.id),
                ]).mapped('cantidad_avance'))
                cantidad_actual = sum(record.actividad_ids.filtered(lambda line: line.task_id == task).mapped('cantidad_avance'))
                cantidad_total = task.cantidad_sol or 0.0

                if cantidad_total and cantidad_previa + cantidad_actual > cantidad_total:
                    raise ValidationError(
                        _("El avance acumulado de la tarea %(task)s excede la cantidad solicitada.")
                        % {'task': task.display_name}
                    )
        self.write({'state': 'confirmed'})
        # Al confirmarse, las tareas completas pasan a Listo/Hecho.
        self.actividad_ids.mapped('task_id')._sync_bitacora_completion()

    def action_draft(self):
        tasks = self.actividad_ids.mapped('task_id')
        self.write({'state': 'draft'})
        tasks._sync_bitacora_completion()

    def action_cancel(self):
        tasks = self.actividad_ids.mapped('task_id')
        self.write({'state': 'cancel'})
        tasks._sync_bitacora_completion()

    def action_view_actividades(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lineas de Avance',
            'res_model': 'bitacora.actividades',
            'view_mode': 'list,form',
            'domain': [('bitacora_id', '=', self.id)],
            'context': {'default_bitacora_id': self.id},
        }
