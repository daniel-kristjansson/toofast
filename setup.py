"""setup.py controls the build, testing, and distribution of the egg"""

from setuptools import setup, find_packages
import re
import sys
import os.path


VERSION_REGEX = re.compile(r"""
    ^__version__\s=\s
    ['"](?P<version>.*?)['"]
""", re.MULTILINE | re.VERBOSE)

VERSION_FILE = os.path.join("toofast", "version.py")


def get_version():
    """Reads the version from the package"""
    with open(VERSION_FILE) as handle:
        lines = handle.read()
        result = VERSION_REGEX.search(lines)
        if result:
            return result.groupdict()["version"]
        else:
            raise ValueError("Unable to determine __version__")


def get_requirements():
    """Reads the installation requirements from requirements.pip"""
    with open("requirements.pip") as f:
        lines = f.read().split("\n")
        lines_without_comments = filter(lambda l: not l.startswith('#'), lines)
        return lines_without_comments


setup(name='toofast',
    version=get_version(),
    description="Vehicle Speed Analysis",
    long_description="",
    # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Apache 2.0 License'
    ],
    keywords='',
    author='Daniel Thor Kristjansson',
    author_email='danielk@cuymedia.net',
    url='',
    license='APL',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    dependency_links=[
    ],
    scripts=[
    ],
    package_data={ "toofast": [] },
    install_requires=get_requirements(),
    test_suite = 'nose.collector',
    entry_points="""
        [paste.app_factory]
        main=toofast:main
    """,
)
