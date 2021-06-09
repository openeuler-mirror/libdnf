%global libsolv_version 0.7.7
%global libmodulemd_version 2.5.0
%global librepo_version 1.12.0
%global dnf_conflict 4.2.23
%global swig_version 3.0.12

%global requires_python2_sphinx python2-sphinx
%global requires_python3_sphinx python3-sphinx

%bcond_with valgrind
%bcond_without python3
%bcond_with python2
%bcond_with rhsm
%bcond_with zchunk
%bcond_with sanitizers

%global _cmake_opts \\\
    -DENABLE_RHSM_SUPPORT=%{?with_rhsm:ON}%{!?with_rhsm:OFF} \\\
    %{nil}

Name:                      libdnf
Version:                   0.48.0
Release:                   2
Summary:                   Library providing simplified C and Python API to libsolv
License:                   LGPLv2+
URL:                       https://github.com/rpm-software-management/libdnf
Source0:                   %{url}/archive/%{version}/%{name}-%{version}.tar.gz                    

Patch0:                    fix-python2-no-format-arguments-error.patch
Patch1:                    CVE-2021-3445.patch

BuildRequires:             cmake gcc gcc-c++ libsolv-devel >= %{libsolv_version} gettext
BuildRequires:             pkgconfig(librepo) >= %{librepo_version} pkgconfig(check)              
BuildRequires:             pkgconfig(gio-unix-2.0) >= 2.46.0 pkgconfig(gtk-doc) gpgme-devel
BuildRequires:             rpm-devel >= 4.11.0 pkgconfig(sqlite3) pkgconfig(smartcols)
BuildRequires:             pkgconfig(json-c) pkgconfig(cppunit) pkgconfig(libcrypto)
BuildRequires:             pkgconfig(modulemd-2.0) >= %{libmodulemd_version} 

%if %{with sanitizers}
BuildRequires:             libasan-static
BuildRequires:             liblsan-static
BuildRequires:             libubsan-static
%endif

Requires:                  libmodulemd >= %{libmodulemd_version}
Requires:                  libsolv >= %{libsolv_version}
Requires:                  librepo >= %{librepo_version}

%if %{without python2}
Obsoletes:                 python2-%{name} < %{version}-%{release}
Obsoletes:                 python2-hawkey < %{version}-%{release}
Obsoletes:                 python2-hawkey-debuginfo < %{version}-%{release}
Obsoletes:                 python2-libdnf-debuginfo < %{version}-%{release}
%endif

%description
A Library providing simplified C and Python API to libsolv.

%package devel
Summary:                   Development files for %{name}
Requires:                  %{name} = %{version}-%{release}
Requires:                  libsolv-devel >= %{libsolv_version}

%description devel
Development files for %{name}.

%if %{with python2}
%package -n                python2-%{name}
%{?python_provide:%python_provide python2-%{name}}
Summary:                   Python 2 bindings for the libdnf library.
Requires:                  %{name} = %{version}-%{release}
BuildRequires:             python2-devel swig >= %{swig_version}
%if !0%{?mageia}
BuildRequires:  %{requires_python2_sphinx}
%endif

%description -n python2-%{name}
Python 2 bindings for the libdnf library.
%endif

%if %{with python3}
%package -n                python3-%{name}
%{?python_provide:%python_provide python3-%{name}}
Summary:                   Python 3 bindings for the libdnf library.
Requires:                  %{name} = %{version}-%{release}
BuildRequires:             python3-devel %{requires_python3_sphinx} swig >= %{swig_version}

%description -n python3-%{name}
Python 3 bindings for the libdnf library.
%endif

%if %{with python2}
%package -n                python2-hawkey
Summary:                   Python 2 bindings for the hawkey library
%{?python_provide:%python_provide python2-hawkey}
BuildRequires:             python2-devel python2-nose
Requires:                  %{name} = %{version}-%{release}
Requires:                  python2-%{name} = %{version}-%{release}
Conflicts:                 python2-dnf < %{dnf_conflict}
Conflicts:                 python-dnf < %{dnf_conflict}

