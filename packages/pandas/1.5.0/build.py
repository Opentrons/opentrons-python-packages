from builder import package_build

package_build.build_package(
    source=package_build.github_source(
        org='pandas-dev',
        repo='pandas',
        tag='v1.5.0'),
    setup_py_commands=['build_ext', 'bdist_wheel'],
    build_dependencies=['numpy', 'Cython>=0.29.32,<3', 'setuptools>=51.0.0']
)
