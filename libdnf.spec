%global libsolv_version 0.7.7
%global libmodulemd_version 2.5.0
%global librepo_version 1.12.0
%global dnf_conflict 4.2.23
%global swig_version 3.0.12

%global requires_python3_sphinx python3-sphinx

%bcond_with valgrind
%bcond_with rhsm
%bcond_with zchunk
%bcond_with sanitizers


%global _cmake_opts \\\
    -DENABLE_RHSM_SUPPORT=%{?with_rhsm:ON}%{!?with_rhsm:OFF} \\\
    %{nil}

Name:                      libdnf
Version:                   0.48.0
Release:                   1
Summary:                   Library providing simplified C and Python API to libsolv
License:                   LGPLv2+
URL:                       https://github.com/rpm-software-management/libdnf
Source0:                   %{url}/archive/%{version}/%{name}-%{version}.tar.gz                    
BuildRequires:             cmake gcc gcc-c++ libsolv-devel >= %{libsolv_version} gettext
BuildRequires:             pkgconfig(librepo) >= %{librepo_version} pkgconfig(check)              
BuildRequires:             pkgconfig(gio-unix-2.0) >= 2.46.0 pkgconfig(gtk-doc) gpgme-devel
BuildRequires:             rpm-devel >= 4.11.0 pkgconfig(sqlite3) pkgconfig(smartcols)
BuildRequires:             pkgconfig(json-c) pkgconfig(cppunit) pkgconfig(libcrypto)
BuildRequires:             pkgconfig(modulemd-2.0) >= %{libmodulemd_version} 

Requires:                  libmodulemd >= %{libmodulemd_version}
Requires:                  libsolv >= %{libsolv_version}
Requires:                  librepo >= %{librepo_version}

Obsoletes:                 python2-%{name} < %{version}-%{release}
Obsoletes:                 python2-hawkey < %{version}-%{release}
Obsoletes:                 python2-hawkey-debuginfo < %{version}-%{release}
Obsoletes:                 python2-libdnf-debuginfo < %{version}-%{release}

%description
A Library providing simplified C and Python API to libsolv.

%package devel
Summary:                   Development files for %{name}
Requires:                  %{name} = %{version}-%{release}
Requires:                  libsolv-devel >= %{libsolv_version}

%description devel
Development files for %{name}.

%package -n                python3-%{name}
%{?python_provide:%python_provide python3-%{name}}
Summary:                   Python 3 bindings for the libdnf library.
Requires:                  %{name} = %{version}-%{release}
BuildRequires:             python3-devel %{requires_python3_sphinx} swig >= %{swig_version}

%description -n python3-%{name}
Python 3 bindings for the libdnf library.

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

%prep
%autosetup
mkdir build-py3

%build
pushd build-py3
  %cmake -DPYTHON_DESIRED:FILEPATH=%{__python3} -DWITH_GIR=0 -DWITH_MAN=0 -Dgtkdoc=0 ../ %{!?with_zchunk:-DWITH_ZCHUNK=OFF} %{!?with_valgrind:-DDISABLE_VALGRIND=1} %{_cmake_opts} \
  -DWITH_SANITIZERS=%{?with_sanitizers:ON}%{!?with_sanitizers:OFF}
  %make_build
popd

%check
pushd build-py3
  make ARGS="-V" test
popd

%install
pushd build-py3
  %make_install
popd

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

%files -n python3-%{name}
%{python3_sitearch}/%{name}/

%files -n python3-hawkey
%{python3_sitearch}/hawkey/

%changelog
* Tue Apr 28 2020 zhouyihang <zhouyihang3@huawei.com> - 0.48.0-1
- Type:requirement
- ID:NA
- SUG:NA
- DESC:update libdnf version to 0.48.0

* Tue Jan 7 2020 openEuler Buildteam <buildteam@openeuler.org> - 0.37.2-2 
- Package init.
