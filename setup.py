from setuptools import setup, find_packages

requires = [
    'python-arango',
    'marshmallow'
]

setup(
    name='arango-orm',
    version='0.1',
    description='A SQLAlchemy like ORM implementation for arangodb',
    long_description="A SQLAlchemy like ORM implementation using python-arango as the backend library",
    classifiers=[
        "Programming Language :: Python"
    ],
    author='Kashif Iftikhar',
    author_email='kashif@compulife.com.pk',
    url="https://github.com/threatify/arango-orm",
    license="GNU General Public License v3 (GPLv3)",
    keywords='arangodb orm python',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires
)
