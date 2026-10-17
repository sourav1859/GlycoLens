from types import SimpleNamespace

import numpy as np
import pytest

from research.models.adapters import ContextConfiguration, ModelInferenceError, ModelNotLoadedError
from research.models.adapters.converters import meal_window_to_forecast_example
from research.models.adapters.timesfm3 import TIMESFM3_REVISION, TimesFM3ForecastAdapter
from tests.research.test_m2_protocol import shifted_window


class FakeModel:
    def __init__(self, crossing=False):
        self.calls = []
        self.crossing = crossing

    def predict(self, values, **kwargs):
        self.calls.append((values, kwargs))
        quantiles = np.tile(np.arange(9) + 100, (24, 1)).astype(float)
        if self.crossing:
            quantiles[:, 0] = 200
        return SimpleNamespace(quantiles=quantiles)


def test_checkpoint_is_pinned_load_idempotent_and_meal_features_reach_backend():
    fake = FakeModel()
    loads = []

    def loader(**kwargs):
        loads.append(kwargs)
        return fake

    model = TimesFM3ForecastAdapter(loader=loader)
    example = meal_window_to_forecast_example(
        shifted_window(0), context=ContextConfiguration.CGM_INSULIN_NUTRITION
    )
    with pytest.raises(ModelNotLoadedError):
        model.predict(example.request)
    model.load()
    model.load()
    result = model.predict(example.request)
    assert len(loads) == 1 and loads[0]["revision"] == TIMESFM3_REVISION
    assert loads[0]["local_files_only"] is True
    assert fake.calls[0][1]["past_only_covariates"].shape[1] == 24
    assert fake.calls[0][1]["past_future_covariates"].shape == (4, 48)
    assert np.any(fake.calls[0][1]["past_future_covariates"][:, 23] > 0)
    assert np.all(fake.calls[0][1]["past_future_covariates"][:, 24:] == 0)
    assert result.median == (104,) * 24


def test_crossing_quantiles_fail_without_silent_sorting():
    model = TimesFM3ForecastAdapter(loader=lambda **kw: FakeModel(crossing=True))
    model.load()
    example = meal_window_to_forecast_example(
        shifted_window(0), context=ContextConfiguration.CGM_ONLY
    )
    with pytest.raises(ModelInferenceError):
        model.predict(example.request)
