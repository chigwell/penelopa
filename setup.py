from setuptools import setup, find_packages

setup(
    name='penelopa',
    version='0.0.30',
    author='Eugene Evstafev',
    author_email='chigwel@gmail.com',
    description='Penelopa: AI-driven codebase modifier using OpenAI GPT models',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/chigwell/penelopa',
    packages=find_packages(),
    install_requires=[
        'pathspec',
        'argparse',
        'pyyaml',
        'openai',
        'penelopa-dialog',
        'ProjectCodebaseToJsonl',
        'clarifyquestgen',
        'CodebaseLister',
        'mistralai',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'penelopa=penelopa.penelopa:main',
        ],
    },
)
