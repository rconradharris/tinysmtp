from setuptools import setup


setup(
    name='tinysmtp',
    version='0.1.1',
    url='https://github.com/rconradharris/tinysmtp',
    license='BSD',
    author='Rick Harris',
    author_email='rconradharris@gmail.com',
    description='Basically Flask-Mail without the Flask part',
    long_description=__doc__,
    py_modules=['tinysmtp'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[''],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
