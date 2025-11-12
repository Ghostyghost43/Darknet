#!/usr/bin/env python3
"""
Darknet - Advanced Wireless Security Framework
A comprehensive tool for wireless penetration testing and defense
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='darknet-wireless',
    version='1.0.0',
    author='Darknet Team',
    author_email='info@darknet-wireless.local',
    description='Advanced Wireless Security Framework for Red and Blue Teams',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/codypratt88/Darknet',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Topic :: Security',
        'Topic :: System :: Networking',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: POSIX :: Linux',
    ],
    python_requires='>=3.8',
    install_requires=[
        'scapy>=2.5.0',
        'pyshark>=0.6',
        'netaddr>=0.10.1',
        'click>=8.1.0',
        'colorama>=0.4.6',
        'rich>=13.7.0',
        'prompt-toolkit>=3.0.43',
        'pyyaml>=6.0.1',
        'python-dotenv>=1.0.0',
        'cryptography>=41.0.0',
        'pycryptodome>=3.19.0',
        'psutil>=5.9.0',
        'tabulate>=0.9.0',
        'pandas>=2.1.0',
        'numpy>=1.26.0',
        'requests>=2.31.0',
        'tqdm>=4.66.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'pytest-asyncio>=0.21.0',
            'black>=23.0.0',
            'flake8>=6.1.0',
            'pylint>=3.0.0',
        ],
        'web': [
            'flask>=3.0.0',
            'flask-socketio>=5.3.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'darknet=darknet.cli:main',
            'darknet-console=darknet.console:interactive',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
