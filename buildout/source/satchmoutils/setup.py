from setuptools import setup, find_packages
import os


version = '0.1'


setup(
    name='satchmoutils',
    version=version,
    description="Generic utilities and addons for Satchmo",
    long_description=open("README.rst").read() + "\n" +
                     open(os.path.join("docs", "HISTORY.rst")).read(),
    # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
    ],
    keywords='',
    author='Biagio Grimaldi',
    author_email='biagio.grimaldi@abstract.it',
    url='https://github.com/abstract-open-solutions/satchmo-utils',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Django',
        'Satchmo',
    ]
)
