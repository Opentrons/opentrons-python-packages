import os
from builder.host import run


def test_container_build_invoker() -> None:
    invoke_str = run._container_build_invoke_cmd(25, 12)
    assert "--build-arg=HOST_USER_ID=25" in invoke_str
    assert "--build-arg=HOST_GROUP_ID=12" in invoke_str
    assert os.path.exists(next((arg for arg in invoke_str if "Dockerfile" in arg)))


def container_run_invoker() -> None:
    args = ["arg1", "arg2", "arg with spaces"]
    invoke_str = run._container_run_invoke_cmd("my-cool-container", args)
    assert "my-cool-container" in invoke_str
    for arg in args:
        assert arg in invoke_str
