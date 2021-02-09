import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wss_sdk",
    version="0.0.1",
    author="WSS PS",
    author_email="oz.tamari@whitesourcesoftware.com",
    description="WSS SDK",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
)
