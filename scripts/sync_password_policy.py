"""Sincroniza a política JS testável com a função Xano, sem acesso remoto."""
from pathlib import Path
import argparse

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'xano/function/security/password_operation.xs'
START='// POLICY_BEGIN\n'
END='// POLICY_END'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    original=TARGET.read_text()
    head,tail=original.split(START,1)
    _,tail=tail.split(END,1)
    policy=(ROOT/'xano/security/password_policy.js').read_text()
    if '"""' in policy:
        raise ValueError('Delimitador inválido')
    expected=head+START+policy+END+tail
    if args.check:
        if expected!=original:
            raise SystemExit('Política Xano desatualizada')
        print('Política Xano sincronizada.')
    else:
        TARGET.write_text(expected)


if __name__=='__main__':
    main()
