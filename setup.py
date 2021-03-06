#!/usr/bin/env python
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from setuptools import setup

version = "0.1.dev"

setup(
    name="periscope",
    version=version,
    packages=["periscope", "periscope.test"],
    package_data={},
    author="Ahmed El-Hassany",
    author_email="ahassany@indiana.edu",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    url="https://github.com/periscope-ps/periscope",
    description="Periscope is the implementation of both Unified Network Informatin Service (UNIS) and Measurement Store (MS).",
    include_package_data = True,
    
    install_requires=[
        "tornado",
        "pymongo",
        "asyncmongo",
        "unittest2",
        "netlogger>=4.3.0",
        "validictory>=validictory-0.8.1",
        "mock==0.8.0",
        "jsonpointer==0.2",
        "argparse",
        "httplib2",
        "jsonpath",
	"M2Crypto"
    ],
    dependency_links=[
        "http://github.com/ahassany/asyncmongo/tarball/getmore_ioloop#egg=asyncmongo-1.2.1",
    ],
    entry_points = {
        'console_scripts': [
            'periscoped = periscope.app:main',
        ]
    },
)
