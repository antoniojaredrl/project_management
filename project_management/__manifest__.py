{
    'name': "project_management",
    'summary': "Sistema de Administración de Proyectos",
    'description': """
    Modulo diseñado para la planeación e administración de las diferentes actividades a realizar.
    """,
    'author': "Antonio JRL.",
    'website': "",
    'category': 'personalized',
    'version': '19.0.0.1',

    'depends': ['base', 'mail', 'project', 'sale', 'sale_project','hr'],

    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/bitacora_views.xml',
        'views/bitacora_actividades_views.xml',
        'views/disciplina_obra_views.xml',
        'views/plantas_obra_views.xml',
        'views/inherit_project_task_views.xml',
        'views/menu_actions.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
