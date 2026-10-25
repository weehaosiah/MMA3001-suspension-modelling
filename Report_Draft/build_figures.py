"""Publication sized figures from saved traces and saved final predictions only."""
import csv
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color, black, white
import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / 'figures'
OUT.mkdir(exist_ok=True)
W, H = 496.8, 235
BLUE = HexColor('#12648E')
ORANGE = HexColor('#AB632B')

def chart_canvas(name):
    return canvas.Canvas(str(OUT/(name+'.pdf')), pagesize=(W,H))

def panel(c, box, xlim, ylim, xticks, yticks, xlabel, ylabel, title):
    x,y,w,h=box
    def xx(v): return x+(v-xlim[0])/(xlim[1]-xlim[0])*w
    def yy(v): return y+(v-ylim[0])/(ylim[1]-ylim[0])*h
    c.setFillColor(black); c.setFont('Helvetica-Bold',10)
    c.drawString(x,y+h+12,title)
    c.setLineWidth(.4)
    for v in xticks:
        px=xx(v); c.setStrokeColor(HexColor('#DDDDDD')); c.line(px,y,px,y+h)
        c.setFillColor(black); c.setFont('Helvetica',9); c.drawCentredString(px,y-13,str(v))
    for v in yticks:
        py=yy(v); c.setStrokeColor(HexColor('#DDDDDD')); c.line(x,py,x+w,py)
        c.setFillColor(black); c.setFont('Helvetica',9); c.drawRightString(x-5,py-3,str(v))
    c.setStrokeColor(black); c.rect(x,y,w,h)
    c.setFont('Helvetica',9.5); c.drawCentredString(x+w/2,y-29,xlabel)
    c.saveState(); c.translate(x-32,y+h/2); c.rotate(90); c.drawCentredString(0,0,ylabel); c.restoreState()
    return xx,yy

def clip(c,box):
    c.saveState(); p=c.beginPath(); p.rect(*box); c.clipPath(p,stroke=0,fill=0)

def line(c, xs, ys, xx, yy, color):
    c.setStrokeColor(color); c.setLineWidth(1.2); path=c.beginPath()
    for i,(a,b) in enumerate(zip(xs,ys)):
        if i==0:path.moveTo(xx(a),yy(b))
        else:path.lineTo(xx(a),yy(b))
    c.drawPath(path)

def save(c,name):
    c.save(); d=pdfium.PdfDocument(str(OUT/(name+'.pdf')))
    d[0].render(scale=3).to_pil().save(OUT/(name+'.png'))

rows=list(csv.DictReader((ROOT/'Suspension_Model/final_evaluation_v1/test_predictions.csv').open()))
c=chart_canvas('test_comparison')
boxes=[(42,55,185,145),(292,55,185,145)]
x,y=panel(c,boxes[0],(35,46),(35,46),[36,40,44],[36,40,44], 'Simulated peak A (mm)','Predicted peak A (mm)','Peak agreement')
clip(c,boxes[0]); c.setStrokeColor(HexColor('#666666')); c.setDash(3,2); c.line(x(35),y(35),x(46),y(46)); c.setDash()
for pred,color in [('linear_prediction_mm',ORANGE),('svr_prediction_mm',BLUE)]:
    c.setFillColor(color)
    for r in rows:c.circle(x(float(r['A_mm'])),y(float(r[pred])),1.6,stroke=0,fill=1)
c.restoreState()
x,y=panel(c,boxes[1],(35,46),(-.5,.5),[36,40,44],[-.4,0,.4], 'Simulated peak A (mm)','Simulated minus predicted (mm)','Residuals on a common scale')
clip(c,boxes[1]);c.setStrokeColor(HexColor('#555555'));c.line(x(35),y(0),x(46),y(0))
for pred,color in [('linear_residual_mm',ORANGE),('svr_residual_mm',BLUE)]:
    c.setFillColor(color)
    for r in rows:c.circle(x(float(r['A_mm'])),y(float(r[pred])),1.6,stroke=0,fill=1)
c.restoreState()
for tx,color,label in [(85,ORANGE,'Linear regression'),(275,BLUE,'Frozen SVR')]:
    c.setFillColor(color); c.circle(tx,13,2.5,stroke=0,fill=1);c.setFillColor(black);c.setFont('Helvetica',10);c.drawString(tx+8,9,label)
save(c,'test_comparison')

rows=list(csv.DictReader((ROOT/'Suspension_Model/results/nominal_trace_1ms.csv').open()))
print('trace columns',list(rows[0]))
# The plotting source is a preserved numerical trace, without another integration.
times=[float(r['time_s']) for r in rows]
values=[float(r['relative_m'])*1000 for r in rows]
c=chart_canvas('nominal_motion')
boxes=[(42,55,185,145),(292,55,185,145)]
x,y=panel(c,boxes[0],(0,2.5),(-30,45),[0,1,2],[-20,0,20,40],'Time since bump starts (s)','Relative displacement (mm)','Motion through 2.5 s')
clip(c,boxes[0]);line(c,times,values,x,y,BLUE)
c.setStrokeColor(ORANGE);c.setLineWidth(.8);c.setDash(3,2);c.line(x(.5),y(-30),x(.5),y(45));c.setDash();c.restoreState()
x,y=panel(c,boxes[1],(.5,3),(-5,5),[.5,1.5,2.5],[-4,-2,0,2,4],'Time since bump starts (s)','Relative displacement (mm)','Settling band enlarged')
clip(c,boxes[1]);c.setFillColor(HexColor('#DDEBDD'));c.rect(x(.5),y(-1),x(3)-x(.5),y(1)-y(-1),stroke=0,fill=1)
line(c,times,values,x,y,BLUE);c.setStrokeColor(HexColor('#32794D'));c.setDash(2,2);c.line(x(1.769331763),y(-5),x(1.769331763),y(5));c.setDash();c.restoreState()
c.setFillColor(black);c.setFont('Helvetica',9);c.drawString(44,9,'Dashed orange  bump exit at 0.50 s');c.drawString(292,9,'Dashed green  final band entry')
save(c,'nominal_motion')
