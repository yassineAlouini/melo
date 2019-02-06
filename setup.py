from setuptools import find_packages, setup

NAME = 'melo'
VERSION = '0.1'
AUTHOR = 'Yassine Alouini'
DESCRIPTION = """A multiplayer ELO tracking system."""
EMAIL = "yassinealouini@outlook.com"
URL = ""
INSTALL_REQUIRES = ["elo", "pandas", "slacker", "emoji", "tabulate"]

setup(
    name=NAME,
    version=VERSION,
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(),
    # Some metadata
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    url=URL,
    license="MIT",
    keywords="ELO multi-player",
)
