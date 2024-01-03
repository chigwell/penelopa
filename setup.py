from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='penelopa',
    version='0.0.1',
    description='Placeholder for Penelopa project.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Eugene Evstafev',
    author_email='chigwel@gmail.com',
    url='https://github.com/chigwell/penelopa',
    packages=find_packages(),
    install_requires=[
    ],
)
