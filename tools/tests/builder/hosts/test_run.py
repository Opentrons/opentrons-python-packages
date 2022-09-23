import re
from builder.host import run
from builder import __version__


def test_container_image_name() -> None:
    assert __version__.split("+")[0] in run._container_image_specific()
    assert re.match("^([:/a-z0-9-._]){0,128}$", run._container_image_specific())
    assert re.match("^([:/a-z0-9-._]){0,128}$", run._container_image_latest())


def test_container_run_invoker() -> None:
    args = ["arg1", "arg2", "arg with spaces"]
    invoke_str = run._container_run_invoke_cmd("my-cool-container", args)
    assert "my-cool-container" in invoke_str
    for arg in args:
        assert arg in invoke_str
