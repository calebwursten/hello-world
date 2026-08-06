#!/usr/bin/env python3
"""55A Hall St - clean, to-scale floor plan redrawn from hand sketch.
Scale: 3/16" = 1'-0"  (1 real inch = 1.125 pt). Letter portrait.
All dimension values transcribed verbatim from the original sketch (inches).
"""
import math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

OUT = "55A_Hall_St_floor_plan.pdf"
PW, PH = letter  # 612 x 792

S = 1.125          # pt per real inch (1:64 -> 3/16" = 1')
X0 = 312.0         # page x of the main wall plane (real x=0)
Y0 = 726.0         # page y of the top wall (real y=0); page y decreases downward

def X(x): return X0 + x * S
def Y(y): return Y0 - y * S

# ---- geometry (real inches; x=0 main left wall plane, y=0 top wall) ----
# Right wall: vertical at 173 down to bath bottom (y=234), then tapers to 120
# at the bottom (y=516) - the sketch draws the lean in the living band, and this
# honors top 25+148=173 and bottom 34.5+120=154.5 with step-out 40/34.5.
def RWX(y):
    return 173.0 if y <= 234 else 173.0 - 53.0*(y-234.0)/282.0

WALLS = [
    # exterior envelope
    ((0,0),(173,0)),                    # top wall
    ((173,0),(173,234)),                # right wall, upper (plumb)
    ((173,234),(120,516)),              # right wall, living band (tapers per dims)
    ((120,516),(-34.5,516)),            # bottom wall
    ((-34.5,516),(-40,301)),            # living left wall
    ((-40,301),(0,301)),                # jog / step-out
    # main wall plane (x=0) with openings as sketched
    ((0,0),(0,118.3)),
    ((0,126.5),(0,200.5)),
    ((0,218.5),(0,261.7)),
    ((0,287.1),(0,301)),
    # annex (left Bed)
    ((0,126.5),(-38,126.5)),            # chamfer stub cap (38")
    ((-38,126.5),(-51.7,146)),          # 55 deg diagonal
    ((0,146),(-180.7,146)),             # annex top edge, full to corridor wall (129" to diagonal foot)
    ((-180.7,146),(-180.7,259.5)),      # annex left edge (113.5")
    ((-180.7,259.5),(0,259.5)),         # annex bottom edge, closes to corridor wall
    ((-125.7,259.5),(-125.7,227.5)),    # step (32")
    ((-125.7,227.5),(0,227.5)),         # annex bottom shelf (strip north face)
    # bed room pocket stub at 25" (pen-gap preserved; lower piece meets hatch block)
    ((25,0),(25,40)),
    ((25,64),(25,76)),
    # bed/kitchen wall with door gap as sketched
    ((0,96),(122.3,96)),
    ((140.4,96),(173,96)),
    # bath (closed rectangle as sketched; right side = right wall)
    ((97,160),(173,160)),               # bath top
    ((97,160),(97,234)),                # bath left
    ((97,234),(173,234)),               # bath bottom (76")
]

HATCH_A = [(0,76),(25,76),(25,96),(0,96)]                     # 25x20 block, bed room
HB_T, HB_B, HB_D = 288.5, 439.0, 24.0                          # living block (proportional)
HATCH_B = [(RWX(HB_T)-HB_D,HB_T),(RWX(HB_T),HB_T),
           (RWX(HB_B),HB_B),(RWX(HB_B)-HB_D,HB_B)]

ROOMS = [("Bed",(86.5,48)),("Kitchen",(86.5,130)),("Bath",(135,199)),
         ("Bed",(-118,178)),("Living",(45,382))]

c = canvas.Canvas(OUT, pagesize=letter)
c.setTitle("55A Hall St - Floor Plan (to scale)")
c.setAuthor("Redrawn from field sketch")

# ---------- helpers ----------
def line(p,q,w=2.0,color=(0,0,0)):
    c.setLineWidth(w); c.setStrokeColorRGB(*color)
    c.setLineCap(1)
    c.line(X(p[0]),Y(p[1]),X(q[0]),Y(q[1]))

