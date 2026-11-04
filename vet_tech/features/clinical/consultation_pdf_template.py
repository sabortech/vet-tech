"""Dynamic ReportLab layout based on the supplied VetTech visual reference.

Only individual local mascot graphics are reused. Pages, text and tables are
constructed here; no PDF page is used as a background and no remote assets load.
"""
from io import BytesIO
from functools import lru_cache
from pathlib import Path
from threading import BoundedSemaphore, Lock
from xml.sax.saxutils import escape

import reportlab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, LongTable, TableStyle

from .consultation_pdf import ConsultationDocument, ConsultationPDFError

MAX_PDF_BYTES = 2 * 1024 * 1024
RENDER_TIMEOUT_SECONDS = 20
_SLOTS = BoundedSemaphore(2)
_FONT_LOCK = Lock()
_ROOT = Path(__file__).resolve().parents[3]
_ASSETS = _ROOT / 'assets' / 'consultation-pdf'
GREEN = colors.HexColor('#315f3e')
INK = colors.HexColor('#273b2e')
PALE = colors.HexColor('#edf3e8')
LINE = colors.HexColor('#d4e2d2')
MARGIN = 18 * mm


def _fonts():
    with _FONT_LOCK:
        if 'VetTechBody' not in pdfmetrics.getRegisteredFontNames():
            directory = Path(reportlab.__file__).parent / 'fonts'
            pdfmetrics.registerFont(TTFont('VetTechBody', str(directory / 'Vera.ttf')))
            pdfmetrics.registerFont(TTFont('VetTechBold', str(directory / 'VeraBd.ttf')))


def _paragraph(text, *, heading=False, size=None):
    style = ParagraphStyle('vt', fontName='VetTechBold' if heading else 'VetTechBody',
        fontSize=size or (13 if heading else 9), leading=(size or (13 if heading else 9))*1.45,
        textColor=GREEN if heading else INK, spaceAfter=8, splitLongWords=True)
    return Paragraph(escape(str(text)).replace('\n', '<br/>'), style)


@lru_cache(maxsize=2)
def _graphic(name):
    image = ImageReader(str(_ASSETS / name))
    image.getRGBData()
    return image


def _draw_image(canvas, name, x, y, width, opacity=1):
    # Names are constant calls from this module, never clinical inputs or URLs.
    image = _graphic(name)
    w, h = image.getSize()
    canvas.saveState()
    canvas.setFillAlpha(opacity)
    canvas.drawImage(image, x, y, width=width, height=width*h/w, mask='auto')
    canvas.restoreState()


def _cover(canvas, doc, document):
    w,h=A4
    canvas.saveState()
    canvas.setFillColor(PALE);canvas.setStrokeColor(GREEN)
    path=canvas.beginPath();path.moveTo(0,h);path.lineTo(280,h)
    path.lineTo(0,h-210);path.close();canvas.drawPath(path,fill=1,stroke=0)
    canvas.setLineWidth(1)
    for offset in (40,90,140,190):
        canvas.line(0,h-offset,offset/.75,h)
    _draw_image(canvas,'mascote-v.png',w/2-160,h*.49,320,.10)
    _draw_image(canvas,'mascote-v.png',w/2-112,h*.53,224)
    canvas.setFillColor(GREEN);canvas.setFont('VetTechBold',35)
    canvas.drawCentredString(w/2,h*.43,'VetTech')
    canvas.setStrokeColor(colors.HexColor('#769c69'));canvas.setLineWidth(2)
    canvas.line(w/2-88,h*.417,w/2+88,h*.417)
    title=_paragraph('Prontuário da consulta\nveterinária',heading=True,size=19)
    title.style.alignment=1
    tw,th=title.wrap(w-2*MARGIN,90);title.drawOn(canvas,MARGIN,h*.37-th)
    _draw_image(canvas,'mascote-canto.png',w-185,-5,220)
    canvas.setStrokeColor(LINE);canvas.setLineWidth(.6)
    canvas.line(MARGIN,147,w-MARGIN,147)
    # Very long names remain complete in the paginated identification table.
    cover_name=document.pet_name if len(document.pet_name)<=100 else f'Pet nº {document.pet_id}'
    name=_paragraph(cover_name,heading=True,size=12);_,nh=name.wrap(w-2*MARGIN-100,60)
    name.drawOn(canvas,MARGIN,130-nh)
    canvas.setFillColor(INK);canvas.setFont('VetTechBody',9)
    canvas.drawString(MARGIN,92,f'Consulta nº {document.consultation_id} · {dict(document.fields)["Data do atendimento"]}')
    canvas.restoreState()


