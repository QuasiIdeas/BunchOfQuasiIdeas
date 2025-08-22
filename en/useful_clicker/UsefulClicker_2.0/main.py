
import argparse
from pathlib import Path
from core.xml_engine import XMLProgram
def main():
    ap = argparse.ArgumentParser(description="UsefulClicker — Stage 2")
    ap.add_argument("xml_path", type=str, help="Path to XML scenario")
    ap.add_argument("--debug", action="store_true", help="Show debug window")
    args = ap.parse_args()
    xml_path = Path(args.xml_path); log_path = xml_path.with_suffix(".usefulclicker.log")
    prog = XMLProgram(xml_path, debug=args.debug, log_path=log_path)
    prog.run()
if __name__ == "__main__":
    main()