def tick(px,py,ang=45,l=4.5):
    dx = l*math.cos(math.radians(ang))/2; dy = l*math.sin(math.radians(ang))/2
    c.setLineWidth(1.1); c.line(px-dx,py-dy,px+dx,py+dy)

def dim_h(x1,x2,y,off_pt,label,text_above=True):
    """horizontal dimension between real x1..x2 at wall line y; dim line offset off_pt pts above wall"""
    yd = Y(y) + off_pt
    c.setStrokeColorRGB(0,0,0); c.setLineWidth(0.5)
    for xx in (x1,x2):
        e0 = Y(y); step = 4 if yd > e0 else -4
        c.line(X(xx), e0 + step*0.8, X(xx), yd + step*0.75)
    c.line(X(x1),yd,X(x2),yd)
    tick(X(x1),yd); tick(X(x2),yd)
    c.setFont("Helvetica",8.2)
    tx = (X(x1)+X(x2))/2
    ty = yd + 2.5 if text_above else yd - 9
    c.drawCentredString(tx,ty,label)

def dim_v(y1,y2,x,off_pt,label,text_side=1,label_dy=0):
    """vertical dimension between real y1..y2; dim line at page x = X(x)+off_pt"""
    xd = X(x) + off_pt
    c.setStrokeColorRGB(0,0,0); c.setLineWidth(0.5)
    c.line(xd,Y(y1),xd,Y(y2))
    tick(xd,Y(y1)); tick(xd,Y(y2))
    c.setFont("Helvetica",8.2)
    ym = (Y(y1)+Y(y2))/2 - 3 + label_dy
    if text_side>0: c.drawString(xd+4,ym,label)
    else: c.drawRightString(xd-4,ym,label)

def dim_v_ext(y1,y2,wall_x1,wall_x2,xd_real,label):
    """vertical dim with horizontal extension lines from wall points (right-side chain)"""
    xd = X(xd_real)
    c.setLineWidth(0.5); c.setStrokeColorRGB(0,0,0)
    for yy,wx in ((y1,wall_x1),(y2,wall_x2)):
        c.line(X(wx)+4,Y(yy),xd+3,Y(yy))
    c.line(xd,Y(y1),xd,Y(y2))
    tick(xd,Y(y1)); tick(xd,Y(y2))
    c.setFont("Helvetica",8.2)
    c.drawString(xd+5,(Y(y1)+Y(y2))/2-3,label)

def hatch(poly, spacing=4.0):
    c.saveState()
    p = c.beginPath()
    p.moveTo(X(poly[0][0]),Y(poly[0][1]))
    for pt in poly[1:]: p.lineTo(X(pt[0]),Y(pt[1]))
    p.close()
    c.setLineWidth(1.0); c.drawPath(p,stroke=1,fill=0)
    c.clipPath(p,stroke=0,fill=0)
    xs=[X(p_[0]) for p_ in poly]; ys=[Y(p_[1]) for p_ in poly]
    x0,x1=min(xs),max(xs); y0,y1=min(ys),max(ys)
    c.setLineWidth(0.5)
    n=int(((x1-x0)+(y1-y0))/spacing)+2
    for i in range(n):
        b=y0-(x1-x0)+i*spacing
        c.line(x0,b,x1,b+(x1-x0))
    c.restoreState()

# ---------- draw ----------
for p,q in WALLS: line(p,q,2.0)
hatch(HATCH_A); hatch(HATCH_B)

c.setFillColorRGB(0,0,0)
for name,(rx,ry) in ROOMS:
    c.setFont("Helvetica-Bold",11)
    c.drawCentredString(X(rx),Y(ry)-4,name)

