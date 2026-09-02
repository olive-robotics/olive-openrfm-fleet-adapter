# Copyright 2026 Olive Robotics
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import math

import numpy as np
import pytest

from olive_openrmf_fleet_adapter.coordinate_transform import estimate_transform
from olive_openrmf_fleet_adapter.coordinate_transform import (
    estimate_transform_error,
)


def test_estimate_transform_recovers_similarity_transform():
    source = [[0.0, 0.0], [2.0, 0.0], [0.0, 1.0], [2.0, 1.0]]
    target = [[3.0, -1.0], [3.0, 3.0], [1.0, -1.0], [1.0, 3.0]]

    transform = estimate_transform(source, target)

    assert np.allclose(transform.transform(source), target)
    assert transform.get_rotation() == pytest.approx(math.pi / 2.0)
    assert transform.get_scale() == pytest.approx(2.0)
    assert transform.get_translation() == pytest.approx([3.0, -1.0])
    assert estimate_transform_error(transform, source, target) \
        == pytest.approx(0.0)


def test_estimate_transform_handles_identical_source_points():
    transform = estimate_transform(
        [[1.0, 2.0], [1.0, 2.0]],
        [[4.0, 7.0], [6.0, 9.0]],
    )

    assert transform.get_scale() == pytest.approx(1.0)
    assert transform.get_rotation() == pytest.approx(0.0)
    assert transform.transform([1.0, 2.0]) == pytest.approx([5.0, 8.0])


def test_estimate_transform_rejects_mismatched_point_counts():
    with pytest.raises(ValueError, match="same point count"):
        estimate_transform([[0.0, 0.0]], [[0.0, 0.0], [1.0, 1.0]])
