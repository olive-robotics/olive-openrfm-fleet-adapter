from setuptools import setup
import os
from glob import glob
package_name = 'olive_openrmf_fleet_adapter'

setup(
    name=package_name,
    version='0.0.2',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # ('share/' + package_name,['config.yaml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*.launch.py')),),
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*.yaml')),),

    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Samuel Hafner',
    maintainer_email='samuel@olive-robotics.com',
    description='Olive OpenRMF fleet adapter',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'fleet_adapter=olive_openrmf_fleet_adapter.fleet_adapter:main'
        ],
    },
)
