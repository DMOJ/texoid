from setuptools import setup

setup(
    name='texoid',
    version='0.1',
    packages=['texoid'],
    entry_points={
        'console_scripts': [
            'texoid = texoid.server:main',
        ]
    },
    install_requires=['tornado'],

    author='Xyene',
    author_email='xyene@dmoj.ca',
    url='https://github.com/DMOJ/texoid',
    description='LaTeX math rendering server.',
    classifiers=[
        'Development Status :: 3 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Education',
        'Topic :: Software Development',
    ],
)
