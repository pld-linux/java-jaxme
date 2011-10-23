# TODO
# - fix javadoc
#   java.lang.ClassNotFoundException: org.apache.tools.ant.taskdefs.optional.TraXLiaison
#
# Conditional build:
%bcond_with	javadoc		# don't build javadoc

%define srcname jaxme
Summary:	Open source implementation of JAXB
Name:		java-%{srcname}
Version:	0.5.1
Release:	1
License:	ASL 2.0
Group:		Development/Languages/Java
URL:		http://ws.apache.org/jaxme/
# svn export http://svn.apache.org/repos/asf/webservices/jaxme/tags/R0_5_1/ ws-jaxme-0.5.1
# tar czf ws-jaxme-0.5.1-src.tar.gz ws-jaxme
Source0:	ws-jaxme-%{version}-src.tar.gz
# Source0-md5:        9709c7fb68880d494c3c347c3faa74c8
Source1:	bind-MANIFEST.MF
# generated docs with forrest-0.5.1
Patch0:		docs_xml.patch
Patch1:		catalog.patch
Patch2:		system-dtd.patch
Patch3:		jdk16.patch
Patch4:		ant-scripts.patch
Patch5:		use-commons-codec.patch
BuildRequires:	ant >= 1.6
BuildRequires:	ant-apache-resolver
BuildRequires:	ant-nodeps >= 1.6
BuildRequires:	antlr
BuildRequires:	docbook-dtd45-xml
BuildRequires:	docbook-style-xsl
BuildRequires:	java(jaxp_parser_impl)
BuildRequires:	java(jaxp_transform_impl)
BuildRequires:	java-commons-codec
BuildRequires:	java-hsqldb
BuildRequires:	java-junit
BuildRequires:	java-log4j
BuildRequires:	java-xalan
BuildRequires:	java-xml-commons
BuildRequires:	java-xml-commons-resolver
BuildRequires:	java-xmldb
BuildRequires:	java-xmldb-sdk
BuildRequires:	jdk >= 1.6
BuildRequires:	jpackage-utils >= 1.6
BuildRequires:	rpmbuild(macros) >= 1.300
%if %(locale -a | grep -q '^en_US$'; echo $?)
BuildRequires:	glibc-localedb-all
%endif
Requires:	antlr
Requires:	java(jaxp_parser_impl)
Requires:	java(jaxp_transform_impl)
Requires:	java-commons-codec
Requires:	java-hsqldb
Requires:	java-junit
Requires:	java-log4j
Requires:	java-xalan
Requires:	java-xml-commons
Requires:	java-xmldb
Requires:	java-xmldb-sdk
Requires:	jpackage-utils
Obsoletes:	ws-jaxme
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
A Java/XML binding compiler takes as input a schema description (in
most cases an XML schema, but it may be a DTD, a RelaxNG schema, a
Java class inspected via reflection, or a database schema). The output
is a set of Java classes:
- A Java bean class matching the schema description. (If the schema
  was obtained via Java reflection, the original Java bean class.)
- Read a conforming XML document and convert it into the equivalent
  Java bean.
- Vice versa, marshal the Java bean back into the original XML
  document.

%package        javadoc
Summary:	Javadoc for %{name}
Group:		Documentation
Requires:	jpackage-utils

%description    javadoc
%{summary}.

%package        manual
Summary:	Documents for %{name}
Group:		Documentation

%description    manual
%{summary}.

%prep
%setup -q -n ws-%{srcname}
find -name "*.jar" | xargs rm -v

%patch0 -p0
%patch1 -p0
%patch2 -p1
%patch3 -p1
%patch4 -p0
%patch5 -p0

DOCBOOKX_DTD=$(%{_bindir}/xmlcatalog /usr/share/sgml/docbook/xml-dtd-4.5/catalog.xml "-//OASIS//DTD DocBook XML V4.5//EN")
%{__sed} -i -e 's|@DOCBOOKX_DTD@|$DOCBOOKX_DTD|' src/documentation/manual/jaxme2.xml

%build
# source code not US-ASCII
export LC_ALL=en_US

export OPT_JAR_LIST="xalan-j2 ant/ant-nodeps xalan-j2-serializer xml-commons-resolver ant/ant-apache-resolver"
# FIXME: xml-commons-jaxp-1.3-apis we can't solve
CLASSPATH=$(build-classpath antlr hsqldb commons-codec junit log4j xmldb xerces-j2)

%ant all %{?with_javadoc:Docs.all} \
	-Dbuild.sysclasspath=first \
	-Ddocbook.home=%{_datadir}/sgml/docbook \
	-Ddocbookxsl.home=%{_datadir}/sgml/docbook/xsl-stylesheets

mkdir -p META-INF
cp -p %{SOURCE1} META-INF/MANIFEST.MF
touch META-INF/MANIFEST.MF
zip -u dist/jaxmeapi-%{version}.jar META-INF/MANIFEST.MF

%if %{with javadoc}
rm -rf apidocs
mv build/docs/src/documentation/content/apidocs .
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_javadir}/%{srcname}

for jar in dist/*.jar; do
	cp -p $jar $RPM_BUILD_ROOT%{_javadir}/%{srcname}
done

# create unversioned symlinks
for a in $RPM_BUILD_ROOT%{_javadir}/%{srcname}/*.jar; do
	jar=${a##*/}
	ln -s $jar $RPM_BUILD_ROOT%{_javadir}/%{srcname}/${jar%%-%{version}.jar}.jar
done

# javadoc
%if %{with javadoc}
install -d $RPM_BUILD_ROOT%{_javadocdir}/%{srcname}-%{version}
cp -a apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{srcname}-%{version}
ln -s %{srcname}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{srcname} # ghost symlink
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc LICENSE
%{_javadir}/%{srcname}

%if %{with javadoc}
%files javadoc
%defattr(644,root,root,755)
%doc %{_javadocdir}/%{name}-%{version}
%doc %{_javadocdir}/%{name}

%files manual
%defattr(644,root,root,755)
%doc build/docs/src/documentation/content/*
%endif
