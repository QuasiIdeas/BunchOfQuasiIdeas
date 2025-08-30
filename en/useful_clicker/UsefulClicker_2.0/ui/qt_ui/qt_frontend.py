"""Lightweight Qt5 frontend for UsefulClicker XML engine.

This module implements a minimal UI that can be used to control the
XMLProgram engine: play/pause, next (skip), restart, load/save XML and
inspect program tree. The UI is intentionally lightweight so other
frontends (web_ui etc.) can be plugged in similarly.
"""
from pathlib import Path
import threading, sys, time
try:
    from PyQt5 import QtWidgets, QtCore, uic
except Exception:
    QtWidgets = None

from core.xml_engine import XMLProgram

def _load_ui_file(ui_path: Path):
    # Workaround: some .ui files produced by QtDesigner contain C++-style enum
    # qualifiers like "Qt::WindowModality::NonModal" which older/newer PyQt
    # uic.loadUi may fail to resolve. Replace such qualifiers with plain
    # enum names before loading.
    txt = Path(ui_path).read_text(encoding='utf-8')
    if 'Qt::WindowModality::' in txt:
        txt = txt.replace('Qt::WindowModality::', '')
    # Use temporary file to feed uic
    import tempfile
    tf = tempfile.NamedTemporaryFile(mode='w', suffix='.ui', delete=False, encoding='utf-8')
    try:
        tf.write(txt); tf.flush(); tf.close()
        return uic.loadUi(tf.name)
    finally:
        try:
            import os; os.unlink(tf.name)
        except Exception:
            pass

class ProgramThread(threading.Thread):
    def __init__(self, prog: XMLProgram, on_finish=None):
        super().__init__(daemon=True)
        self.prog = prog
        self.on_finish = on_finish

    def run(self):
        try:
            self.prog.run()
        except Exception:
            # let UI observe via on_finish
            pass
        if callable(self.on_finish):
            try:
                self.on_finish()
            except Exception:
                pass

