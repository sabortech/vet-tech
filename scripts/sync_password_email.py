"""Gera a função Xano de renderização a partir do template canônico. Sem rede."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "xano/templates"
OUTPUT = ROOT / "xano/function/security/render_password_email.xs"


def renderer_code() -> str:
    config = json.loads((TEMPLATES / "password_verification.json").read_text())
    return "\n".join([
        "const config = " + json.dumps(config, ensure_ascii=False) + ";",
        "const template = " + json.dumps((TEMPLATES / "password_verification.html").read_text(), ensure_ascii=False) + ";",
        "const plain = " + json.dumps((TEMPLATES / "password_verification.txt").read_text(), ensure_ascii=False) + ";",
        r"""const p=$input;
if(!Object.hasOwn(config.purposes,p.purpose)||typeof p.code!=='string'||!/^\d{6}$/.test(p.code)||!Number.isInteger(p.validity_minutes)||p.validity_minutes<1||p.validity_minutes>60)throw Error('Mensagem inválida.');
for(const k of ['brand_color','background_color','text_color'])if(!/^#[0-9a-fA-F]{6}$/.test(config[k]))throw Error('Cor inválida.');
for(const key of ['header_image_url','footer_image_url','davi_image_url','vitor_image_url','danikelly_image_url','ocean_image_url'])if(!/^https:\/\/[a-z0-9.-]+(?::[0-9]+)?\/[^\s"<>]*$/i.test(config[key]))throw Error('URL da imagem inválida.');
const values={...config,...config.purposes[p.purpose],code:p.code,validity_minutes:String(p.validity_minutes)};
const escape=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#x27;'}[c]));
const render=(source,safe)=>source.replace(/\{\{([a-z_]+)\}\}/g,(_,key)=>{if(typeof values[key]!=='string')throw Error('Variável inválida.');return safe?escape(values[key]):values[key];});
return {subject:values.subject,html:render(template,true),text:render(plain,false)};""",
    ])


def generated() -> str:
    code = renderer_code()
    if '"""' in code:
        raise ValueError("Delimitador Xano não permitido no template")
    return '''// Gerado por scripts/sync_password_email.py; editar xano/templates/.
function "Security/render_password_email" {
  input {
    text purpose
    text code
    int validity_minutes
  }
  stack {
    api.lambda {
      code = """
''' + code + '''
        """
      timeout = 5
    } as $message
  }
  response = $message
  history = false
  tags = ["vettech", "password-security"]
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = generated()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != content:
            raise SystemExit("Template Xano desatualizado: execute scripts/sync_password_email.py")
        print("Template Xano sincronizado.")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(content)
        print(f"Gerado: {OUTPUT}")


if __name__ == "__main__":
    main()
