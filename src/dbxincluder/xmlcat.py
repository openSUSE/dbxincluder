#
# Copyright (c) 2016 SUSE Linux GmbH
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#

"""xmlcat module: Provide xml-catalog lookups"""

import subprocess


XMLCAT_CACHE = {}


def xmlcatalog_lookup(url, catalog):
    """Run the xmlcatalog tool to lookup url in catalog.
    The code for xml catalogs in libxml2 is not exposed by lxml
    and python3 binding for libxml2 are not commonly available.

    :return: Either None on failure or a URL"""

    catalog = catalog if catalog else "/etc/xml/catalog"

    try:
        return subprocess.check_output(
            ["xmlcatalog", catalog, url], universal_newlines=True
        )
    except subprocess.CalledProcessError:
        return None


def lookup_url(url, catalog):
    """Looks up url in the xml catalog.
    Warning: This caches lookups, so if you lookup the same URL for different catalogs,
    the result will be the same."""

    try:
        return XMLCAT_CACHE[url]
    except KeyError:
        target = xmlcatalog_lookup(url, catalog)
        if target is None:
            target = url

        XMLCAT_CACHE[url] = target
        return XMLCAT_CACHE[url]
