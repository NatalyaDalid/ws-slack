import setuptools

with open("../README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wss_sdk",
    version="0.0.1",
    author="WS PS",
    author_email="oz.tamari@whitesourcesoftware.com",
    description="WS Python SDK",
    scripts=['web/web'],
    url='http://pypi.python.org/pypi/PackageName/',
    license='LICENSE.txt',
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    long_description=open("../README.md").read(),
    install_requires=[],
)
