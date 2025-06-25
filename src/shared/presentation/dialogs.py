import flet as ft
from src.shared.presentation.theme import CORTEX_AI_PALETTE


def show_dialog(page: ft.Page, title: str, message: str):
    def close_dlg(e):
        dlg.open = False
        page.update()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(title),
        content=ft.Text(message, selectable=True),
        actions=[ft.TextButton("OK", on_click=close_dlg)],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.dialog = dlg
    dlg.open = True
    page.update()

def show_snackbar(page: ft.Page, message: str, is_error: bool = False):
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=CORTEX_AI_PALETTE.error_container if is_error else CORTEX_AI_PALETTE.secondary_container,
        action_color=CORTEX_AI_PALETTE.on_error_container if is_error else CORTEX_AI_PALETTE.on_secondary_container,
    )
    page.snack_bar.open = True
    page.update()