%description -n python2-hawkey
Python 2 bindings for the hawkey library.
%endif

%if %{with python3}
%package -n                python3-hawkey
Summary:                   Python 3 bindings for the hawkey library
%{?python_provide:%python_provide python3-hawkey}
BuildRequires:             python3-devel python3-nose
Requires:                  %{name} = %{version}-%{release}
Requires:                  python3-%{name} = %{version}-%{release}
Conflicts:                 python3-dnf < %{dnf_conflict}
Obsoletes:                 platform-python-hawkey < %{version}-%{release}

%description -n python3-hawkey
Python 3 bindings for the hawkey library.
%endif

%prep
%autosetup -p1
%if %{with python2}
mkdir build-py2
%endif
%if %{with python3}
mkdir build-py3
%endif

%build
%if %{with python2}
pushd build-py2
  %cmake -DPYTHON_DESIRED:FILEPATH=%{__python2} -DWITH_MAN=OFF ../ %{!?with_zchunk:-DWITH_ZCHUNK=OFF} %{!?with_valgrind:-DDISABLE_VALGRIND=1} %{_cmake_opts} \
  -DWITH_SANITIZERS=%{?with_sanitizers:ON}%{!?with_sanitizers:OFF}
  %make_build
popd
%endif

%if %{with python3}
pushd build-py3
  %cmake -DPYTHON_DESIRED:FILEPATH=%{__python3} -DWITH_GIR=0 -DWITH_MAN=0 -Dgtkdoc=0 ../ %{!?with_zchunk:-DWITH_ZCHUNK=OFF} %{!?with_valgrind:-DDISABLE_VALGRIND=1} %{_cmake_opts} \
  -DWITH_SANITIZERS=%{?with_sanitizers:ON}%{!?with_sanitizers:OFF}
  %make_build
popd
%endif

%check
%if %{with python3}
%if %{without python2}
pushd build-py3
  make ARGS="-V" test
popd
%else
pushd build-py3/python/hawkey/tests
  make ARGS="-V" test
popd
%endif
%endif

%install
%if %{with python2}
pushd build-py2
  %make_install
popd
%endif

%if %{with python3}
pushd build-py3
  %make_install
popd
%endif

%find_lang %{name}

%ldconfig_scriptlets

%files -f %{name}.lang 
%license COPYING
%doc README.md AUTHORS
%{_libdir}/%{name}.so.*
%dir %{_libdir}/libdnf/
%dir %{_libdir}/libdnf/plugins/
%{_libdir}/libdnf/plugins/README

%files devel
%doc %{_datadir}/gtk-doc/html/%{name}/
%{_libdir}/%{name}.so
%{_libdir}/pkgconfig/%{name}.pc
%{_includedir}/%{name}/

%if %{with python2}
%files -n python2-%{name}
%{python2_sitearch}/%{name}/
%endif

%if %{with python3}
%files -n python3-%{name}
%{python3_sitearch}/%{name}/
%endif

%if %{with python2}
%files -n python2-hawkey
%{python2_sitearch}/hawkey/
%endif

%if %{with python3}
%files -n python3-hawkey
%{python3_sitearch}/hawkey/
%endif

%changelog
* Tue Jun 8 2021 gaihuiying <gaihuiying@huawei.com> - 0.48.0-2
- Type:CVE
- ID:NA
- SUG:NA
- DESC:fix CVE-2021-3445 and remove python2 test

* Sat Aug 29 2020 openEuler Buildteam <buildteam@openeuler.org> - 0.48.0-1
- Type:requirement
- ID:NA
- SUG:NA
- DESC:upgrade to 0.48.0

* Tue Aug 18 2020 chenyaqiang <chenyaqiang@huawei.com> - 0.37.2-3
- rebuild for package build

* Tue Jan 7 2020 openEuler Buildteam <buildteam@openeuler.org> - 0.37.2-2 
- Package init.
