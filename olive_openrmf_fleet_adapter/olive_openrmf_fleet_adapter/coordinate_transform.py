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


class SimilarityTransform:
    """A rotation, uniform scale, and translation in two dimensions."""

    def __init__(self, scale_cos, scale_sin, translation):
        self._scale_cos = float(scale_cos)
        self._scale_sin = float(scale_sin)
        self._translation = np.asarray(translation, dtype=float)

    def transform(self, points):
        points_array = np.asarray(points, dtype=float)
        if points_array.ndim not in (1, 2) or points_array.shape[-1] != 2:
            raise ValueError("Expected a 2D point or an array of 2D points")

        rotation_and_scale = np.array([
            [self._scale_cos, self._scale_sin],
            [-self._scale_sin, self._scale_cos],
        ])
        transformed = points_array @ rotation_and_scale + self._translation
        return transformed.tolist()

    def get_rotation(self):
        return math.atan2(self._scale_sin, self._scale_cos)

    def get_scale(self):
        return math.hypot(self._scale_cos, self._scale_sin)

    def get_translation(self):
        return self._translation.tolist()


def estimate_transform(source_points, target_points):
    """Estimate the least-squares similarity transform between 2D points."""
    source = _point_array(source_points, "source")
    target = _point_array(target_points, "target")

    if source.shape != target.shape:
        raise ValueError("Source and target must contain the same point count")
    if len(source) == 0:
        return SimilarityTransform(1.0, 0.0, [0.0, 0.0])

    source_mean = source.mean(axis=0)
    target_mean = target.mean(axis=0)
    source_centered = source - source_mean
    target_centered = target - target_mean
    denominator = np.sum(source_centered * source_centered)

    if denominator < 1e-12:
        return SimilarityTransform(
            1.0, 0.0, target_mean - source_mean)

    scale_cos = np.sum(source_centered * target_centered) / denominator
    scale_sin = (
        np.dot(source_centered[:, 0], target_centered[:, 1])
        - np.dot(source_centered[:, 1], target_centered[:, 0])
    ) / denominator

    rotation_and_scale = np.array([
        [scale_cos, -scale_sin],
        [scale_sin, scale_cos],
    ])
    translation = target_mean - rotation_and_scale @ source_mean

    return SimilarityTransform(scale_cos, scale_sin, translation)


def estimate_transform_error(transform, source_points, target_points):
    """Return the mean squared point error for an estimated transform."""
    source = _point_array(source_points, "source")
    target = _point_array(target_points, "target")

    if source.shape != target.shape:
        raise ValueError("Source and target must contain the same point count")
    if len(source) == 0:
        return 0.0

    transformed = np.asarray(transform.transform(source), dtype=float)
    return float(np.mean(np.sum((transformed - target) ** 2, axis=1)))


def _point_array(points, name):
    points_array = np.asarray(points, dtype=float)
    if points_array.size == 0:
        return np.empty((0, 2), dtype=float)
    if points_array.ndim != 2 or points_array.shape[1] != 2:
        raise ValueError(f"{name.capitalize()} points must have shape (N, 2)")
    return points_array
