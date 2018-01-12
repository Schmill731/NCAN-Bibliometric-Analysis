# Setup File for Python Module ncan-bib-assess
# Created by Billy Schmitt

from setuptools import setup

setup(name='ncan_bibrun',
      version='0.1',
      description='NCAN Bibliometric Assessment',
      url='https://github.com/Schmill731/NCAN-Bibliometric-Analysis',
      author='Billy Schmitt',
      author_email='williamschmitt@college.harvard.edu',
      license='NCAN',
      packages=['ncan_bibrun'],
      install_requires=['requests', 'xlsxwriter'],
      scripts=['bin/ncan-bibrun'],
      include_package_data=True,
      zip_safe=False)
