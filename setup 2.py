from setuptools import setup, find_packages

setup(
    name="twitter_nlp_ONS",
    version="0.1.0",
    packages=find_packages(exclude=['*tests']),
    install_requires=['numpy', 'matplotlib', 'pandas', 'nltk'],
    author='Nisha Lad, Matthew Cheng, Johannes Heyl',
    author_email='nisha.lad.13@ucl.ac.uk, i.cheng.19@ucl.ac.uk, johannes.heyl.19@ucl.ac.uk',
    license='Copyright (c) 2020 N. Lad, M. Cheng, J. Heyl',
    description='NLP Analysis on Topical Twitter Data',
    long_description=open('README.md').read(),
    # entry_points={
    #     'console_scripts': [
    #         'bussimula = travelplanner.command:process'
    #     ]}
)
