from builder import build

build.build_package(
    source=build.github_source(
        org='pandas-dev',
        repo='pandas',
        tag='v1.5.0'),
    setup_py_commands=['build_ext', 'bdist_wheel'],
    build_dependencies=['numpy', 'Cython']
)
