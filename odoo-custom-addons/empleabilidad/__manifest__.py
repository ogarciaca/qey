{
    'name' : 'Employee engagement',
    'version' : '1.0',
    'summary': 'Employee engagement software',
    'sequence': 10,
    'description': """Library Management Software - Employee engagement  Add-on in odoo""",
    'category': 'Human Resources/Employees',
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
    
    ],
    'data': ['views/empl_engage.xml'
            ,'views/empl_studies.xml'
            ,'views/candidate_skills.xml'
            ,'views/candidate_jobs.xml'
            ,'views/candidate_edus.xml'
            ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}