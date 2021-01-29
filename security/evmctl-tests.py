#!/usr/bin/env python
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.
#
# Copyright: 2021 IBM
# Author: Nageswara R Sastry <rnsastry@linux.vnet.ibm.com>

import os
from avocado import Test
from avocado.utils import archive, process
from avocado.utils.software_manager import SoftwareManager


class EvmCtl(Test):
    """
    evmctl-testsuite
    :avocado: tags=security,testsuite
    """
    def setUp(self):
        '''
        Install the basic packages to support evmctl
        '''
        # Check for basic utilities
        smm = SoftwareManager()
        deps = ['gcc', 'make']
        for package in deps:
            if not smm.check_installed(package) and not smm.install(package):
                self.cancel('%s is needed for the test to be run' % package)
        url = "https://sourceforge.net/projects/linux-ima/files/latest/download"
        tarball = self.fetch_asset(url, expire='7d')
        tarball_gz = "".join([tarball, ".tar.gz"])
        # Need to rename the download file as avocado API looks for tar.gz
        # extension to identify as a archive
        os.rename(tarball, tarball_gz)
        self.log.info("tarball name %s - %s" % (tarball, tarball_gz))
        archive.extract(tarball_gz, self.workdir)
        self.sourcedir = os.path.join(self.workdir, os.listdir(self.workdir)[0])
        self.log.info("sourcedir - %s" % self.sourcedir)
        os.chdir(self.sourcedir)
        process.run('./autogen.sh', ignore_status=True)

    def test(self):
        '''
        Running tests from evmctl
        '''
        count = 0
        output = process.system_output('./build.sh', ignore_status=True).decode()
        for line in output.splitlines():
            if '# FAIL' in line:
                count = line.split(":")[1].strip()
                self.log.info(line)
        # If the fail count is more than 0 then there are some failed tests
        if int(count) > 0:
            self.fail("%s test(s) failed, please refer to the log" % count)
