# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# DESCRIPTION
# This implements the 'bootimg-partition' source plugin class for
# 'wic'. The plugin creates an image of boot partition, copying over
# files listed in IMAGE_BOOT_FILES bitbake variable.
#
# AUTHORS
# Maciej Borzecki <maciej.borzecki (at] open-rnd.pl>
#

import os
import re

from wic import msger
from wic.pluginbase import SourcePlugin
from wic.utils.oe.misc import *

class BootimgPartitionPlugin(SourcePlugin):
    name = 'bootimg-partition'

    @classmethod
    def do_install_disk(self, disk, disk_name, cr, workdir, oe_builddir,
                        bootimg_dir, kernel_dir, native_sysroot):
        """
        Called after all partitions have been prepared and assembled into a
        disk image. Do nothing.
        """
        pass

    @classmethod
    def do_configure_partition(self, part, source_params, cr, cr_workdir,
                               oe_builddir, bootimg_dir, kernel_dir,
                               native_sysroot):
        """
        Called before do_prepare_partition(). Possibly prepare
        configuration files of some sort.

        """
        pass

    @classmethod
    def do_prepare_partition(self, part, source_params, cr, cr_workdir,
                             oe_builddir, bootimg_dir, kernel_dir,
                             rootfs_dir, native_sysroot):
        """
        Called to do the actual content population for a partition i.e. it
        'prepares' the partition to be incorporated into the image.
        In this case, does the following:
        - sets up a vfat partition
        - copies all files listed in IMAGE_BOOT_FILES variable
        """
        hdddir = "%s/boot" % cr_workdir
        rm_cmd = "rm -rf %s" % cr_workdir
        exec_cmd(rm_cmd)

        install_cmd = "install -d %s" % hdddir
        exec_cmd(install_cmd)

        msger.debug('Bootimg dir: %s' % bootimg_dir)
        img_deploy_dir = get_bitbake_var("DEPLOY_DIR_IMAGE")
        boot_files = get_bitbake_var("IMAGE_BOOT_FILES")

        if not boot_files:
            msger.error('No boot files defined, IMAGE_BOOT_FILES unset')

        msger.debug('Boot files: %s' % boot_files)

        # list of tuples (src_name, dst_name)
        deploy_files = []
        for src_entry in re.findall(r'[\w;\-\./]+', boot_files):
            if ';' in src_entry:
                dst_entry = tuple(src_entry.split(';'))
            else:
                dst_entry = (src_entry, src_entry)

            msger.debug('Destination entry: %r' % (dst_entry,))
            deploy_files.append(dst_entry)

        for deploy_entry in deploy_files:
            src, dst = deploy_entry
            src_path = os.path.join(img_deploy_dir, src)
            dst_path = os.path.join(hdddir, dst)

            msger.debug('Install %s as %s' % (os.path.basename(src_path),
                                              dst_path))
            install_cmd = "install -m 0644 -D %s %s" \
                          % (src_path, dst_path)
            exec_cmd(install_cmd)

        msger.debug('Prepare boot partition using rootfs in %s' % (hdddir))
        part.prepare_rootfs(cr_workdir, oe_builddir, hdddir,
                            native_sysroot)

