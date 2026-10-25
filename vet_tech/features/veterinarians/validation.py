"""Local form feedback; Xano remains the authority for all validation."""
import re

UFS = "AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split()


def professional_payload(form, species, specialties, clinic):
    crmv = str(form.get("crmv", "")).strip().upper()
    uf = str(form.get("crmv_uf", "")).strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{1,20}", crmv):
        raise ValueError("CRMV deve conter de 1 a 20 letras ou números, sem espaços internos.")
    if uf not in UFS:
        raise ValueError("Informe a UF do CRMV.")
    if not species or not specialties:
        raise ValueError("Selecione pelo menos uma espécie e uma especialidade.")
    all_ids = [*species, *specialties, *([clinic] if clinic else [])]
    if any(not str(i).isascii() or not str(i).isdecimal() or int(i) <= 0 for i in all_ids):
        raise ValueError("Selecione opções válidas dos catálogos.")
    return {"crmv": crmv, "crmv_uf": uf, "especies_ids": sorted({int(i) for i in species}),
            "especialidades_ids": sorted({int(i) for i in specialties}), "clinica_id": int(clinic) if clinic else None}
