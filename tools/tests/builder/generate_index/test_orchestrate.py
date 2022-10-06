from pathlib import Path
from builder.generate_index import orchestrate


def test_collate_to_packages(
    dist_path: Path, dist_files: set[Path], package_names: list[str]
) -> None:
    collated = orchestrate.collate_to_packages(dist_files)
    assert sorted(collated.keys()) == sorted(package_names)
    for package_name, dists in collated.items():
        assert dists
        for dist in dists:
            assert package_name in str(dist.name)
            dist_files.remove(dist)
    assert not dist_files, f"Some distributions were not captured: {dist_files}"
