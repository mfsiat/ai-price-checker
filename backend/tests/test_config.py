"""Tests for environment-driven configuration and production-safety guards."""

import pytest

from app.config import DEFAULT_CORS_ORIGIN, ConfigError, load_settings


def test_defaults_to_development_and_localhost():
    settings = load_settings(env={})
    assert settings.environment == "development"
    assert settings.cors_origins == [DEFAULT_CORS_ORIGIN]
    assert not settings.is_production


def test_origins_parsed_and_trimmed():
    settings = load_settings(
        env={"CORS_ORIGINS": " https://a.com , , https://b.com ,"}
    )
    assert settings.cors_origins == ["https://a.com", "https://b.com"]


def test_blank_origins_fall_back_to_default():
    settings = load_settings(env={"CORS_ORIGINS": " , ,"})
    assert settings.cors_origins == [DEFAULT_CORS_ORIGIN]


def test_production_requires_explicit_origins():
    settings = load_settings(
        env={"ENVIRONMENT": "production", "CORS_ORIGINS": "https://app.example.com"}
    )
    assert settings.is_production
    assert settings.cors_origins == ["https://app.example.com"]


def test_production_rejects_wildcard_origin():
    with pytest.raises(ConfigError):
        load_settings(env={"ENVIRONMENT": "production", "CORS_ORIGINS": "*"})


def test_log_level_normalized():
    settings = load_settings(env={"LOG_LEVEL": "debug"})
    assert settings.log_level == "DEBUG"
