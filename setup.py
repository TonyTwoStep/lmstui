#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
	name="LMStui",
	version="0.0.1",
	package_dir={'':'src'},
	packages=find_packages( 'src'),
	python_requires=">=3.4.0",
	install_requires=['requests','asciimatics>=1.11.0'],
	scripts=['src/lmstui.py'],
	data_files=[
		('config', ['config/lmstui.conf.dist'])
		],
	author="R.S.U.",
	description="LMS TUI Remote",
	license="GPL v3",
	url="https://www.nexus0.net/pub/sw/lmstui",

)
