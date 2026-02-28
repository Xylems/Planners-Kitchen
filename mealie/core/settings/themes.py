from pydantic_settings import BaseSettings, SettingsConfigDict


class Theme(BaseSettings):
    light_primary: str = "#558B2F"
    light_accent: str = "#8BC34A"
    light_secondary: str = "#4A7C59"
    light_success: str = "#43A047"
    light_info: str = "#1976D2"
    light_warning: str = "#F57F17"
    light_error: str = "#EF5350"

    dark_primary: str = "#7CB342"
    dark_accent: str = "#AED581"
    dark_secondary: str = "#66BB6A"
    dark_success: str = "#43A047"
    dark_info: str = "#1976D2"
    dark_warning: str = "#F57F17"
    dark_error: str = "#EF5350"
    model_config = SettingsConfigDict(env_prefix="theme_", extra="allow")
