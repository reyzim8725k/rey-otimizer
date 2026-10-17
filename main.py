"""Entrypoint do Rey Optimizer."""
from core.admin import ensure_admin

if __name__ == "__main__":
    ensure_admin()
    from ui.app import ReyOptimizerApp
    ReyOptimizerApp().run()
