import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    long_description = f.read()

setup(
    name='texoid',
    version='0.2.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'texoid = texoid.main:main',
        ]
    },
    install_requires=['tornado'],
    extras_require={
        'test': ['requests'],
    },

    author='Quantum',
    author_email='quantum@dmoj.ca',
    url='https://github.com/DMOJ/texoid',
    description='LaTeX math rendering server.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Artistic Software',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Topic :: Software Development',
    ],
)
