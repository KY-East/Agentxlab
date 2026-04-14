"""Test configuration: mock external dependencies so tests run without Zep/DB."""

import sys
from unittest.mock import MagicMock
from types import ModuleType

# Mock zep_cloud before any app code imports it
zep_mock = ModuleType("zep_cloud")
zep_client_mock = ModuleType("zep_cloud.client")
zep_types_mock = ModuleType("zep_cloud.types")

zep_client_mock.Zep = MagicMock

class FakeEpisodeMetadataFilter:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class FakeMetadataFilterGroup:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class FakeSearchFilters:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

zep_types_mock.EpisodeMetadataFilter = FakeEpisodeMetadataFilter
zep_types_mock.MetadataFilterGroup = FakeMetadataFilterGroup
zep_types_mock.SearchFilters = FakeSearchFilters

sys.modules["zep_cloud"] = zep_mock
sys.modules["zep_cloud.client"] = zep_client_mock
sys.modules["zep_cloud.types"] = zep_types_mock

# Mock app.config.settings
settings_mock = MagicMock()
settings_mock.zep_api_key = "test-key"
settings_mock.litellm_model = "test-model"
settings_mock.deepseek_api_key = ""
settings_mock.default_ai_model = "test-model"

config_mod = ModuleType("app.config")
config_mod.settings = settings_mock
sys.modules["app.config"] = config_mod
