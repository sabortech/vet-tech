"""Synthetic schedule cards; no API requests or real clinical records."""
import sys
sys.path.insert(0, '/home/usuario/vet-tech')
import reflex as rx
from vet_tech.components.veterinary_schedule import schedule_card
class Preview(rx.State):
    rows: list[dict[str,str]] = [
        {'id':str(i), 'pet_id':'7', 'autorizado':'sim', 'status':status,
         'pet_nome':label, 'pet_foto':'', 'foto_ausente':'sim', 'hora':'10:00',
         'quando':'09/11/2026', 'status_label':label, 'motivo':'Verificação visual do LED'}
        for i,(status,label) in enumerate([('agendada','Não iniciou'),('em_atendimento','Em atendimento'),('finalizada','Concluída'),('cancelada','Cancelada'),('','Desconhecida')],1)]
def index():
    return rx.box(rx.foreach(Preview.rows,lambda row: schedule_card(row)),padding='30px',display='grid',gap='24px',grid_template_columns=['1fr','1fr','repeat(3, minmax(0, 1fr))'])
app=rx.App(stylesheets=['/vet_tech.css'])
app.add_page(index)
