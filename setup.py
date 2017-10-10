import ast
import re

from setuptools import setup, find_packages


VERSION_RE = re.compile(r'__version__\s+=\s+(.*)')


with open('vhbbtools/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(VERSION_RE.search(f.read().decode('utf-8')).group(1)))


setup(
    name='vhbbtools',
    version=version,
    description='A Python package for CMS physics analyses using VHiggsBB ntuples.',
    url='https://github.com/swang373/vhbbtools',
    download_url='https://github.com/swang373/vhbbtools/tarball/{0}'.format(version),
    author='Sean-Jiun Wang',
    author_email='sean.jiun.wang@gmail.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=2.7, <3',
    install_requires=[
        'appdirs',
        'cached_property',
        'contextlib2',
        'dill',
        'futures',
        'jinja2',
        'rootpy>=1.0.0',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
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

