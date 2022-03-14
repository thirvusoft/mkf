from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in mk_fiber/__init__.py
from mk_fiber import __version__ as version

setup(
	name="mk_fiber",
	version=version,
	description="mk",
	author="mk",
	author_email="mk",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