# ---- dimensions (verbatim values) ----
dim_h(0,25,0,16,'25"'); dim_h(25,173,0,16,'148"')
dim_v(0,76,0,-14,'76"',text_side=-1); dim_v(76,96,0,-14,'20"',text_side=-1)
dim_v_ext(0,96,   173,173,187,'96"')
dim_v_ext(96,160, 173,173,187,'64"')
dim_v_ext(160,234,173,173,187,'74"')
dim_v_ext(234,516,173,120,187,'282"')
dim_h(97,173,234,-12,'76"',text_above=False)
dim_h(-180.7,-51.7,146,12,'129"')
dim_h(-38,0,126.5,15,'38"')
dim_v(146,259.5,-180.7,-14,'113.5"',text_side=-1)
dim_v(227.5,259.5,-125.7,-10,'32"',text_side=-1)
dim_h(-180.7,-125.7,259.5,-12,'55"',text_above=False)
# 55 degree angle at diagonal foot (angle between annex top edge and diagonal)
c.setLineWidth(0.5)
foot = (X(-51.7),Y(146))
p = c.beginPath(); r=15
p.arc(foot[0]-r,foot[1]-r,foot[0]+r,foot[1]+r,0,55)
c.drawPath(p)
c.setFont("Helvetica",8.2)
c.drawString(foot[0]+16,foot[1]+3,u'55°')
dim_h(-34.5,0,516,-16,'34.5"',text_above=False)
dim_h(0,120,516,-16,'120"',text_above=False)
# floating 40" near step-out (as on sketch; referent not identified on original)
c.setFont("Helvetica",8.2)
c.drawRightString(X(-44),Y(316),'40"')

# ---------- title block ----------
tb_top = 112
c.setLineWidth(0.8); c.setStrokeColorRGB(0,0,0)
c.line(36,tb_top,576,tb_top)
c.setFont("Helvetica-Bold",14)
c.drawString(36,tb_top-18,"55A HALL ST — FLOOR PLAN")
c.setFont("Helvetica",8.5)
c.drawString(36,tb_top-31,"Redrawn to scale from hand-measured field sketch")
c.setFont("Helvetica-Bold",8.5)
c.drawString(36,tb_top-44,'Scale: 3/16" = 1\'-0"  (1:64)')
c.setFont("Helvetica",7.5)
c.drawString(36,tb_top-56,"All dimensions in inches, as noted on sketch.")
c.drawString(36,tb_top-66,"Not a survey — verify on site. 2026-08-06")

# scale bar: 0-2-4-8 ft
sb_x, sb_y = 152, tb_top-46
ft = 12*S
c.setLineWidth(0.8)
for a,b,fill in [(0,2,1),(2,4,0),(4,8,1)]:
    c.rect(sb_x+a*ft, sb_y, (b-a)*ft, 5, stroke=1, fill=fill)
c.setFont("Helvetica",6.5)
for v in (0,2,4,8):
    c.drawCentredString(sb_x+v*ft, sb_y+8, str(v))
c.drawString(sb_x+8*ft+5, sb_y, "ft")

# notes (right column)
nx = 306
notes = [
    "1. Room names and all dimension values are copied verbatim from the sketch.",
    "2. Wall openings (gaps) and the two hatched features are not dimensioned on",
    "    the sketch; they are drawn in proportion to the sketch and left unlabeled.",
    "3. Sketch gives overall width 25\"+148\" = 173\" at top and 34.5\"+120\" = 154.5\"",
    "    at bottom; the right wall is drawn tapering in the living room so both stay",
    "    true, matching the lean in the sketch. Verify on site.",
    "4. The 40\" note beside the living-room step-out is placed as on the sketch;",
    "    the step-out is drawn 40\" deep at the jog (34.5\" at the bottom wall).",
    "5. Walls are single-line as sketched; wall thicknesses were not recorded.",
]
c.setFont("Helvetica-Bold",7.2); c.drawString(nx,tb_top-14,"NOTES")
c.setFont("Helvetica",6.8)
yy = tb_top-24
for n in notes:
    c.drawString(nx,yy,n); yy -= 9

c.showPage(); c.save()
print("wrote", OUT)
