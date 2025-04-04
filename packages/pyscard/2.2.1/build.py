from builder import package_build

package_build.build_package(
    source=package_build.github_source(
        org='LudovicRousseau',
        repo='pyscard',
        tag='2.2.1'),
    setup_py_commands=['build_ext', 'bdist_wheel'],
    build_dependencies=[]
)
