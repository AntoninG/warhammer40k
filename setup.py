
from setuptools import setup, find_packages
from warhammer40k.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='warhammer40k',
    version=VERSION,
    description='Let me offer you MathHammer',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Antonin GUILET',
    author_email='antonin.guilet-dupont@laposte.net',
    url='https://github.com/AntoninG/warhammer40k',
    license='unlicensed',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'warhammer40k': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        warhammer40k = warhammer40k.main:main
    """,
)
