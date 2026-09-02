from importlib.metadata import metadata


def test_package_declares_mit_license():
    package_metadata = metadata("blastdesign-ai")

    assert package_metadata["License-Expression"] == "MIT"