from ...interfaces import WidgetModuleAdapter
from ...module_registry import descriptor_for
from .module import OrganizerModule
DESCRIPTOR=descriptor_for('organizer')
class OrganizerInterface(WidgetModuleAdapter):
    commands={'inspect':lambda w,p:w.service.inspect(p['path']), 'plan':lambda w,p:w.service.plan(p['path'],p['destination'],p.get('action','copy')), 'execute':lambda w,p:w.service.execute(p['plan'],confirm=p.get('confirm') is True)}
    def __init__(self):super().__init__(DESCRIPTOR,OrganizerModule)
    def apply_context(self,widget,context):
        if context.selected_paths:widget.source.setText(context.selected_paths[0]);widget.show_info()
