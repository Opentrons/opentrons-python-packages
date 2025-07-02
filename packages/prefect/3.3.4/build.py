from builder import package_build

# Build Prefect 3.3.4 for OT-2
# This package uses modern Python packaging but should be compatible with setup.py builds
package_build.build_package(
    source=package_build.github_source(
        org='PrefectHQ',
        repo='prefect',
        tag='3.3.4'),
    setup_py_commands=['bdist_wheel'],
    build_dependencies=[]
)