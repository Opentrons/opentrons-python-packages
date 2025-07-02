from builder import package_build

# Build Pendulum 3.1.0 for OT-2
# Pendulum is a dependency of Prefect and requires compilation for ARM
package_build.build_package(
    source=package_build.github_source(
        org='sdispater',
        repo='pendulum',
        tag='3.1.0'),
    setup_py_commands=['bdist_wheel'],
    build_dependencies=['setuptools', 'wheel', 'maturin>=1.0,<2.0']
)