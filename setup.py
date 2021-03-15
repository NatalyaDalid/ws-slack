import setuptools
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='ws-slack',
    version='0.0.1',
    url='https://github.com/whitesource-ps/ws-slack',
    license='LICENSE.txt',
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=open('requirements.txt').read().splitlines(),
    author="WhiteSource Professional Services",
    author_email="ps@whitesourcesoftware.com",
    description='WS Slack integration',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
