# template name attributes
%define templatename centos
%define templatever 7
%define templatearch x86_64

# Human-readable attributes
%define fullname Centos %templatever
%define fulltemplatearch (for AMD64/Intel EM64T)

# template dirs
%define templatedir /vz/template/%templatename/%templatever/%templatearch/config
%define ostemplatedir %templatedir/os/default

# vzpkgenv related
%define pkgman 410x64
%define package_manager rpm%pkgman
%define package_manager_pkg vzpkgenv%pkgman >= 7.0.0

# Files lists
%define files_lst() \
find %1 -type d -printf '%%%dir %%%attr(%m,root,root) %p\\n' | sed "s,%buildroot,,g" >> %2\
find %1 -type f -printf '%%%config %%%attr(%m,root,root) %p\\n' | sed "s,%buildroot,,g" >> %2\
%nil

# Sources list
%define sources_lst() \
%((cd %_sourcedir;\
s=1;\
for tmpl in %1; do\
sources=$tmpl"_*";\
for file in $sources; do\
echo Source$s: $file;\
s=$((s+1))\
done;\
done))\
%nil

# Obsoletes list
%define obsoletes_lst() \
%((for tmpl in %1; do\
[ $tmpl = os ] && continue;\
echo "Obsoletes: $tmpl-%templatename-%templatever-%templatearch-ez < 7.0.0";\
echo "Provides: $tmpl-%templatename-%templatever-%templatearch-ez = %version-%release";\
done))\
%nil

# Templates list - packages file should be always present in any template!
%define templates_list() %((cd %_sourcedir; for f in *_packages; do echo -n "${f%_*} "; done))

Summary: %fullname %fulltemplatearch Template set
Name: %templatename-%templatever-%templatearch-ez
Group: Virtuozzo/Templates
License: GPL
Version: 7.0.0
Release: 24%{?dist}
BuildRoot: %_tmppath/%name-root
BuildArch: noarch
Requires: %package_manager_pkg

# template source files
%sources_lst %templates_list

# obsoletes
%obsoletes_lst %templates_list

%description
%fullname %fulltemplatearch packaged as a Virtuozzo Template set.

%install
installfile() {
	local sourcename=%_sourcedir/${1}_$4
	local mode=$2
	local dir=$3
	local name=$4

	[ ! -f $sourcename ] && return

	install -m $mode $sourcename $dir/$name
}

rm -f files.lst
for tmpl in %templates_list; do
	[ $tmpl = "os" ] && dir=%buildroot/%ostemplatedir || \
		dir=%buildroot/%templatedir/app/$tmpl/default

	mkdir -p $dir

	if [ $tmpl = "os" ]; then
		# Os template only files

		# Text
		echo "%fullname %fulltemplatearch Virtuozzo Template" > $dir/description
		echo "%fullname %fulltemplatearch Virtuozzo Template" > $dir/summary

		# Package manager
		echo "%package_manager" > $dir/package_manager

		# Disable upgrade
		touch $dir/upgradable_versions

		# Pkgman environment
		installfile $tmpl 0644 $dir environment

		# vzctl-related
		installfile $tmpl 0644 $dir distribution

		# Kernel virtualization
		installfile $tmpl 0644 $dir osrelease

		# Os template cache scripts
		installfile $tmpl 0755 $dir pre-cache
		installfile $tmpl 0755 $dir post-cache
		installfile $tmpl 0755 $dir ct2vm
		installfile $tmpl 0755 $dir mid-pre-install
		installfile $tmpl 0755 $dir mid-post-install
		installfile $tmpl 0755 $dir pre-upgrade
		installfile $tmpl 0755 $dir post-upgrade
	else
		# App templates only files

		# Text
		echo "$tmpl for %fullname %fulltemplatearch Virtuozzo Template" > $dir/description
		echo "$tmpl for %fullname %fulltemplatearch Virtuozzo Template" > $dir/summary
	fi

	# Common things

	# Installation sources
	installfile $tmpl 0644 $dir mirrorlist
	installfile $tmpl 0644 $dir repositories

	# Packages
	installfile $tmpl 0644 $dir packages

	# Scripts
	installfile $tmpl 0755 $dir pre-install
	installfile $tmpl 0755 $dir pre-install-hn
	installfile $tmpl 0755 $dir post-install
	installfile $tmpl 0755 $dir post-install-hn

	# Versioning
	echo "%release" > $dir/release
	echo "%version" > $dir/version
	%files_lst $dir files.lst
