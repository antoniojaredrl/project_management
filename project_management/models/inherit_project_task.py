from odoo import models, fields, api, _

class InheritProjectTask(models.Model):
    _inherit='project.task'

    #Seccion: Campos 
    es_tarea_obra = fields.Boolean(
        string="Es tarea de Obra",
        help="Muestra si una tarea sera parte de un proceso de obra o no.",
        default=False,
    )

    # Datos Generales:
    cliente = fields.Many2one(
        'res.partner',
        string="Cliente",
        help="Cliente al que se le realizara la actividad.",
        domain="[('category_id', '=', 'Cliente')]"
    )

    planta = fields.Many2one(
        'plantas.obra',
        string="Planta",
        help="Planta donde se ejecutara la actividad.",
    )

    

    #Seccion: Metodos