{
    'name' : 'Employee engagement',
    'version' : '1.0',
    'summary': 'Employee engagement software',
    'sequence': 10,
    'description': """Software de empleanbilidad - conectarse a empleos  Add-on in odoo""",
    'category': 'empleabilidad',
    'website': 'https://www.odoolibrary.tech',
    'version': '14.0.1',
    'depends': ['base','hr_skills','hr_recruitment',
        'hr',
        'calendar',
        'fetchmail',
        'utm',
        'attachment_indexation',
        'web_tour',
        'digest',
        'website_partner',
  
    ],
    'data': ['security/groups.xml'
            ,'views/empl_engage.xml'
            ,'views/empl_studies.xml'
            ,'views/candidate_skills.xml'
            ,'views/candidate_jobs.xml'
            ,'views/candidate_edus.xml'
            ,'views/vacant_skills.xml'
            ,'views/candidate_works.xml'
            ,'views/vacant_appls.xml'
            ,'views/works_template.xml'
            ,'views/candidate_templates.xml'
            ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}