done

%files -f files.lst

%changelog
* Wed 12 12 2018 Alexa Stefanov <astefanov@virtuozzo.com> 7.0.0-24
- disable systemd-sysctl systemd-vconsole-setup, see PSBM-58992

* Thu Jun 15 2017 Denis Silakov <dsilakov@virtuozzo.com> 7.0.0-23
- Enable extras repo, see #PSBM-67241

* Wed Dec 14 2016 Konstantin Volkov <wolf@virtuozzo.com> 7.0.0-22
- Set distribution to centos, see #PSBM-54824

* Tue Dec 13 2016 Denis Silakov <dsilakov@virtuozzo.com> 7.0.0-21
- Force firewalld to use individual calls to iptables/ebtables (#PSBM-57264)

* Mon Oct 31 2016 Konstantin Volkov <wolf@virtuozzo.com> 7.0.0-20
- Remove docker app template

* Fri Oct 28 2016 Konstantin Volkov <wolf@virtuozzo.com> 7.0.0-19
- Open tcp port for mod_ssl, see #PSBM-54473

* Thu Oct 27 2016 Konstantin Volkov <wolf@virtuozzo.com> 7.0.0-18
- Added hook for docker.service that resolves conflicts with firewalld.service, see #PSBM-54353

* Fri Oct 21 2016 Konstantin Volkov <wolf@virtuozzo.com> 7.0.0-17
- Enable firewalld by default, open appropriate ports, see #PSBM-54055
- Set default timezone for host, see #PSBM-54121

* Mon Oct 10 2016 Konstantin Volkov <wolf@virtuozzo.com> 7.0.0-16
- Turn back iptables service, see #PSBM-53457

* Thu Sep 29 2016 Konstantin Volkov <wolf@virtuozzo.com> 7.0.0-15
- Check for beature bridge:off, see #PSBM-52739

* Wed Sep 14 2016 Konstantin Volkov <wolf@virtuozzo.com> 7.0.0-14
- Disable iptables service by default, see #PSBM-52142

* Fri Sep  9 2016 Konstantin Volkov <wolf@virtuozzo.com> 7.0.0-13
- Drop postgresql and mariadb triggers: fixed in vzpkgenv, see #PSBM-50243

* Mon Sep  5 2016 Konstantin Volkov <wolf@virtuozzo.com> 7.0.0-12
- Corrected docker template according to VZ7 kernel, see #PSBM-50601

* Fri Jun 03 2016 Denis Silakov <dsilakov@virtuozzo.com> 7.0.0-11
- Fix docker template (see #PSBM-47910)

* Sat May 28 2016 Denis Silakov <dsilakov@virtuozzo.com> 7.0.0-9
- More devel template adjustments (see #PSBM-47659)

* Thu May 26 2016 Denis Silakov <dsilakov@virtuozzo.com> 7.0.0-8
- Fix kpathsea requirement for devel template
- Fix php template requirements - centos does't have php-pecl-zip in main repos

* Thu May 19 2016 Alexander Stefanov-Khryukin <akhryukin@virtuozzo.com> 7.0.0-7
- Explicitly create run/lock for mailman, see #PSBM-47198

* Tue Dec  1 2015 Konstantin Volckov <wolf@sw.ru> 7.0.0-6
- Fixed postgresql startup just after installation to Container, see #PSBM-41623

* Tue Jul 14 2015 Konstantin Volckov <wolf@sw.ru> 7.0.0-5
- Removed check for devnodes net/tun:rw, see #PSBM-34902

* Tue Jul 07 2015 Konstantin Volckov <wolf@sw.ru> 7.0.0-4
- Removed checks for tty and random devnodes rw requires for docker

* Mon Jul 06 2015 Konstantin Volckov <wolf@sw.ru> 7.0.0-3
- Adopted docker template to Virtuozzo 7.0, see #PSBM-34625

* Tue Jun 30 2015 Konstantin Volckov <wolf@sw.ru> 7.0.0-2
- Set default target as multi-user target, see #PSBM-34228
- Enable rpcbind.socket by default, see #PSBM-34604

* Wed Jun 17 2015 Konstantin Volckov <wolf@sw.ru> 7.0.0-1
- Initial release
