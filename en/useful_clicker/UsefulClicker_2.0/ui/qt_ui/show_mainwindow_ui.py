"""
Standalone script: loads mainwindow.ui and shows it.

Usage:
  python show_mainwindow_ui.py [--offscreen] [--auto-close N]

By default it will try to show the window normally. Use --offscreen to force
QT_QPA_PLATFORM=offscreen (useful in CI). --auto-close closes the window after
N seconds (default 3).
"""
import sys
import os
import argparse
from pathlib import Path

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--offscreen', action='store_true', help='Force offscreen platform')
    ap.add_argument('--auto-close', type=float, default=3.0, help='Automatically close after N seconds (0 = never)')
    args = ap.parse_args(argv)

    if args.offscreen:
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

    try:
        from PyQt5 import QtWidgets, QtCore
    except Exception as e:
        print('PyQt5 import failed:', e)
        return 2

    # Ensure repo module path so we can import helper
    repo_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo_root))

    try:
        from ui.qt_ui import qt_frontend as qf
    except Exception:
        # Fallback: try to load UI directly via uic with similar workaround
        from PyQt5 import uic
        ui_file = Path(__file__).resolve().parent / 'mainwindow.ui'
        # Workaround for C++-style enum qualifiers
        txt = ui_file.read_text(encoding='utf-8')
        if 'Qt::WindowModality::' in txt:
            txt = txt.replace('Qt::WindowModality::', '')
        import tempfile
        tf = tempfile.NamedTemporaryFile(mode='w', suffix='.ui', delete=False, encoding='utf-8')
        tf.write(txt); tf.flush(); tf.close()
        try:
            app = QtWidgets.QApplication([])
            win = uic.loadUi(tf.name)
            # attach loadProgram handler if present
            def _do_load_program_fallback():
                start_dir = Path(__file__).resolve().parents[2] / 'examples'
                start = str(start_dir) if start_dir.exists() else str(Path.cwd())
                fn, _ = QtWidgets.QFileDialog.getOpenFileName(win, 'Load XML program', start, 'XML Files (*.xml);;All Files (*)')
                if not fn:
                    return
                try:
                    txt = Path(fn).read_text(encoding='utf-8')
                except Exception:
                    txt = ''
                ed = getattr(win, 'xmlEditor', None)
                if ed is not None:
                    try:
                        ed.setPlainText(txt)
                    except Exception:
                        try:
                            ed.setHtml('<pre>%s</pre>' % (txt,))
                        except Exception:
                            pass
                # populate tree widget
                try:
                    from lxml import etree as ET
                except Exception:
                    import xml.etree.ElementTree as ET
                try:
                    parsed = ET.fromstring(txt.encode('utf-8'))
                except Exception:
                    parsed = None
                tw = getattr(win, 'treeWidget', None)
                if tw is not None:
                    tw.clear()
                    if parsed is not None:
                        def add_item(parent, node):
                            # coerce tag to string to avoid QTreeWidgetItem type errors
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
                        root_item = QtWidgets.QTreeWidgetItem([parsed.tag])
                        tw.addTopLevelItem(root_item)
                        for ch in list(parsed):
                            add_item(root_item, ch)
                        tw.expandAll()
            btn = getattr(win, 'loadProgram', None)
            if btn is not None:
                try:
                    btn.clicked.connect(_do_load_program_fallback)
                except Exception:
                    pass
            win.show()
            if args.auto_close > 0:
                QtCore.QTimer.singleShot(int(args.auto_close*1000), app.quit)
            return app.exec_()
        finally:
            try: os.unlink(tf.name)
            except Exception: pass

    # Create QApplication before loading UI to avoid 'Must construct a QApplication before a QWidget'
    app = QtWidgets.QApplication([])

    # Use helper to load ui (it applies the same enum-workaround)
    ui_file = Path(__file__).resolve().parent / 'mainwindow.ui'
    try:
        win = qf._load_ui_file(ui_file)
    except Exception as e:
        print('Loading UI failed:', e)
        return 3

    # attach a loadProgram handler to the loaded UI (if present)
    def _do_load_program():
        start_dir = Path(__file__).resolve().parents[2] / 'examples'
        start = str(start_dir) if start_dir.exists() else str(Path.cwd())
        fn, _ = QtWidgets.QFileDialog.getOpenFileName(win, 'Load XML program', start, 'XML Files (*.xml);;All Files (*)')
        if not fn:
            return
        try:
            txt = Path(fn).read_text(encoding='utf-8')
        except Exception:
            txt = ''
        ed = getattr(win, 'xmlEditor', None)
        if ed is not None:
            try:
                ed.setPlainText(txt)
            except Exception:
                try:
                    ed.setHtml('<pre>%s</pre>' % (txt,))
                except Exception:
                    pass
        # populate tree widget
        try:
            from lxml import etree as ET
        except Exception:
            import xml.etree.ElementTree as ET
        try:
            parsed = ET.fromstring(txt.encode('utf-8'))
        except Exception:
            parsed = None
        tw = getattr(win, 'treeWidget', None)
        if tw is not None:
            tw.clear()
            if parsed is not None:
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
                root_item = QtWidgets.QTreeWidgetItem([parsed.tag])
                tw.addTopLevelItem(root_item)
                for ch in list(parsed):
                    add_item(root_item, ch)
                tw.expandAll()
    btn = getattr(win, 'loadProgram', None)
    if btn is not None:
        try:
            btn.clicked.connect(_do_load_program)
        except Exception:
            pass

    # If the loaded object is a QMainWindow it may not have a parent; show it.
    win.show()

    if args.auto_close > 0:
        QtCore.QTimer.singleShot(int(args.auto_close*1000), app.quit)

    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())
