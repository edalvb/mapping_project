import flet as ft
from pydantic import BaseModel

class ColorPalette(BaseModel):
    primary: str = "#3B82F6"
    on_primary: str = "#FFFFFF"
    primary_container: str = "#1E40AF"
    on_primary_container: str = "#DBEAFE"

    secondary: str = "#14B8A6"
    on_secondary: str = "#FFFFFF"
    secondary_container: str = "#0F766E"
    on_secondary_container: str = "#A7F3D0"

    tertiary: str = "#8B5CF6"
    on_tertiary: str = "#FFFFFF"
    tertiary_container: str = "#5B21B6"
    on_tertiary_container: str = "#EDE9FE"

    error: str = "#EF4444"
    on_error: str = "#FFFFFF"
    error_container: str = "#FEE2E2"
    on_error_container: str = "#991B1B"

    surface: str = "#F8FAFC"
    on_surface: str = "#0F172A"
    on_surface_variant: str = "#475569"
    outline: str = "#94A3B8"

    inverse_surface: str = "#1E293B"
    inverse_on_surface: str = "#E2E8F0"

CORTEX_AI_PALETTE = ColorPalette()

CORTEX_AI_THEME = ft.Theme(
    color_scheme=ft.ColorScheme(
        primary=CORTEX_AI_PALETTE.primary,
        on_primary=CORTEX_AI_PALETTE.on_primary,
        primary_container=CORTEX_AI_PALETTE.primary_container,
        on_primary_container=CORTEX_AI_PALETTE.on_primary_container,
        secondary=CORTEX_AI_PALETTE.secondary,
        on_secondary=CORTEX_AI_PALETTE.on_secondary,
        secondary_container=CORTEX_AI_PALETTE.secondary_container,
        on_secondary_container=CORTEX_AI_PALETTE.on_secondary_container,
        tertiary=CORTEX_AI_PALETTE.tertiary,
        on_tertiary=CORTEX_AI_PALETTE.on_tertiary,
        tertiary_container=CORTEX_AI_PALETTE.tertiary_container,
        on_tertiary_container=CORTEX_AI_PALETTE.on_tertiary_container,
        error=CORTEX_AI_PALETTE.error,
        on_error=CORTEX_AI_PALETTE.on_error,
        error_container=CORTEX_AI_PALETTE.error_container,
        on_error_container=CORTEX_AI_PALETTE.on_error_container,
        surface=CORTEX_AI_PALETTE.surface,
        on_surface=CORTEX_AI_PALETTE.on_surface,
        on_surface_variant=CORTEX_AI_PALETTE.on_surface_variant,
        outline=CORTEX_AI_PALETTE.outline,
    ),
    tabs_theme=ft.TabsTheme(
        unselected_label_color=CORTEX_AI_PALETTE.on_surface_variant,
    )
)