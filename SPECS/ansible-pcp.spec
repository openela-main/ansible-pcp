Name:             ansible-pcp
Version:          2.2.7
Release:          1%{?dist}
Summary:          Ansible Metric collection for Performance Co-Pilot
License:          MIT
URL:              https://github.com/performancecopilot/ansible-pcp
Source:           https://github.com/performancecopilot/ansible-pcp/archive/v%{version}/%{name}-%{version}.tar.gz
BuildArch:        noarch

%if 0%{?rhel}
%global collection_namespace redhat
%global collection_name rhel_metrics
%else
%global collection_namespace performancecopilot
%global collection_name metrics
%endif

# NOTE: Even though ansible-core is in 8.6, it is only available
# at *runtime*, not at *buildtime* - so we can't have
# ansible-core as a build_dep on latest RHEL versions.
%if 0%{?fedora}
%bcond_without ansible
%global ansible_build_dep ansible-core >= 2.11.0
%else
%if 0%{?rhel} && ! 0%{?epel}
%bcond_with ansible
%else
%bcond_without ansible
%global ansible_build_dep ansible >= 2.9.10
%endif
%endif

%if 0%{?rhel} >= 8
Requires: (ansible-core >= 2.11.0 or ansible >= 2.9.0)
%endif

%if %{with ansible}
BuildRequires:    %{ansible_build_dep}
%endif

%{!?ansible_collection_files:%define ansible_collection_files %{_datadir}/ansible/collections/ansible_collections/%{collection_namespace}/}

# package has been removed from RHEL8
%if 0%{?rhel} >= 8
%bcond_with ansible_lint
%else
%bcond_without ansible_lint
%endif

%if %{with ansible_lint}
BuildRequires:    python3-ansible-lint
%endif

%description
A collection containing roles for Performance Co-Pilot (PCP) and related
software such as Redis and Grafana.  The collection is made up of several
Ansible roles, including:

%{collection_namespace}.%{collection_name}.pcp
A role for core PCP capabilities, configuring live performance analysis
with a large base set of metrics from the kernel and system services, as
well as data recording and rule inference.

%{collection_namespace}.%{collection_name}.redis
A role for configuring a local Redis server, suitable for use with a
Performance Co-Pilot archive repository (for single or many hosts) and
fast, scalable querying of metrics.

%{collection_namespace}.%{collection_name}.grafana
A role for configuring a local Grafana server, providing web frontend
visuals for Performance Co-Pilot metrics, both live and historically.
Data sources for Vector (live), Redis (historical) and interactive
bpftrace (eBPF) scripts can be configured by this role.  The PCP REST
API service (from the core pcp role) should be configured in order to
use this role.

%{collection_namespace}.%{collection_name}.bpftrace
A role that extends the core PCP role, providing metrics from bpftrace
scripts using Linux eBPF facilities.  Configuring authentication of a
local user capable of running bpftrace scripts via the PCP agent is a
key task of this role.

%{collection_namespace}.%{collection_name}.elasticsearch
A role that extends the core PCP role, providing metrics from a live
ElasticSearch instance for PCP analysis or exporting of PCP metric
values (and metadata) to ElasticSearch for the indexing and querying
of performance data.

%prep
%autosetup
mv .yamllint.yml yamllint.yml
mv .yamllint_defaults.yml yamllint_defaults.yml
%if 0%{?rhel}
rm -vr roles/repository tests/*repository* tests/*/*repository* docs/repository
%endif
rm -vr .github .gitignore .ansible-lint .*.yml
sed -i \
    -e 's/^name: .*/name: %{collection_name}/g' \
    -e 's/^namespace: .*/namespace: %{collection_namespace}/g' \
    galaxy.yml
find . -name \*.yml -o -name \*.md | while read file; do
    sed -i \
        -e 's/performancecopilot.metrics/%{collection_namespace}.%{collection_name}/g' \
    $file
done

%build
%if %{with ansible}
%ansible_collection_build
%else
tar -cf %{_tmppath}/%{collection_namespace}-%{collection_name}-%{version}.tar.gz .
%endif

%install
%if %{with ansible}
%ansible_collection_install
%else
mkdir -p %{buildroot}%{ansible_collection_files}/%{collection_name}
cd %{buildroot}%{ansible_collection_files}/%{collection_name}
tar -xf %{_tmppath}/%{collection_namespace}-%{collection_name}-%{version}.tar.gz
%endif

%check
mv yamllint.yml .yamllint.yml
mv yamllint_defaults.yml .yamllint_defaults.yml
%if %{with ansible_lint}
ansible-lint `find roles -name \*.yml`
%endif

%files
%doc README.md
%license LICENSE
%{ansible_collection_files}

%changelog
* Fri Oct 28 2022 Nathan Scott <nathans@redhat.com> 2.2.7-1
- Latest upstream release (BZ 2132847)

* Thu Apr 21 2022 Nathan Scott <nathans@redhat.com> 2.2.5-1
- Switch to using bcond spec file mechanisms
- Latest upstream release (BZ 2059464)

* Tue Feb 15 2022 Nathan Scott <nathans@redhat.com> 2.2.2-2
- RHEL8.6+, RHEL9+, Fedora - add "ansible-core or ansible" dep

* Fri Nov 12 2021 Nathan Scott <nathans@redhat.com> 2.2.2-1
- Resolves Grafana provisioning issue (BZ 1967321)
- Latest upstream release (BZ 2022168)

* Thu Aug 26 2021 Nathan Scott <nathans@redhat.com> 2.2.1-1
- Latest upstream release

* Fri Jun 25 2021 Nathan Scott <nathans@redhat.com> 2.1.4-1
- Latest upstream release

* Tue Jun 08 2021 Nathan Scott <nathans@redhat.com> 2.1.3-3
- Rebuild for full pass through CI/gating processes

* Mon Jun 07 2021 Nathan Scott <nathans@redhat.com> 2.1.3-2
- Drop unnecessary package dependency on Ansible

* Thu Jun 03 2021 Nathan Scott <nathans@redhat.com> 2.1.3-1
- Initial version of RHEL package (BZ 1854055)
- Latest upstream release

* Fri Feb 05 2021 Nathan Scott <nathans@redhat.com> 2.1.2-1
- Add RHEL macros to the spec alongside Fedora
- Latest upstream release

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Wed Nov 11 2020 Nathan Scott <nathans@redhat.com> 2.0.3-1
- Updated for new version with changed namespace
- Ansible collection macros now used in the spec
- Added ansible-lint checking in %%check section

* Fri Oct 23 2020 Nathan Scott <nathans@redhat.com> 1.0.0-1
- Initial RPM spec build
