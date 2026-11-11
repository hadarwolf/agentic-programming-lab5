import random
from collections.abc import Iterator

import pytest


@pytest.fixture(autouse=True)
def seeded_random() -> Iterator[None]:
    """Make the computer opponent's tie-breaks the same on every run."""
    state = random.getstate()
    random.seed(67723)
    yield
    random.setstate(state)
