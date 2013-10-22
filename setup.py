from distutils.core import setup

setup(
    name='NIF_WRF',
    version='0.1',
    packages=['NIF_WRF', 'NIF_WRF.DB', 'NIF_WRF.GUI', 'NIF_WRF.GUI.widgets', 'NIF_WRF.util', 'NIF_WRF.Analysis'],
    url='',
    license='MIT',
    author='Alex Zylstra',
    author_email='azylstra@psfc.mit.edu',
    description='NIF WRF analysis and database code'
)
