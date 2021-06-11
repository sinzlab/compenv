import pytest

from repro.distribution import InstalledDistributionConverter
from repro.model import Distribution, Module


class FakePackagePath:
    def __init__(self, path):
        self.path = path
        self.suffix = "." + self.path.split(".")[-1]

    def locate(self):
        return self.path


class FakePathlibPath(FakePackagePath):
    _not_existing_paths = {"/dist1/tests/module1.py", "/dist2/tests/module1.py"}

    def __init__(self, path):
        self.path = path

    def exists(self):
        return self.path not in self._not_existing_paths

    def __eq__(self, other):
        return self.path == other.path

    def __hash__(self):
        return hash(self.path)


class FakeImportlibMetadataDistribution:
    def __init__(self, metadata, files):
        self.metadata = metadata
        self.files = files


@pytest.fixture
def fake_distribution_metadata():
    return {
        "dist1": {"Name": "dist1", "Version": "0.1.0"},
        "dist2": {"Name": "dist2", "Version": "0.1.2"},
        "dist3": {"Name": "dist3", "Version": "1.2.3"},
    }


@pytest.fixture
def fake_distribution_files():
    return {
        "dist1": [
            FakePackagePath("/dist1/package1/module1.py"),
            FakePackagePath("/dist1/README.md"),
            FakePackagePath("/dist1/package1/__init__.py"),
            FakePackagePath("/dist1/tests/module1.py"),
        ],
        "dist2": [
            FakePackagePath("/dist2/tests/module1.py"),
            FakePackagePath("/dist2/requirements.txt"),
            FakePackagePath("/dist2/package1/__init__.py"),
            FakePackagePath("/dist2/package1/module1.py"),
        ],
        "dist3": None,
    }


@pytest.fixture
def fake_distributions(fake_distribution_metadata, fake_distribution_files):
    return [
        FakeImportlibMetadataDistribution(m, fake_distribution_files[n]) for n, m in fake_distribution_metadata.items()
    ]


@pytest.fixture
def fake_get_installed_distributions_func(fake_distributions):
    def _fake_get_installed_distributions_func():
        return iter(fake_distributions)

    return _fake_get_installed_distributions_func


@pytest.fixture
def converter(fake_get_installed_distributions_func):
    InstalledDistributionConverter._get_installed_distributions_func = staticmethod(
        fake_get_installed_distributions_func
    )
    InstalledDistributionConverter._path_cls = FakePathlibPath
    return InstalledDistributionConverter()


def test_correct_distributions_returned(converter):
    expected_distributions = {
        "dist1": Distribution(
            "dist1",
            "0.1.0",
            frozenset(
                [
                    Module(FakePathlibPath("/dist1/package1/__init__.py")),
                    Module(FakePathlibPath("/dist1/package1/module1.py")),
                ]
            ),
        ),
        "dist2": Distribution(
            "dist2",
            "0.1.2",
            frozenset(
                [
                    Module(FakePathlibPath("/dist2/package1/__init__.py")),
                    Module(FakePathlibPath("/dist2/package1/module1.py")),
                ]
            ),
        ),
        "dist3": Distribution("dist3", "1.2.3", frozenset()),
    }
    actual_distributions = converter()
    assert actual_distributions == expected_distributions


def test_repr(converter):
    assert repr(converter) == "InstalledDistributionConverter()"
