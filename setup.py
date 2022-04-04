from setuptools import setup, find_namespace_packages

setup(
    name='company_invoices',
    packages=find_namespace_packages(include=['company_invoices', 'tests']),
    install_requires=[
                       'chargebee>=2,<3',
                       'pysqlite3-binary>=0.4.6,<1',
                       'SQLAlchemy>=1.4.25, <2'
                      ],
    test_suite='tests',
)
