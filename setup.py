from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("server/requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name = 'copy-gdoc',
    version = '0.0.1',
    py_modules = ['server', 'cli', 'client'],
    packages = find_packages(),
    install_requires = [requirements],
    python_requires='>=3.10',
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    entry_points = '''
        [console_scripts]
        copy-gdoc=cli.copy_gdoc:main
    '''
)