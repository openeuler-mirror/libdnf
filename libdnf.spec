%global libsolv_version 0.6.30-1
%global libmodulemd_version 1.6.1
%global dnf_conflict 3.7.1
%global swig_version 3.0.12

%bcond_with valgrind
%bcond_without python3
%bcond_without python2

%global _cmake_opts \\\
    -DENABLE_RHSM_SUPPORT=%{?with_rhsm:ON}%{!?with_rhsm:OFF} \\\
    %{nil}

Name:           libdnf
Version:        0.22.0
Release:        9
Summary:        Library providing simplified C and Python API to libsolv
License:        LGPLv2+
URL:            https://github.com/rpm-software-management/libdnf
Source0:        %{url}/archive/%{version}/%{name}-%{version}.tar.gz
Patch0001:      0001-Modify-solver_describe_decision-to-report-cleaned-RhBug1486749.patch
Patch0002:      0002-history-Fix-crash-in-TransactionItemaddReplacedBy.patch
Patch0003:      0003-swdb-create-persistent-WAL-files-RhBug1640235.patch
Patch0004:      0004-Relocate-ModuleContainer-save-hook-RhBug1632518.patch
Patch0005:      0005-Test-if-sack-is-present-and-run-save-module-persistor-RhBug1632518.patch

Patch6000:      Set-relevant-g_log-domain-handlers-instead-of-a-defa.patch
Patch6001:      Add-a-debug-argument-to-Librepolog-addHandler.patch
Patch6002:      Add-a-logdebug-argument-to-hawkey.Sack.patch

BuildRequires:  cmake gcc gcc-c++ libsolv-devel >= %{libsolv_version} pkgconfig(librepo) pkgconfig(check)
BuildRequires:  pkgconfig(gio-unix-2.0) >= 2.46.0 pkgconfig(gtk-doc) pkgconfig(sqlite3) pkgconfig(json-c)
BuildRequires:  rpm-devel >= 4.11.0 pkgconfig(cppunit) pkgconfig(smartcols)
BuildRequires:  pkgconfig(modulemd) >= %{libmodulemd_version} gettext gpgme-devel
Requires:       libmodulemd%{?_isa} >= %{libmodulemd_version}
Requires:       libsolv%{?_isa} >= %{libsolv_version}

%description
A Library providing simplified C and Python API to libsolv.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       libsolv-devel%{?_isa} >= %{libsolv_version}

%description devel
Development files for %{name}.

%if %{with python2}
%package -n python2-libdnf
%{?python_provide:%python_provide python2-%{name}}
Summary:        Python 2 bindings for the libdnf library.
Requires:       %{name}%{?_isa} = %{version}-%{release}
BuildRequires:  python2-devel swig >= %{swig_version}

%description -n python2-libdnf
Python 2 bindings for the libdnf library.
%endif

%package -n python3-libdnf
%{?python_provide:%python_provide python3-%{name}}
Summary:        Python 3 bindings for the libdnf library.
Requires:       %{name}%{?_isa} = %{version}-%{release}
BuildRequires:  python3-devel swig >= %{swig_version}

%description -n python3-libdnf
Python 3 bindings for the libdnf library.

%if %{with python2}
%package -n python2-hawkey
Summary:        Python 2 bindings for the hawkey library
%{?python_provide:%python_provide python2-hawkey}
BuildRequires:  python2-devel python2-nose
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       python2-%{name} = %{version}-%{release}
Conflicts:      python2-dnf < %{dnf_conflict}
Conflicts:      python-dnf < %{dnf_conflict}

%description -n python2-hawkey
Python 2 bindings for the hawkey library.
%endif

%package -n python3-hawkey
Summary:        Python 3 bindings for the hawkey library
%{?python_provide:%python_provide python3-hawkey}
BuildRequires:  python3-devel python3-nose
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       python3-%{name} = %{version}-%{release}
Conflicts:      python3-dnf < %{dnf_conflict}
Obsoletes:      platform-python-hawkey < %{version}-%{release}

%description -n python3-hawkey
Python 3 bindings for the hawkey library.

%prep
%autosetup -p1
%if %{with python2}
mkdir build-py2
%endif
mkdir build-py3

%build
%if %{with python2}
pushd build-py2
  %cmake -DPYTHON_DESIRED:FILEPATH=%{__python2} -DWITH_MAN=OFF ../ %{!?with_valgrind:-DDISABLE_VALGRIND=1} %{_cmake_opts}
  %make_build
popd
%endif

%if %{with python3}
pushd build-py3
  %cmake -DPYTHON_DESIRED:FILEPATH=%{__python3} -DWITH_GIR=0 -DWITH_MAN=0 -Dgtkdoc=0 ../ %{!?with_valgrind:-DDISABLE_VALGRIND=1} %{_cmake_opts}
  %make_build
popd
%endif

%check
if [ "$(id -u)" == "0" ] ; then
        cat <<ERROR 1>&2
Package tests cannot be run under superuser account.
Please build the package as non-root user.
ERROR
        exit 1
fi

%if %{with python2}
pushd build-py2
  make ARGS="-V" test
popd
%endif
pushd build-py3/python/hawkey/tests
  make ARGS="-V" test
popd

%install
%if %{with python2}
pushd build-py2
  %make_install
popd
%endif
pushd build-py3
  %make_install
popd

%find_lang %{name}

%ldconfig_scriptlets

%files -f %{name}.lang
%license COPYING AUTHORS
%doc README.md
%doc %{_datadir}/gtk-doc/html/%{name}/
%{_libdir}/%{name}.so.*

%files devel
%{_libdir}/%{name}.so
%{_libdir}/pkgconfig/%{name}.pc
%{_includedir}/%{name}/

%if %{with python2}
%files -n python2-%{name}
%{python2_sitearch}/%{name}/
%endif

%files -n python3-%{name}
%{python3_sitearch}/%{name}/

%if %{with python2}
%files -n python2-hawkey
%{python2_sitearch}/hawkey/
%endif

%files -n python3-hawkey
%{python3_sitearch}/hawkey/

%changelog
* Sat Dec 21 2019 openEuler Buildteam <buildteam@openeuler.org> - 0.22.0-9
- Not log DEBUG messages by default (RhBug:1355764)

* Sat Nov 9 2019 openEuler Buildteam <buildteam@openeuler.org> - 0.22.0-8
- Type:bugfix
- Id:NA
- SUG:NA
- DESC:add the release

* Wed Sep 18 2019 openEuler Buildteam <buildteam@openeuler.org> - 0.22.0-7
- Package init
