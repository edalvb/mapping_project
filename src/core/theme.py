import flet as ft

primary = "#3B82F6"
on_primary = "#FFFFFF"
primary_container = "#1E40AF"
on_primary_container = "#DBEAFE"

secondary = "#14B8A6"
on_secondary = "#FFFFFF"
secondary_container = "#0F766E"
on_secondary_container = "#A7F3D0"

tertiary = "#8B5CF6"
on_tertiary = "#FFFFFF"
tertiary_container = "#5B21B6"
on_tertiary_container = "#EDE9FE"

error = "#EF4444"
on_error = "#FFFFFF"
error_container = "#FEE2E2"
on_error_container = "#991B1B"

surface = "#F8FAFC"
on_surface = "#0F172A"
surface_variant = "#CBD5E1"
on_surface_variant = "#475569"

outline = "#94A3B8"
outline_variant = "#CBD5E1"

background = "#F8FAFC"
on_background = "#0F172A"

inverse_surface = "#1E293B"
inverse_on_surface = "#E2E8F0"
inverse_primary = "#A5B4FC"

scrim = "#000000"

cortex_theme = ft.Theme(
    color_scheme=ft.ColorScheme(
        primary=primary,
        on_primary=on_primary,
        primary_container=primary_container,
        on_primary_container=on_primary_container,
        secondary=secondary,
        on_secondary=on_secondary,
        secondary_container=secondary_container,
        on_secondary_container=on_secondary_container,
        tertiary=tertiary,
        on_tertiary=on_tertiary,
        tertiary_container=tertiary_container,
        on_tertiary_container=on_tertiary_container,
        error=error,
        on_error=on_error,
        error_container=error_container,
        on_error_container=on_error_container,
        background=background,
        on_background=on_background,
        surface=surface,
        on_surface=on_surface,
        surface_variant=surface_variant,
        on_surface_variant=on_surface_variant,
        outline=outline,
        outline_variant=outline_variant,
        inverse_surface=inverse_surface,
        on_inverse_surface=inverse_on_surface,
        inverse_primary=inverse_primary,
        scrim=scrim,
    ),
    visual_density=ft.VisualDensity.COMPACT,
)