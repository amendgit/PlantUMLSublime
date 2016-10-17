from sublime import *
from sublime_plugin import *
from threading import Thread
import subprocess
import os.path as path
import os

g_plugin_settings = load_settings('PlantUMLSublime.sublime-settings')

def plantuml_jar_path():
    plantuml_jar_path = g_plugin_settings.get("plantuml_jar_path")
    if plantuml_jar_path == 'default':
        plantuml_jar_path = path.abspath(path.join(path.dirname(__file__), 'plantuml-8024.jar'))
    return plantuml_jar_path

def open_diagram_in_sublime(diagram_filepath):
    active_window().open_file(diagram_filepath)

def make_diagram_filepath(uml_filepath, suffix=None, format='png'):
    diagram_filepath = None
    if suffix != None:
        diagram_filepath = path.splitext(uml_filepath)[0] + '-' + suffix + '.' + format
    else:
        diagram_filepath = path.splitext(uml_filepath)[0] + '.' + format
    return diagram_filepath

def async_generate(uml_text, diagram_filepath, output_format='png'):
    t = Thread(target=sync_generate, args=(uml_text, diagram_filepath, output_format,))
    t.daemon = True
    t.start()

def sync_generate(uml_text, diagram_filepath, output_format):
    diagram_fd = open(diagram_filepath, 'wb')
    arg_format = '-t' + output_format
    cmd = ['java', '-jar', plantuml_jar_path(), '-pipe', arg_format, '-charset', 'UTF-8']
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=diagram_fd)
    p.communicate(input=uml_text.encode('UTF-8'))
    if p.returncode != 0:
        if output_format == 'html': error_message('PlantUMLSublime: export html only supported by class diagram.')
        os.remove(diagram_filepath)
        return
    if output_format in ['txt', 'png', 'html']:
        open_diagram_in_sublime(diagram_filepath)

def uml_texts_from_view(view):
    uml_regions, sel = [], view.sel()
    pairs = ((start, view.find('@end', start.begin()),) for start in view.find_all('@start'))
    for start, end in pairs: uml_regions.append(view.full_line(start.cover(end)))
    uml_texts = []
    if len(uml_regions) == 1:
        return [view.substr(uml_regions[0])]
    for uml_region in uml_regions:
        for sel_region in sel:
            if (uml_region.intersects(sel_region)): uml_texts.append(view.substr(uml_region))
    return uml_texts

class plantuml_preview(TextCommand):
    tag_ = 'plantuml_preview'
    settings_ = None

    def run(self, edit):
        uml_texts = uml_texts_from_view(self.view)
        for index, uml_text in enumerate(uml_texts):
            uml_filepath = self.view.file_name()
            suffix = len(uml_texts) != 1 and str(index+1) or None
            diagram_filepath = make_diagram_filepath(uml_filepath, suffix)
            async_generate(uml_text, diagram_filepath)

    def isEnabled(self):
        return True

class plantuml_export(TextCommand):
    tag_ = 'plantuml_export'
    formats_ = ['png', 'txt', 'svg']

    def run(self, edit):
        self.view.window().show_quick_panel(self.formats_, self.export)
    
    def export(self, value):
        output_format = self.formats_[value]
        uml_texts = uml_texts_from_view(self.view)
        for index, uml_text in enumerate(uml_texts):
            uml_filepath = self.view.file_name()
            suffix = len(uml_texts) != 1 and str(index+1) or None
            diagram_filepath = make_diagram_filepath(uml_filepath, suffix, output_format)
            async_generate(uml_text, diagram_filepath, output_format)

    def isEnabled(self):
        return True

def plugin_loaded():
    pass