"""Ordinary Python CLI: creates a GLB, a manifest, and an offline 3D preview."""
import argparse
import json
from pathlib import Path
from cozy_city.layout import build_world
from cozy_city.export import export_world


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preset',choices=['city','village'])
    parser.add_argument('--seed',type=int)
    parser.add_argument('--config',type=Path)
    parser.add_argument('--out',type=Path,default=Path('output/city'))
    parser.add_argument('--force',action='store_true',help='Overwrite only generated output files')
    args = parser.parse_args()
    try:
        cfg = json.loads(args.config.read_text(encoding='utf-8')) if args.config else {}
        if args.preset is not None: cfg['preset']=args.preset
        if args.seed is not None: cfg['seed']=args.seed
        result = export_world(build_world(cfg),args.out,args.force)
    except (ValueError,OSError,TypeError) as exc:
        parser.exit(1,f'Error: {exc}\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))
    print(f'Open: {(args.out/"preview.html").resolve()}')


if __name__ == '__main__':
    main()
