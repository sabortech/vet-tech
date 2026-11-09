"""Synthetic status matrix; no backend requests or real records."""
import sys
sys.path.insert(0, '/home/usuario/vet-tech')
import reflex as rx
from vet_tech.components.veterinary_schedule import consultation_card

class Preview(rx.State):
    rows: list[dict[str,str]] = [
        {'id':str(i), 'pet_id':'7', 'autorizado':allowed, 'status':status,
         'pet_nome':status or 'Desconhecida', 'pet_foto':'', 'foto_ausente':'sim',
         'quando':'09/11/2026', 'status_label':status or 'Desconhecida', 'motivo':'Verificação sintética'}
        for i,(status,allowed) in enumerate([
            ('agendada','sim'),('em_atendimento','sim'),('finalizada','sim'),
            ('cancelada','sim'),('','sim'),('finalizada','nao')],1)]

def index():
    return rx.box(rx.foreach(Preview.rows,consultation_card),padding='24px')
app=rx.App(stylesheets=['/vet_tech.css'])
app.add_page(index)
