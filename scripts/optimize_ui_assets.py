"""Generate delivery assets without changing source images or composition.

Run: .venv/bin/python scripts/optimize_ui_assets.py
Pillow is a build-time tool; the app serves the generated files directly.
"""
import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
OUTPUT = ASSETS / 'optimized'
SOURCES = {
    'fundo.jpeg': 1600,
    'fundo02.jpeg': 1600,
    'fundo_mar.jpeg': 1600,
    'fundinho.jpeg': 1600,
    'fundopets.jpeg': 1600,
    'fundpet.jpeg': 1600,
    'fundpet-dark.png': 1600,
    'mascote02-sem-sombra.png': 640,
    'tutu-sem-fundo.png': 640,
    'mascote_logo.png': 512,
    'mascote05.png': 800,
    'mascote-perfil.png': 640,
    'espreitando.png': 640,
}


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    results = []
    for filename, edge in SOURCES.items():
        source = ASSETS / filename
        target = OUTPUT / (source.stem + '.webp')
        with Image.open(source) as raw:
            img = ImageOps.exif_transpose(raw)
            img = img.convert('RGBA' if 'A' in img.getbands() or 'transparency' in raw.info else 'RGB')
            img.thumbnail((edge, edge), Image.Resampling.LANCZOS)
            img.save(target, 'WEBP', quality=86 if img.mode == 'RGBA' else 84, method=6, exact=True)
            dimensions = list(img.size)
        results.append({'source': str(source.relative_to(ROOT)), 'output': str(target.relative_to(ROOT)),
                        'before_bytes': source.stat().st_size, 'after_bytes': target.stat().st_size,
                        'dimensions': dimensions})
    source = ASSETS / 'mascote_logo.png'
    target = OUTPUT / 'favicon.png'
    with Image.open(source) as raw:
        img = ImageOps.contain(raw.convert('RGBA'), (64, 64), Image.Resampling.LANCZOS)
        img.save(target, 'PNG', optimize=True)
    results.append({'source': str(source.relative_to(ROOT)), 'output': str(target.relative_to(ROOT)),
                    'before_bytes': source.stat().st_size, 'after_bytes': target.stat().st_size,
                    'dimensions': list(img.size)})
    (OUTPUT / 'manifest.json').write_text(json.dumps(results, indent=2) + '\n')
    before = sum({r['source']: r['before_bytes'] for r in results}.values())
    after = sum(r['after_bytes'] for r in results)
    print(json.dumps({'before_bytes': before, 'after_bytes': after, 'reduction_percent': round(100 * (1-after/before), 1)}))


if __name__ == '__main__':
    main()
