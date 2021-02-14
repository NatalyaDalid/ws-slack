import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ws_sdk",
    version="0.0.1",
    author="WS PS",
    author_email="oz.tamari@whitesourcesoftware.com",
    description="WS Python SDK",
    url='https://github.com/whitesource-ps/ws_sdk',
    license='LICENSE.txt',
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
