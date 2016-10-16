from sublime import *
from sublime_plugin import *
from threading import Thread
import subprocess
import os.path as path

g_plugin_settings = load_settings('PlantUMLSublime.sublime-settings')

class plantuml_preview(TextCommand):
    tag_ = 'plantuml_preview'
    settings_ = None

    def run(self, edit):
        uml_texts = self.uml_texts()
        for index, uml_text in enumerate(uml_texts):
            uml_filepath = self.view.file_name()
            suffix = len(uml_texts) != 1 and str(index+1) or None
            diagram_filepath = self.make_diagram_filepath(uml_filepath, suffix)
            self.async_generate(uml_text, diagram_filepath)

    def isEnabled(self):
        return True

    def async_generate(self, uml_text, diagram_filepath):
        t = Thread(target=self.sync_generate, args=(uml_text, diagram_filepath,))
        t.daemon = True
        t.start()

    def sync_generate(self, uml_text, diagram_filepath):
        diagram_fd = open(diagram_filepath, 'wb')
        cmd = ['java', '-jar', self.plantuml_jar_path(), '-pipe', '-tpng', '-quiet', '-charset', 'UTF-8']
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=diagram_fd)
        p.communicate(input=uml_text.encode('UTF-8'))
        self.open_diagram(diagram_filepath)

    def uml_texts(self):
        uml_regions, view, sel = [], self.view, self.view.sel()
        pairs = ((start, view.find('@end', start.begin()),) for start in view.find_all('@start'))
        for start, end in pairs: uml_regions.append(view.full_line(start.cover(end)))
        uml_texts = []
        if len(uml_regions) == 1:
            return [view.substr(uml_regions[0])]
        for uml_region in uml_regions:
            for sel_region in sel:
                if (uml_region.intersects(sel_region)): uml_texts.append(view.substr(uml_region))
        return uml_texts

    def open_diagram(self, diagram_filepath):
        active_window().open_file(diagram_filepath)

    def make_diagram_filepath(self, uml_filepath, suffix=None):
        diagram_filepath = None
        if suffix != None:
            diagram_filepath = path.splitext(uml_filepath)[0] + '-' + suffix + '.png'
        else:
            diagram_filepath = path.splitext(uml_filepath)[0] + '.png'
        return diagram_filepath

    def plantuml_jar_path(self):
        plantuml_jar_path = g_plugin_settings.get("plantuml_jar_path")
        if plantuml_jar_path == 'default':
            plantuml_jar_path = path.abspath(path.join(path.dirname(__file__), 'plantuml-8024.jar'))
        return plantuml_jar_path

def plugin_loaded():
    pass