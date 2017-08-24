import ast
import re

from setuptools import setup, find_packages


_version_re = re.compile(r'__version__\s+=\s+(.*)')


with open('vhbbtools/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(f.read().decode('utf-8')).group(1)))


setup(
    name='vhbbtools',
    version=version,
    description='A Python package for CMS physics analyses using VHiggsBB ntuples.',
    url='https://github.com/swang373/vhbbtools',
    download_url='https://github.com/swang373/vhbbtools/tarball/0.1.0.a0',
    author='Sean-Jiun Wang',
    author_email='sean.jiun.wang@gmail.com',
    license='MIT',
    packages=find_packages(),
    python_requires='>=2.7, <=3',
    install_requires=[
        'appdirs',
        'dill',
        'jinja2',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Physics',
    ],
)

