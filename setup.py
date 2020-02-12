from setuptools import setup, find_packages

setup(
    name="twitter_nlp_ONS",
    version="0.1.0",
    packages=find_packages(exclude=['*tests']),
    install_requires=['numpy', 'matplotlib'],
    # author='Nisha Lad',
    # author_email='nisha.lad.13@ucl.ac.uk',
    # license='Copyright (c) 2019 Nisha Lad',
    # description='Python travelplanner package',
    # long_description=open('README.md').read(),
    # entry_points={
    #     'console_scripts': [
    #         'bussimula = travelplanner.command:process'
    #     ]}
)