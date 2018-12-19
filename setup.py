from setuptools import setup

setup(
    name='texoid',
    version='0.2',
    packages=['texoid'],
    entry_points={
        'console_scripts': [
            'texoid = texoid.main:main',
        ]
    },
    install_requires=['tornado'],

    author='Quantum',
    author_email='quantum@dmoj.ca',
    url='https://github.com/DMOJ/texoid',
    description='LaTeX math rendering server.',
    classifiers=[
        'Development Status :: 3 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Education',
        'Topic :: Software Development',
    ],
)
