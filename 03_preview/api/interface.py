from ...interfaces import WidgetModuleAdapter
from ...module_registry import descriptor_for
from .module import PreviewModule

DESCRIPTOR = descriptor_for("preview")

class PreviewInterface(WidgetModuleAdapter):
    def __init__(self):
        super().__init__(DESCRIPTOR, PreviewModule)

    commands = {
        "release": lambda w, p: w.player.stop(),
        "play": lambda w, p: w.player.play() if w.btn_play.isEnabled() else None,
        "pause": lambda w, p: w.player.pause() if w.btn_pause.isEnabled() else None,
        "stop": lambda w, p: w.player.stop(),
        "seek": lambda w, p: w.player.setPosition(max(0, int(p.get("value", 0)))) if w.seek_slider.isEnabled() else None,
        "refresh": lambda w, p: w._load_current(),
        "next": lambda w, p: w._next_file(),
        "previous": lambda w, p: w._prev_file(),
    }

    def apply_context(self, widget, context):
        if context.selected_paths:
            widget.input_paths(context.selected_paths)
        elif context.working_directory:
            widget.input_paths([context.working_directory])

    def current_context(self):
        context = super().current_context()
        if self.widget is not None and self.widget.current_path:
            context.selected_paths = [self.widget.current_path]
        return context
