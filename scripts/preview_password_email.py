"""Renderiza somente prévias fictícias; não gera códigos reais nem envia e-mail."""
import argparse
import base64
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "xano/templates"
PLACEHOLDER = re.compile(r"\{\{([a-z_]+)\}\}")


def render(purpose: str, code: str, validity_minutes: int) -> dict[str, str]:
    """Usa o HTML canônico com substituição estrita e escape de valores."""
    config = json.loads((TEMPLATES / "password_verification.json").read_text())
    if purpose not in config["purposes"]:
        raise ValueError("Finalidade inválida")
    if not isinstance(code, str) or re.fullmatch(r"[0-9]{6}", code) is None:
        raise ValueError("Código deve conter seis dígitos ASCII")
    if type(validity_minutes) is not int or not 1 <= validity_minutes <= 60:
        raise ValueError("Validade inválida")
    for key in ("brand_color", "background_color", "text_color"):
        if re.fullmatch(r"#[0-9a-fA-F]{6}", config[key]) is None:
            raise ValueError("Cor inválida")
    for key in ("header_image_url", "footer_image_url", "davi_image_url", "vitor_image_url", "danikelly_image_url", "ocean_image_url"):
        if re.fullmatch(r'https://[a-zA-Z0-9.-]+(?::[0-9]+)?/[^\s"<>]*', config[key]) is None:
            raise ValueError("URL da imagem inválida")
    values = {key: config[key] for key in ("brand_color", "background_color", "text_color", "header_image_url", "footer_image_url", "davi_image_url", "vitor_image_url", "danikelly_image_url", "ocean_image_url")}
    values.update(config["purposes"][purpose], code=code, validity_minutes=str(validity_minutes))

    def substitute(source: str, escape: bool) -> str:
        return PLACEHOLDER.sub(lambda match: html.escape(values[match[1]], quote=True) if escape else values[match[1]], source)

    return {
        "subject": values["subject"],
        "html": substitute((TEMPLATES / "password_verification.html").read_text(), True),
        "text": substitute((TEMPLATES / "password_verification.txt").read_text(), False),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "openspec/changes/verificar-alteracao-senha-email/evidence/email")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for purpose in ("change", "reset"):
        result = render(purpose, "042681", 10)
        # A prévia usa a cópia local da arte; o e-mail enviado mantém a URL HTTPS.
        config = json.loads((TEMPLATES / "password_verification.json").read_text())
        for key, filename in (("header_image_url", "password-email-header.jpg"), ("footer_image_url", "password-email-pets.jpg"), ("davi_image_url", "developers/davi-diniz.jpeg"), ("vitor_image_url", "developers/vitor-sousa.png"), ("danikelly_image_url", "developers/danikelly-alves.png"), ("ocean_image_url", "password-email-ocean.jpeg")):
            mime = "image/png" if filename.endswith(".png") else "image/jpeg"
            local_image = "data:" + mime + ";base64," + base64.b64encode((TEMPLATES / filename).read_bytes()).decode("ascii")
            result["html"] = result["html"].replace(config[key], local_image)
        for extension, content in (("html", result["html"]), ("txt", result["text"])):
            (args.output / f"{purpose}.{extension}").write_text(content)
    print(f"Prévias fictícias geradas em {args.output}")


if __name__ == "__main__":
    main()
