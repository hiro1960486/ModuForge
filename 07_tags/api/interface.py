from pathlib import Path
from ...interfaces import WidgetModuleAdapter
from ...module_registry import descriptor_for
from .module import TagsModule

DESCRIPTOR = descriptor_for('tags')

class TagsInterface(WidgetModuleAdapter):
    commands = {
        'refresh': lambda w,p: w.refresh(),
        'set_files': lambda w,p: w.set_files(p['paths']),
        'list_tags': lambda w,p: w.service.list_tags(p['path']),
        'set_tags': lambda w,p: w.set_tags_for_path(p['path'],p['tags']),
        'search_tags': lambda w,p: w.service.search(p['tag']),
        'inspect': lambda w,p: w.service.inspect(p['path']),
        'plan_move': lambda w,p: w.service.plan_move(p['path'],p['destination']),
        'move': lambda w,p: w.move_by_api(p),
    }
    def __init__(self):
        super().__init__(DESCRIPTOR,TagsModule)
    def apply_context(self,widget,context):
        widget.set_files(context.selected_paths)
    def current_context(self):
        ctx=super().current_context()
        if self.widget is not None:
            ctx.selected_paths=[str(x) for x in self.widget.paths]
        return ctx
