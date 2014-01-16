import os

from setuptools import setup, find_packages

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setup(
    name='ezstruct',
    version='0.1.0',
    description='Expressive syntax for working with binary data formats and network protocols.',
    long_description=(read('README.rst') + '\n\n' +
                      read('doc/HISTORY.rst') + '\n\n' +
                      read('doc/AUTHORS.rst')),
    url='http://github.com/matthewg/EzStruct/',
    license='Apache',
    author='Matthew Sachs',
    author_email='matthewg@zevils.com',
    packages=find_packages(exclude=['tests*']),
    include_package_data=False,
    install_requires=['six'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
