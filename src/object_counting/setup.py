from setuptools import find_packages, setup
import os
import sys

package_name = 'object_counting'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mrd42',
    maintainer_email='Michael.E.Wescott@Spiritaero.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'object_counting_node = object_counting.counting_node:main',
        ],
    },
    # Ensure generated console scripts use the active interpreter.
    options={'build_scripts': {'executable': sys.executable}},
)
