"""Prepara apenas os 15 documentos Xano desta change, sem publicar ou copiar segredos."""
import argparse
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
FILES=[
    *[f'table/password_{name}.xs' for name in ('lock','challenge','origin','event')],
    *[f'function/security/{name}.xs' for name in ('password_operation','render_password_email','send_password_email')],
    *[f'api/authentication/{profile}/password_POST.xs' for profile in ('tutor','veterinario')],
    *[f'api/authentication/{profile}/password/request_code_POST.xs' for profile in ('tutor','veterinario')],
    *[f'api/authentication/acesso/password_reset/{action}_POST.xs' for action in ('request','verify','complete')],
    'api/authentication/acesso/password_reset/cleanup_POST.xs',
]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    for name in FILES:
        source=ROOT/'xano'/name
        target=args.output/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
    print(f'{len(FILES)} documentos preparados em {args.output}; nenhum envio remoto.')


if __name__=='__main__':
    main()
