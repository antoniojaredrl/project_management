from odoo import api, fields, models


class SaleOrderLine(models.Model):
    """Sincroniza la cantidad entregada de venta con avances de obra."""

    _inherit = 'sale.order.line'

    obra_task_ids = fields.One2many(
        'project.task',
        'sale_line_id',
        string="Tareas de Obra",
    )

    @api.depends(
        'qty_delivered_method',
        'analytic_line_ids.so_line',
        'analytic_line_ids.unit_amount',
        'analytic_line_ids.product_uom_id',
        'obra_task_ids.bitacora_actividad_ids',
        'obra_task_ids.cantidad_entregada',
    )
    def _compute_qty_delivered(self):
        """Usa avance confirmado de tareas de obra como cantidad entregada.

        Las lineas sin tareas de bitacora conservan la logica estandar de Odoo.
        """
        obra_lines = self.filtered(lambda line: any(line.obra_task_ids.mapped('bitacora_actividad_ids')))
        super(SaleOrderLine, self - obra_lines)._compute_qty_delivered()

        for line in obra_lines:
            line.qty_delivered = sum(
                line.obra_task_ids.filtered(lambda task: task.bitacora_actividad_ids).mapped('cantidad_entregada')
            )