def _inside(canvas, doc):
    w,h=A4
    canvas.saveState()
    canvas.setFillColor(GREEN);canvas.rect(0,h-24,w,24,fill=1,stroke=0)
    canvas.setFont('VetTechBody',13);canvas.drawString(MARGIN,h-63,'VetTech')
    _draw_image(canvas,'mascote-v.png',w-MARGIN-54,h-77,54)
    canvas.setStrokeColor(LINE);canvas.setLineWidth(.5);canvas.line(MARGIN,h-91,w-MARGIN,h-91)
    _draw_image(canvas,'mascote-v.png',w/2-170,h*.34,340,.075)
    canvas.setFillAlpha(.09);canvas.setFont('VetTechBold',40)
    canvas.drawCentredString(w/2,h*.32 - 8*mm,'VetTech');canvas.setFillAlpha(1)
    canvas.setStrokeColor(LINE);canvas.line(MARGIN,36,w-MARGIN,36)
    canvas.setFillColor(colors.HexColor('#687a6d'));canvas.setFont('VetTechBody',7)
    canvas.drawString(MARGIN,24,'VetTech | Relatório de consulta veterinária')
    canvas.drawRightString(w-MARGIN,24,f'Página {doc.page}')
    canvas.restoreState()


def _table(rows, *, header=False):
    width=A4[0]-2*MARGIN
    data=[[_paragraph(label,heading=header and i==0,size=8.5),_paragraph(value,size=9)]
          for i,(label,value) in enumerate(rows)]
    table=LongTable(data,colWidths=[width*.24,width*.76],repeatRows=1 if header else 0,
        splitByRow=1,splitInRow=1,hAlign='LEFT')
    commands=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),
        ('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),
        ('BOTTOMPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,0),(-1,-1),.35,LINE)]
    if header: commands.append(('BACKGROUND',(0,0),(-1,0),PALE))
    table.setStyle(TableStyle(commands))
    return table


def render_consultation_pdf(document: ConsultationDocument) -> bytes:
    if not _SLOTS.acquire(blocking=False):
        raise ConsultationPDFError('O gerador está ocupado. Tente novamente em instantes.')
    try:
        _fonts()
        buffer=BytesIO()
        pdf=SimpleDocTemplate(buffer,pagesize=A4,leftMargin=MARGIN,rightMargin=MARGIN,
            topMargin=108,bottomMargin=54,title='VetTech — Prontuário da consulta',author='VetTech',pageCompression=1)
        story=[Spacer(1,1),PageBreak(),_paragraph('Prontuário da consulta veterinária',heading=True,size=19),
            _paragraph('Identificação',heading=True),
            _table([('Pet',document.pet_name),('Consulta',f'{document.consultation_id} · Finalizada · {dict(document.fields)["Data do atendimento"]}'),
                    ('Veterinário',f'ID {document.veterinarian_id}')]),Spacer(1,10),_paragraph('Consulta',heading=True),
            _table(document.fields)]
        if document.sections:
            story.extend([Spacer(1,10),_paragraph('Registros vinculados',heading=True)])
            for label,records in document.sections:
                rows=[('Categoria','Registro')]
                for index,record in enumerate(records,1):
                    value='\n'.join(f'{title}: {value}' for title,value in record) or 'Não informado'
                    rows.append((f'{label} · {index}',value))
                story.append(_table(rows,header=True));story.append(Spacer(1,10))
        pdf.build(story,onFirstPage=lambda c,d:_cover(c,d,document),onLaterPages=_inside)
        content=buffer.getvalue()
        if not content.startswith(b'%PDF-') or len(content)>MAX_PDF_BYTES:
            raise ConsultationPDFError('A consulta excede o limite de exportação.')
        return content
    finally:
        _SLOTS.release()
