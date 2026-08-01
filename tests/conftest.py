import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SRC = REPO / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture(scope="session")
def repo_root() -> pathlib.Path:
    return REPO


@pytest.fixture(scope="session")
def model_dirs(repo_root):
    return {
        "tt": repo_root / "models" / "lcdm_tt_beta3e-4",
        "ee": repo_root / "models" / "lcdm_tt_ee_lowl",
    }
