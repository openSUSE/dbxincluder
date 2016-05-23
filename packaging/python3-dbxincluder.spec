#
# spec file for package python3-dbxincluder
#
# Copyright (c) 2016 SUSE LINUX GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#


%define binname dbxincluder
Name:           python3-dbxincluder
Version:        0
Release:        0
Summary:        XInclude and DocBook Transclusion preprocessor
License:        GPL-3.0+
Group:          Productivity/Publishing/XML
Url:            https://github.com/openSUSE/dbxincluder
Source:         %{name}-%{version}.tar.xz
BuildRequires:  python3-Sphinx
BuildRequires:  python3-docopt
BuildRequires:  python3-lxml
Requires:       python3-docopt
Requires:       python3-lxml
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch

%description
dbxincluder is an implementation of the XInclude 1.1 specification (https://www.w3.org/TR/xinclude-11)
with support for DocBook transclusion (http://docbook.org/docs/transclusion).

%prep
%setup -q

%build
python3 setup.py build
make %{?_smp_mflags} -C doc man

%install
python3 setup.py install --prefix=%{_prefix} --root=%{buildroot} --install-data=%{_datadir}/%{name}
install -D -m644 -t %{buildroot}%{_mandir}/man1/ doc/_build/man/%{binname}.1

%files
%defattr(-,root,root)
%doc LICENSE
%{python3_sitelib}/*
%{_bindir}/%{binname}
%{_mandir}/man1/*

%changelog
%changelog
