from io import BytesIO
from pathlib import Path
from time import perf_counter
import base64,json,resource,sys
from xml.sax.saxutils import escape
import reportlab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,KeepTogether
from pypdf import PdfReader
root=Path('/home/usuario/vet-tech');out=root/'openspec/changes/exportar-consulta-pdf/evidence';out.mkdir(exist_ok=True)
fonts=Path(reportlab.__file__).parent/'fonts'
pdfmetrics.registerFont(TTFont('VeraPDF',str(fonts/'Vera.ttf')))
pdfmetrics.registerFont(TTFont('VeraPDFBold',str(fonts/'VeraBd.ttf')))
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='VTBody',fontName='VeraPDF',fontSize=10,leading=15,textColor=colors.HexColor('#244532'),spaceAfter=8))
styles.add(ParagraphStyle(name='VTHeading',fontName='VeraPDFBold',fontSize=14,leading=19,textColor=colors.HexColor('#356438'),spaceBefore=16,spaceAfter=10))
styles.add(ParagraphStyle(name='VTTitle',fontName='VeraPDFBold',fontSize=25,leading=32,textColor=colors.HexColor('#244532'),spaceAfter=8))
def para(t,style='VTBody'):return Paragraph(escape(t).replace('\n','<br/>'),styles[style])
def build(long=False):
 data=BytesIO();story=[]
 story += [Image(str(root/'assets/mascote_logo.png'),width=22*mm,height=22*mm,kind='proportional'),para('VetTech','VTTitle'),para('Relatório da consulta','VTHeading'),para('PRÉVIA • DADOS SINTÉTICOS • MODELO PARA APROVAÇÃO')]
 story += [para('Consulta nº 42  |  Pet: Amora (exemplo)'),para('Data do atendimento: 04/11/2026'),para('Veterinário responsável: ID 7 (exemplo)'),para('Motivo','VTHeading'),para('Avaliação de rotina — exemplo de conteúdo publicado.')]
 story += [para('Diagnóstico','VTHeading'),para('Informação clínica sintética para validação do documento. Não é um diagnóstico real.'),para('Observações','VTHeading')]
 text='Orientações de exemplo: atenção à hidratação e observação. Acentuação: ç, ã, é.\nQuebras de linha são preservadas. '
 story += [para(text*(900 if long else 2))]
 story += [para('Vacinas','VTHeading'),para('Registro sintético — data da aplicação: 04/11/2026. Próxima dose: Não informado.'),para('Medicamentos','VTHeading'),para('Medicamento de exemplo — dose e unidade conforme registro publicado. Sem prescrição real.'),para('Exames','VTHeading'),para('Exame sintético — solicitado em 04/11/2026; resultado: Não informado.')]
 def footer(c,d):
  c.setStrokeColor(colors.HexColor('#c6dcbc'));c.line(18*mm,17*mm,A4[0]-18*mm,17*mm)
  c.setFont('VeraPDF',8);c.setFillColor(colors.HexColor('#356438'));c.drawString(18*mm,12*mm,'VetTech • Cópia da consulta publicada');c.drawRightString(A4[0]-18*mm,12*mm,f'Página {d.page}')
 doc=SimpleDocTemplate(data,pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,topMargin=18*mm,bottomMargin=23*mm,title='VetTech — consulta sintética',author='VetTech')
 started=perf_counter();doc.build(story,onFirstPage=footer,onLaterPages=footer);elapsed=perf_counter()-started
 pdf=data.getvalue();reader=PdfReader(BytesIO(pdf));text=''.join(p.extract_text() for p in reader.pages)
 assert pdf.startswith(b'%PDF-') and all(x in text for x in ['ç','ã','é','Amora'])
 assert all(abs(float(p.mediabox.width)-A4[0])<1 for p in reader.pages)
 if long:assert len(reader.pages)>1 and 'Exame sintético' in text
 return pdf,{'pages':len(reader.pages),'bytes':len(pdf),'base64_bytes':len(base64.b64encode(pdf)),'elapsed_seconds':round(elapsed,3),'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
short,s=build();long,l=build(True)
(out/'modelo-consulta-sintetica.pdf').write_bytes(short)
(out/'prova-texto-longo.pdf').write_bytes(long)
(out/'local-proof.json').write_text(json.dumps({'python':sys.version.split()[0],'reportlab':reportlab.Version,'short':s,'long':l,'scope':'prova local; não homologa hospedagem','font_license':str(fonts/'bitstream-vera-license.txt')},indent=2))
print(json.dumps({'reportlab':reportlab.Version,'short':s,'long':l}))