class MainWindowWrapper:
    def __init__(self, xml_path: Path):
        if QtWidgets is None:
            raise RuntimeError("PyQt5 is required for qt_ui")
        self.app = QtWidgets.QApplication(sys.argv)
        ui_file = Path(__file__).parent / "mainwindow.ui"
        self.win = _load_ui_file(ui_file)
        self.xml_path = Path(xml_path)
        self.prog = None
        self.worker = None
        # curiosity output variable name (detected from XML extnode) and last cached value
        self._curiosity_output_var = None
        self._last_curiosity_value = None
        # cached lists to keep UI stable if other code clears widgets
        self._cached_disciplines = []
        self._cached_subtopics = {}

        # Wire basic controls
        self.win.playButton.clicked.connect(self.on_play_pause)
        # toolButton_2 -> next/skip
        try:
            self.win.toolButton_2.clicked.connect(self.on_next)
        except Exception:
            pass
        # toolButton_3 -> restart
        try:
            self.win.toolButton_3.clicked.connect(self.on_restart)
        except Exception:
            pass

        # XML load/save via shortcuts (use QKeySequence to avoid operator misuse)
        try:
            from PyQt5.QtGui import QKeySequence
            save_sc = QtWidgets.QShortcut(QKeySequence('Ctrl+S'), self.win)
            save_sc.activated.connect(self.save_xml)
            open_sc = QtWidgets.QShortcut(QKeySequence('Ctrl+O'), self.win)
            open_sc.activated.connect(self.open_xml)
        except Exception:
            # fallback: ignore shortcuts if QKeySequence isn't available
            pass

        # regenerate buttons (best-effort behaviour)
        try:
            self.win.regenerateButton.clicked.connect(self.on_regenerate_curiosity)
        except Exception:
            pass
        try:
            self.win.regenerateList.clicked.connect(self.on_regenerate_llmcall)
        except Exception:
            pass

        # Populate initial XML and tree
        self.load_xml_file(self.xml_path)

        # Optional: connect a 'loadProgram' button from the UI (if present)
        btn = getattr(self.win, 'loadProgram', None)
        if btn is not None:
            try:
                btn.clicked.connect(self.on_load_program_clicked)
            except Exception:
                pass

        # timer to refresh state (buttons, labels)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.refresh_state)
        self.timer.start(200)

    def start_program(self):
        # create XMLProgram and start thread
        self.prog = XMLProgram(self.current_xml_path)
        self.worker = ProgramThread(self.prog, on_finish=self.on_thread_finish)
        self.worker.start()

    def on_thread_finish(self):
        # called in worker thread; schedule UI update in main thread
        QtCore.QTimer.singleShot(0, self.refresh_state)

    def on_play_pause(self):
        if not self.prog:
            return
        self.prog._toggle_pause()

    def on_next(self):
        if not self.prog:
            return
        self.prog._skip_now()

    def on_restart(self):
        if not self.prog:
            # start fresh
            self.start_program()
            return
        # request restart — engine will stop at next checkpoint
        self.prog.request_restart()

    def refresh_state(self):
        # update play button visual based on program state
        running = self.worker is not None and self.worker.is_alive()
        paused = getattr(self.prog, 'paused', False) if self.prog else False
        if running and not paused:
            self.win.playButton.setText('PAUSE')
            self.win.playButton.setStyleSheet('border: 2px solid #9ece1b')
        elif running and paused:
            self.win.playButton.setText('RESUME')
            self.win.playButton.setStyleSheet('border: 2px solid #e5c07b')
        else:
            self.win.playButton.setText('PLAY')
            self.win.playButton.setStyleSheet('')

        # update listIndex if engine provides any index info
        idx = None
        if self.prog and isinstance(self.prog.variables.get('index', None), int):
            idx = self.prog.variables.get('index')
        if idx is not None:
            self.win.listIndex.setText(f"{idx}")

        # NOTE: do not change visibility of tabs here to avoid flicker/hiding
        # after they are initialized. Visibility is managed once at XML load time.
        # Poll curiosity output variable (if engine running) and update UI when it changes
        try:
            ov = getattr(self, '_curiosity_output_var', None)
            if ov and self.prog:
                val = self.prog.variables.get(ov)
                if val is not None and val != self._last_curiosity_value:
                    self._last_curiosity_value = val
                    # normalize into list of strings
                    if isinstance(val, (list, tuple)):
                        items = [str(x) for x in val]
                        raw = '\n'.join(items)
                    else:
                        raw = str(val)
                        items = [l for l in raw.splitlines() if l.strip()]
                    try:
                        if hasattr(self.win, 'raw_llm_output_textarea'):
                            try:
                                self.win.raw_llm_output_textarea.setPlainText(raw)
                            except Exception:
                                try:
                                    self.win.raw_llm_output_textarea.setHtml('<pre>%s</pre>' % raw)
                                except Exception:
                                    pass
                    except Exception:
                        pass
                    try:
                        if hasattr(self.win, 'termsList'):
                            self.win.termsList.clear()
                            for it in items:
                                self.win.termsList.addItem(str(it))
                    except Exception:
                        pass
        except Exception:
            pass
        # Ensure discipline/subtopics lists stay populated (repair if cleared externally)
        try:
            dlw = getattr(self.win, 'disciplinesList', None)
            if dlw is not None and dlw.count() == 0 and self._cached_disciplines:
                for s in self._cached_disciplines:
                    try:
                        dlw.addItem(s)
                    except Exception:
                        pass
            slw = getattr(self.win, 'subtopicsList', None)
            if slw is not None and slw.count() == 0 and self._cached_subtopics:
                # try to repopulate for currently selected discipline
                cur = None
                try:
                    cur_item = dlw.currentItem() if dlw is not None else None
                    cur = cur_item.text() if cur_item is not None else None
                except Exception:
                    cur = None
                if not cur and self._cached_disciplines:
                    cur = self._cached_disciplines[0]
                if cur and cur in self._cached_subtopics:
                    for s in self._cached_subtopics.get(cur, []):
                        try:
                            slw.addItem(s)
                        except Exception:
                            pass
        except Exception:
            pass

    def open_xml(self):
        fn, _ = QtWidgets.QFileDialog.getOpenFileName(self.win, 'Open XML', str(self.xml_path.parent), 'XML Files (*.xml);;All Files (*)')
        if not fn:
            return
        self.load_xml_file(Path(fn))

    def on_load_program_clicked(self):
        """Handler for loadProgram button: delegate to the common open dialog.

        This simply calls open_xml() to reuse the same behavior and path
        selection logic used elsewhere in the UI.
        """
        try:
            self.open_xml()
        except Exception:
            # fallback: ensure nothing crashes if dialog fails
            return

    def save_xml(self):
        # save contents of xmlEditor to current file
        try:
            txt = self.win.xmlEditor.toPlainText()
        except Exception:
            txt = ''
        if not txt.strip():
            return
        fn, _ = QtWidgets.QFileDialog.getSaveFileName(self.win, 'Save XML', str(self.current_xml_path), 'XML Files (*.xml);;All Files (*)')
        if not fn:
            return
        Path(fn).write_text(txt, encoding='utf-8')
        # reload tree from saved file
        self.load_xml_file(Path(fn))

    def load_xml_file(self, path: Path):
        self.current_xml_path = Path(path)
        try:
            txt = self.current_xml_path.read_text(encoding='utf-8')
        except Exception:
            txt = ''
        # update xmlEditor: try setPlainText, fall back to setHtml
        try:
            ed = getattr(self.win, 'xmlEditor', None)
            if ed is not None:
                try:
                    ed.setPlainText(txt)
                except Exception:
                    try:
                        ed.setHtml('<pre>%s</pre>' % (txt,))
                    except Exception:
                        pass
        except Exception:
            pass
        # parse and populate tree widget
        try:
            from lxml import etree as ET
        except Exception:
            import xml.etree.ElementTree as ET
        try:
            self.parsed_tree = ET.fromstring(txt.encode('utf-8'))
        except Exception:
            self.parsed_tree = None
        self.populate_tree()
        # initialize CuriosityNode controls if present in XML
        try:
            has_cur = False
            if self.parsed_tree is not None:
                for n in self.parsed_tree.findall('.//*'):
                    try:
                        tag = (n.tag or '').lower()
                        if tag == 'curiositynode':
                            has_cur = True; break
                        # also accept extnode/module=curiosity_drive_node
                    if tag == 'extnode' and ( (n.get('module') or '').strip() == 'curiosity_drive_node' ):
                        has_cur = True
                        try:
                            ov = n.get('output_var')
                            if ov:
                                self._curiosity_output_var = ov
                        except Exception:
                            pass
                        break
                    except Exception:
                        continue
            if has_cur:
                self._init_curiosity_tab()
            # detect llmcall presence as well and set tab visibility
            has_llm = False
            try:
                if self.parsed_tree is not None:
                    for n in self.parsed_tree.findall('.//*'):
                        try:
                            if (n.tag or '').lower() == 'llmcall':
                                has_llm = True; break
                        except Exception:
                            continue
            except Exception:
                has_llm = False
            try:
                self.win.CuriosityNodeTab.setVisible(has_cur)
            except Exception:
                pass
            try:
                self.win.llmcall_tab.setVisible(has_llm)
            except Exception:
                pass
            # schedule re-init after a short delay in case other UI actions clear widgets
            try:
                QtCore.QTimer.singleShot(700, lambda: self._init_curiosity_tab() if has_cur else None)
            except Exception:
                pass
        except Exception:
            pass

    def _init_curiosity_tab(self):
        """Populate disciplinesList and subtopicsList from curiosity_drive_node module."""
        # ensure repo root is on sys.path so curiosity_drive_node can be imported
        try:
            repo_root = Path(__file__).resolve().parents[2]
            rp = str(repo_root)
            import sys
            if rp not in sys.path:
                sys.path.insert(0, rp)
        except Exception:
            pass
        try:
            import curiosity_drive_node as cdn
        except Exception:
            cdn = None
        if cdn is None:
            return
        # Populate disciplinesList
        try:
            dlw = getattr(self.win, 'disciplinesList', None)
            if dlw is not None:
                dlw.clear()
                self._cached_disciplines = []
                for d in getattr(cdn, 'disciplines', []):
                    try:
                        s = str(d)
                    except Exception:
                        s = repr(d)
                    dlw.addItem(s)
                    self._cached_disciplines.append(s)
        except Exception:
            pass
        # Populate subtopicsList (empty by default or for first discipline)
        try:
            slw = getattr(self.win, 'subtopicsList', None)
            if slw is not None:
                slw.clear()
                # if there is at least one discipline, show its subtopics
                first = None
                try:
                    first = cdn.disciplines[0] if getattr(cdn, 'disciplines', None) else None
                except Exception:
                    first = None
                if first and getattr(cdn, 'subtopics', None):
                    items = cdn.subtopics.get(first, [])
                    self._cached_subtopics = {}
                    for k,v in getattr(cdn, 'subtopics', {}).items():
                        try:
                            self._cached_subtopics[str(k)] = [str(x) for x in v]
                        except Exception:
                            self._cached_subtopics[str(k)] = [repr(x) for x in v]
                    for it in self._cached_subtopics.get(str(first), []):
                        slw.addItem(it)
        except Exception:
            pass
        # connect selection change: when discipline selected -> populate subtopics
        try:
            if dlw is not None and slw is not None:
                def _on_discipline_changed(current, previous=None):
                    try:
                        txt = current.text() if current is not None else None
                    except Exception:
                        try:
                            txt = str(current)
                        except Exception:
                            txt = None
                    slw.clear()
                    if txt and getattr(cdn, 'subtopics', None):
                        items = cdn.subtopics.get(txt, [])
                        for it in items:
                            try:
                                slw.addItem(str(it))
                            except Exception:
                                slw.addItem(repr(it))
                try:
                    dlw.currentItemChanged.connect(_on_discipline_changed)
                except Exception:
                    try:
                        dlw.itemSelectionChanged.connect(lambda: _on_discipline_changed(dlw.currentItem()))
                    except Exception:
                        pass
        except Exception:
            pass

    def populate_tree(self):
        tw = self.win.treeWidget
        tw.clear()
        if not getattr(self, 'parsed_tree', None):
            return
        def add_item(parent, node):
            if hasattr(node, 'tag'):
                try:
                    text = str(node.tag)
                except Exception:
                    try:
                        text = repr(node.tag)
                    except Exception:
                        text = '<tag>'
            else:
                text = str(node)
            it = QtWidgets.QTreeWidgetItem([text])
            parent.addChild(it)
            for ch in list(node):
                add_item(it, ch)

        root = self.parsed_tree
        try:
            root_text = str(root.tag)
        except Exception:
            try:
                root_text = repr(root.tag)
            except Exception:
                root_text = '<root>'
        root_item = QtWidgets.QTreeWidgetItem([root_text])
        tw.addTopLevelItem(root_item)
        for ch in list(root):
            add_item(root_item, ch)
        tw.expandAll()

    def on_regenerate_curiosity(self):
        # best-effort: call curiosity_drive_node.run_node in background and show results
        try:
            import curiosity_drive_node as cdn
        except Exception:
            cdn = None
        def worker():
            if cdn is None:
                out = 'curiosity module not available'
                items = []
            else:
                txt = cdn.run_node()
                out = txt
                items = [s for s in txt.splitlines() if s.strip()]
            def ui_update():
                try:
                    self.win.raw_llm_output_textarea.setPlainText(out)
                except Exception:
                    try:
                        self.win.raw_llm_output_textarea.setHtml('<pre>%s</pre>' % out)
                    except Exception:
                        pass
                try:
                    self.win.termsList.clear()
                    for it in items:
                        self.win.termsList.addItem(it)
                except Exception:
                    pass
                # request program restart
                if self.prog:
                    self.prog.request_restart()
            QtCore.QTimer.singleShot(0, ui_update)
        threading.Thread(target=worker, daemon=True).start()

    def on_regenerate_llmcall(self):
        # Find first llmcall node in parsed xml and try to invoke engine handler
        if not getattr(self, 'parsed_tree', None):
            return
        node = None
        for n in self.parsed_tree.findall('.//'):
            try:
                if n.tag.lower() == 'llmcall':
                    node = n; break
            except Exception:
                continue
        if node is None:
            return
        # run handle_llmcall in background using a temporary XMLProgram instance
        def worker():
            prog = XMLProgram(self.current_xml_path)
            try:
                prog.handle_llmcall(node)
                out = prog.variables.get(node.get('output_var') or '','')
                if isinstance(out, list):
                    items = out
                    out_text = '\n'.join(items)
                else:
                    out_text = str(out)
                    items = [l for l in out_text.splitlines() if l.strip()]
            except Exception as e:
                out_text = f'LLM call failed: {e}'
                items = []
            def ui_update():
                try:
                    self.win.raw_llm_output_textarea_2.setPlainText(out_text)
                except Exception:
                    pass
                try:
                    self.win.listWidget.clear()
                    for it in items:
                        self.win.listWidget.addItem(str(it))
                except Exception:
                    pass
                if self.prog:
                    self.prog.request_restart()
            QtCore.QTimer.singleShot(0, ui_update)
        threading.Thread(target=worker, daemon=True).start()

    def run(self):
        # start program thread and show UI
        self.start_program()
        self.win.show()
        return self.app.exec_()

def run_ui(xml_path: str):
    mw = MainWindowWrapper(Path(xml_path))
    return mw.run()

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('xml_path')
    args = ap.parse_args()
    run_ui(args.xml_path)
