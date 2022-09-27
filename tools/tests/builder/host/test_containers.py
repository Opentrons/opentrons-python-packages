import re
from builder.host import containers
from builder import __version__


def test_container_image_name() -> None:
    assert __version__.split("+")[0] in containers._container_image_specific()
    assert re.match("^([:/a-z0-9-._]){0,128}$", containers._container_image_specific())
    assert re.match("^([:/a-z0-9-._]){0,128}$", containers._container_image_latest())


def test_container_run_invoker() -> None:
    args = ["arg1", "arg2", "arg with spaces"]
    invoke_str = containers._container_run_invoke_cmd("my-cool-container", args, "")
    assert "my-cool-container" in invoke_str
    for arg in args:
        assert arg in invoke_str
