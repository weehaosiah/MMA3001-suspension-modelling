from pathlib import Path
import json
import hashlib
from copy import deepcopy

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
DOCX = OUT / 'MMA3001_suspension_report_draft.docx'
doc = Document()
# The bundled base document carries a title border and an odd and even header
# setting. Remove both so this report has plain headings and a consistent header.
for element in list(doc.settings.element):
    if element.tag == qn('w:evenAndOddHeaders'):
        doc.settings.element.remove(element)
for border in list(doc.styles.element.iter(qn('w:pBdr'))):
    border.getparent().remove(border)
sec = doc.sections[0]
sec.page_width = Inches(8.5)
sec.page_height = Inches(11)
sec.top_margin = Inches(.78)
sec.bottom_margin = Inches(.72)
sec.left_margin = sec.right_margin = Inches(.8)
sec.header_distance = sec.footer_distance = Inches(.3)

styles = doc.styles
for name in ['Normal', 'Body Text']:
    st = styles[name]
    st.font.name = 'Calibri'
    st.font.size = Pt(11)
    st.font.color.rgb = RGBColor.from_string('171717')
    st.paragraph_format.line_spacing = 1.08
    st.paragraph_format.space_after = Pt(7)
for name, size in [('Title', 23), ('Heading 1', 16), ('Heading 2', 12)]:
    st = styles[name]
    st.font.name = 'Calibri'
    st.font.size = Pt(size)
    st.font.color.rgb = RGBColor.from_string('000000')
    st.font.bold = True
    st.paragraph_format.space_before = Pt(8 if name != 'Title' else 0)
    st.paragraph_format.space_after = Pt(8)
    st.paragraph_format.keep_with_next = True
styles['Caption'].font.name = 'Calibri'
styles['Caption'].font.size = Pt(9)
styles['Caption'].font.color.rgb = RGBColor.from_string('444444')
styles['Caption'].font.bold = False
styles['Caption'].paragraph_format.space_after = Pt(8)

h = sec.header.paragraphs[0]
h.text = ''
f = sec.footer.paragraphs[0]
f.alignment = WD_ALIGN_PARAGRAPH.RIGHT
field = OxmlElement('w:fldSimple')
field.set(qn('w:instr'), 'PAGE')
f._p.append(field)

def p(text='', style=None):
    return doc.add_paragraph(text, style)

def heading(text):
    global _new_page
    h = doc.add_heading(text, 1)
    if _new_page:
        h.paragraph_format.page_break_before = True
        _new_page = False

def sub(text):
    doc.add_heading(text, 2)

def page():
    global _new_page
    _new_page = True

_new_page = False

def flag(code, text):
    para = p()
    run = para.add_run(f'Student review {code}  ')
    run.bold = True
    run.font.color.rgb = RGBColor.from_string('7A3E13')
    para.add_run(text)

def table(headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.autofit = False
    if widths:
        for c, w in zip(t.columns, widths):
            c.width = Inches(w)
    for cell, text in zip(t.rows[0].cells, headers):
        cell.text = text
        shade = OxmlElement('w:shd'); shade.set(qn('w:fill'), 'EAECEF')
        cell._tc.get_or_add_tcPr().append(shade)
        for run in cell.paragraphs[0].runs:
            run.bold = True
    repeat = OxmlElement('w:tblHeader'); t.rows[0]._tr.get_or_add_trPr().append(repeat)
    for row in rows:
        for cell, text in zip(t.add_row().cells, row):
            cell.text = str(text)
    for row in t.rows:
        row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
        for i, cell in enumerate(row.cells):
            if widths:
                cell.width = Inches(widths[i])
            tcpr = cell._tc.get_or_add_tcPr()
            margins = OxmlElement('w:tcMar')
            for side in ['top', 'bottom', 'left', 'right']:
                el = OxmlElement('w:'+side); el.set(qn('w:w'), '45' if side in ['top','bottom'] else '75'); el.set(qn('w:type'), 'dxa'); margins.append(el)
            tcpr.append(margins)
            for para in cell.paragraphs:
                para.paragraph_format.space_after = Pt(2)
                para.paragraph_format.line_spacing = 1.02
                for run in para.runs:
                    run.font.size = Pt(10.5)
    return t

def fig(rel, width, caption, alt):
    para = p()
    para.paragraph_format.keep_with_next = True
    para.paragraph_format.space_after = Pt(2)
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    shape = para.add_run().add_picture(str(ROOT / rel), width=Inches(width))
    shape._inline.docPr.set('descr', alt)
    p(caption, 'Caption')

def mr(text):
    e = OxmlElement('m:r'); t = OxmlElement('m:t'); t.text = text; e.append(t); return e

def seq(*items):
    return [mr(x) if isinstance(x, str) else x for x in items]

def scr(base, low=None, high=None):
    kind = 'm:sSubSup' if low is not None and high is not None else ('m:sSub' if low is not None else 'm:sSup')
    o = OxmlElement(kind)
    for tag, value in [('m:e', base), ('m:sub', low), ('m:sup', high)]:
        if value is None: continue
        child = OxmlElement(tag)
        for x in (seq(value) if isinstance(value, str) else value): child.append(x)
        o.append(child)
    return o

def frac(a, b):
    e = OxmlElement('m:f')
    for tag, val in [('m:num', a), ('m:den', b)]:
        q = OxmlElement(tag)
        for x in val: q.append(x)
        e.append(q)
    return e

def eq(items):
    para = p()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.space_after = Pt(8)
    math = OxmlElement('m:oMath')
    for x in items: math.append(mr(x) if isinstance(x, str) else x)
    para._p.append(math)

def link(para, label, url):
    from docx.opc.constants import RELATIONSHIP_TYPE as RT
    rel = para.part.relate_to(url, RT.HYPERLINK, is_external=True)
    hyp = OxmlElement('w:hyperlink'); hyp.set(qn('r:id'), rel)
    r = OxmlElement('w:r'); props = OxmlElement('w:rPr')
    col = OxmlElement('w:color'); col.set(qn('w:val'), '174D72'); props.append(col)
    r.append(props); t = OxmlElement('w:t'); t.set(qn('xml:space'),'preserve'); t.text=label; r.append(t); hyp.append(r); para._p.append(hyp)

# Page 1
doc.add_heading('Predicting peak suspension travel with numerical simulation and regression', 0)
p('MMA3001 Numerical Methods and Machine Learning\nIndividual project report draft  |  22 October 2026')
flag('R1', 'Add your name and student ID. Replace the marked review prompts with your own explanations before submission. This is an AI assisted draft, not a declaration of independent authorship or completed student reflection.')
heading('1  Engineering question and principal finding')
p('This project asks how suspension spring stiffness and damping affect the largest dynamic movement between a vehicle body and wheel when a generic vehicle corner crosses one prescribed road bump. A verified numerical model supplies response labels, and regression models estimate the same peak for previously unseen stiffness and damping pairs within a fixed study domain. The intended use is rapid comparison of simulated setups before deciding which cases merit a full response analysis.')
p('The development selected support vector regression model achieved a root mean square error of 0.029796 mm on 100 reserved simulated cases, compared with 0.199436 mm for linear regression. A separate nine setup benchmark measured a mean of single case median warm query times of 0.163470 ms for SVR and 222.637844 ms for the peak only simulation path. These results support a fast surrogate for the adopted simulated peak. They do not establish measured vehicle accuracy or replace the simulation outputs needed to interpret post bump behaviour. [E3, E4, E6]')
sub('The engineering target')
p('The primary response A is the maximum absolute body minus wheel displacement over the full checked response, measured from static equilibrium and reported in millimetres. The observation includes the bump and subsequent motion. A larger magnitude in either direction increases A. This is dynamic travel about equilibrium; it excludes static sag and is neither peak to peak range nor accumulated movement. [E1]')
p('The post bump maximum and the time to remain within a ±1 mm relative displacement band are separate physical diagnostics. The learned models predict A alone. In particular, a small post bump maximum does not establish short settling, and relative displacement near zero does not establish that either mass has stopped moving. [E5]')
sub('Scope and evidence status')
p('The study uses a passive linear quarter car with fixed body mass, wheel mass, tyre stiffness and bump. Only spring stiffness and damping vary. It is a controlled simulation study, without measured car calibration or claims about comfort, grip, safety or lap time. The scientific evidence is preserved at the 11 October checkpoint 8ba9808. A later local profiling supplement dated 12 October is identified explicitly in Section 7; the supplied records do not establish that it was uploaded. [E1, E6, E7]')
flag('R2', 'Explain your personal engineering motivation and why this restricted question is useful. The records do not establish your own rationale or a physical design acceptance threshold.')

# Page 2
page(); heading('2  Model inputs outputs and assumptions')
p('Upward displacements zₛ and zᵤ describe the sprung body and unsprung wheel assembly relative to their static equilibrium positions. The suspension spring and viscous damper act between them; a linear tyre spring connects the wheel to the prescribed road r. The governing model follows the quarter car formulation in [1]. With active force absent, the equations are')
eq([scr('m','s'), scr('z','s','″'), ' = −',scr('k','s'),'(',scr('z','s'),' − ',scr('z','u'),') − ',scr('c','s'),'(',scr('z','s','′'),' − ',scr('z','u','′'),')'])
eq([scr('m','u'),scr('z','u','″'),' = ',scr('k','s'),'(',scr('z','s'),' − ',scr('z','u'),') + ',scr('c','s'),'(',scr('z','s','′'),' − ',scr('z','u','′'),') + ',scr('k','t'),'(r − ',scr('z','u'),')'])
p('The four state variables are ordered as body displacement, body velocity, wheel displacement and wheel velocity. All start at zero. Constant gravitational loads are already balanced in the static equilibrium reference, so gravity does not appear in these dynamic equations. Positive body minus wheel displacement means extension. Equal displacements imply zero relative displacement, without implying zero velocities. [E1]')
table(['Quantity', 'Adopted value or domain', 'Role'], [
    ['Body and wheel mass', '365.4 kg and 43.0 kg', 'Fixed'],
    ['Tyre stiffness', '350,000 N/m', 'Fixed'],
    ['Suspension stiffness kₛ', '18,000 to 30,000 N/m\nNominal 24,000 N/m', 'Varied input'],
    ['Suspension damping cₛ', '1,594.8 to 2,658.0 N s/m\nNominal 2,126.4 N s/m', 'Varied input'],
    ['Bump height and duration', '0.050 m and 0.50 s', 'Fixed input'],
], [1.65,3.4,1.85])
p('The nominal coefficients are the published generic front corner baseline in Soong et al., Table 2 [2]. They are not measurements of an identified vehicle. The ±25% stiffness and damping ranges are project choices. The raised cosine bump shape is adapted from [3]; its 0.50 s duration is a project choice, rather than the source example duration.')
eq(['r(t) = ',frac(seq('h'),seq('2')),'[1 − cos(',frac(seq('2πt'),seq('τ')),')],   0 ≤ t ≤ τ;    r(t) = 0 otherwise'])
sub('Interface and output meaning')
p('The ML query accepts a nonempty N by 2 numeric array with columns kₛ in N/m and cₛ in N s/m. Guards reject malformed shapes, nonfinite values and inputs outside the inclusive limits. It returns N peaks in mm. Simulator configuration guards require positive physical parameters and solver controls; zero bump height is allowed for checks. Accepting other simulator configurations does not validate them. [E1, E3]')
p('The model omits tyre damping, pitch and roll, nonlinear springs, bump stops, active forces and contact loss dynamics. The total tyre force screen is a validity check, not a contact loss model or a physical travel clearance calculation.')
flag('R3', 'Explain the spring and damper force signs and why the equilibrium reference removes constant gravity. Confirm that you can distinguish the ML input interface from the larger simulator configuration.')

# Page 3
page(); heading('3  Numerical method and verification')
p('SciPy RK45 integrates the four state initial value problem using an embedded Runge Kutta 5(4) pair [4]. Adaptive internal steps control estimated local integration error. Dense output is then observed on a separate time grid to estimate response peaks and band crossings. Tightening solver tolerances and refining the observation grid answer different accuracy questions; a fine plotted curve alone does not verify integration.')
p('The adopted label settings are relative tolerance 10⁻⁶, absolute tolerances [10⁻⁹ m, 10⁻⁸ m/s, 10⁻⁹ m, 10⁻⁸ m/s], maximum internal step 0.005 s, 1 ms observations and a 5 s horizon. The bump and flat road segments share the complete position and velocity state at 0.50 s. Resetting that state would erase the remaining physical response. [E1, E2]')
sub('Checks and acceptance criteria')
p('Nine combinations of low, nominal and high stiffness and damping were checked against tighter RK45 integration, finer observation grids, a 10 s horizon and classical RK4 at 0.5 and 0.25 ms. The declared numerical agreement criteria were 0.05 mm for peaks and 0.01 s for settling, with consistent resolved status. These are project numerical criteria, not exact label error bars or engineering design requirements. [E2]')
table(['Verification comparison across nine pilots', 'Largest observed difference in A'],[
    ['Adopted settings versus tighter longer reference', '0.000464924 mm'],
    ['Solver refinement with observation grid fixed', '0.000000575 mm'],
    ['Observation grid refinement from 1 to 0.5 ms', '0.000464873 mm'],
    ['Observation horizon extended from 5 to 10 s', '0 mm'],
    ['RK4 at 0.5 ms versus RK45 on the same grid', '0.0000000225 mm'],
    ['RK4 at 0.25 ms versus RK45 on the same grid', '0.0000000128 mm'],
], [4.85,2.05])
p('The largest adopted versus reference post bump peak difference was 7.47 × 10⁻⁷ mm. Across the 0.5, 1 and 2 mm settling bands, the largest settling difference was 8.86 × 10⁻⁶ s. Observation resolution dominated the measured A discrepancy in these pilots; all discrepancies remained below the adopted limits. The evidence therefore supported retaining the less expensive label settings within this checked study. [E2]')
p('A clamped wheel analytical diagnostic checked the body equation, with maximum position discrepancy 3.80 × 10⁻¹³ m. A zero road check, state continuity, nonincreasing post bump energy, contact and tail checks supplied complementary evidence. All nine pilots passed their declared checks. RK4 shares the force function with RK45, and the reduced diagnostic is not an analytical solution of the full two mass system. Agreement therefore cannot eliminate shared formulation errors. [E2]')
p('Each later dataset row also received eligibility, contact and tail checks. The full refinement programme covered nine pilots, rather than all 400 setups. These results establish observed numerical consistency, not a certified continuous time error bound or agreement with a real vehicle.')
flag('R4', 'Explain why solver refinement, observation refinement and longer observation are all needed, and what the energy tail check adds. Do not substitute the number of passing software tests for this reasoning.')

# Page 4
page(); heading('4  Dataset and model development')
p('Each dataset row represents one complete stiffness and damping setup and its simulated response, rather than one time sample. The design contains 400 distinct pairs: a 15 by 15 training grid with 225 rows, 75 uniformly sampled validation pairs using seed 3001, and 100 uniformly sampled reserved test pairs using seed 3002. The nine pilot labels were reused only in training; the remaining 391 labels required new integrations. [E3]')
p('All 400 labels passed the adopted eligibility checks. The smallest sampled total tyre force was 2,398.809 N and the largest terminal relative displacement energy bound was 0.011531 mm. These support label eligibility under this model, without proving every unobserved point in the continuous parameter domain. The generated labels are project data, not downloaded experimental observations. [E3]')
sub('A credible baseline and a nonlinear alternative')
p('Linear regression supplies an interpretable affine baseline for A as a function of stiffness and damping. The alternative is support vector regression with a radial basis function kernel. It combines similarities to support vectors to represent a curved response surface, while regularisation and an epsilon insensitive loss limit the fitting incentive for small residuals. Although the motion equations are linear in the state variables, changing their coefficients changes the full trajectory and its peak time; the peak need not be linear in the two parameters. [5, E3]')
p('Each pipeline fitted its own StandardScaler using only the 225 training inputs during development. Scaling prevents the different numerical scales of stiffness and damping from dominating kernel distances. Target values remained in mm. One linear model and 18 predeclared SVR candidates used the same training and validation rows. The SVR search used C = 1, 10 or 100, gamma = 0.1, 1 or 10, and epsilon = 0.05 or 0.20 mm. [E3]')
table(['Development metric in mm', 'Linear regression', 'Selected SVR'],[
    ['Training RMSE', '0.220778', '0.034579'],
    ['Validation RMSE', '0.199456', '0.031088'],
    ['Validation MAE', '0.159690', '0.027277'],
    ['Validation maximum absolute error', '0.485281', '0.059600'],
], [3.6,1.65,1.65])
p('Selection minimised validation RMSE, giving C = 100, gamma = 1 and epsilon = 0.05 mm, with 49 support vectors in the development fit. The selected SVR improved the sampled validation errors over the linear baseline. Epsilon is the training loss tube, not a guaranteed prediction error, numerical tolerance or safety margin. [E3]')
sub('Sensitivity of selection to numerical labels')
p('A check recomputed the 75 validation labels with tighter settings while preserving predictions. Maximum label change was 0.000678 mm and RMS change 0.000310 mm. The 0.001398 mm score gap to the next SVR exceeded twice that RMS change; replacing the reference labels preserved the ranking. This supports selection under this refinement, without guaranteeing the same choice on another dataset. Reserved test responses did not inform development. [E3]')
flag('R5', 'Explain why validation may influence selection while the reserved test must remain outside that process, and why each scaler is fitted only on the permitted fitting rows.')

# Page 5
page(); heading('5  Once only held out evaluation')
p('The final plan froze the selected SVR settings and the linear comparator before the reserved response values were accessed. Both pipelines were freshly refitted on the same 300 original development rows, comprising the former training and validation sets. Each final scaler therefore learned from those 300 inputs. The tighter validation labels remained a verification reference and were not substituted into fitting. The final SVR had 45 support vectors. [E4]')
p('The saved order is plan freeze, completed refits, then first test response access. The UTC timestamps correspond to 5 October 2026 in Sydney. All 100 reserved rows matched the frozen setup identities and remained eligible; predictions were finite and positive. Residual means simulated minus predicted, so a positive value indicates underprediction. RMSE penalises larger residuals more strongly than MAE. [E4]')
table(['Metric on the same 100 test setups', 'Linear regression', 'Frozen SVR'],[
    ['RMSE in mm', '0.199436', '0.029796'],
    ['MAE in mm', '0.161225', '0.026311'],
    ['Maximum absolute error in mm', '0.435026', '0.051826'],
    ['Maximum underprediction in mm', '0.435026', '0.051696'],
    ['Mean residual in mm', '−0.013453', '+0.002502'],
    ['R squared', '0.994254', '0.999872'],
], [3.7,1.6,1.6])
fig('Report_Draft/figures/test_comparison.png', 6.9,
    'Figure 1  The two frozen refits on the same 100 cases, replotted from saved predictions. Residuals share one scale. Source E4.',
    'Predicted versus simulated peak and residuals versus simulated peak for both frozen models on the same 100 cases.')
p('SVR had lower observed errors on these simulated test cases, consistent with its prior development selection. The frozen plan declared no engineering acceptance threshold. Neither high R squared nor the largest observed error supplies a worst case guarantee, physical clearance allowance or real vehicle validation. [E4]')
p('The test is now consumed. No model preference or settings changed after access. Any subsequent test informed tuning requires new independent evaluation evidence; these 100 cases cannot be relabelled as untouched. Likewise, errors on the 300 refit rows are fitting errors, rather than fresh validation evidence.')

# Page 6
page(); heading('6  Peak movement and settling answer different questions')
p('The refined nominal full response peak is 40.571155 mm at 0.442 s, in extension. The post bump maximum is 31.891620 mm at the inclusive 0.50 s exit boundary. Later compression reaches approximately −20.427 mm at 0.77075 s. Motion therefore persists after exit, although the nominal largest absolute excursion occurs earlier. [E1, E5]')
fig('Report_Draft/figures/nominal_motion.png', 6.9,
    'Figure 2  Saved 1 ms trace. Left shows the first 2.5 s of the 5 s response; right enlarges the ±1 mm band and clips earlier peaks. Source E1.',
    'Road bump, full body minus wheel displacement, and enlarged post bump settling view showing sustained entry at about 1.769 seconds.')
p('Settling is the final sustained entry of relative displacement into ±1 mm, measured from bump exit. The nominal estimate is 1.269332 s after exit, with at least one observed second inside the band and additional numerical and tail checks. A first zero crossing or first band entry is insufficient. A ±0.5 mm band gives 1.644586 s and ±2 mm gives 1.174273 s, so the chosen band must accompany any reported settling time. It is a project tolerance. [E2, E5]')
table(['Stiffness at nominal damping', 'A in mm', 'Post bump peak in mm', 'Settling after exit in s'],[
    ['18,000 N/m', '39.343201', '33.663539', '1.376665'],
    ['24,000 N/m', '40.571155', '31.891621', '1.269332'],
    ['30,000 N/m', '40.848021', '28.673449', '1.445348'],
], [2.3,1.2,1.7,1.7])
p('In these saved cases, increasing stiffness from nominal to 30,000 N/m lowers the post bump peak while increasing both A and settling time. All 225 training post bump maxima occur at the exit boundary, so they must not be described as later rebound peaks. [E5]')

# Page 7
page(); heading('7  Runtime comparison and performance analysis')
p('The bounded runtime study compares paths returning the same scalar A at nine previously verified setups. Five measured rounds rotate method order with one numerical library thread. Input guards and scaling are included. Each ML timing observation averages 1,000 real calls to reduce timer noise; its spread is not the distribution of individual request latency. Imports, model loading, file operations, plotting and offline label generation and training are excluded. [E6]')
table(['Warm timing in ms', 'Simulation for A', 'Linear', 'SVR'],[
    ['Mean of nine single case medians', '222.637844', '0.126471', '0.163470'],
    ['Median time for one nine row batch', '2,014.271000', '0.127570', '0.182364'],
], [3.1,1.4,1.2,1.2])
p('For these warm single queries, the simulation to SVR ratio is approximately 1,362. The nine row batch ratio is approximately 11,045, reflecting different batching behaviour. These ratios are local query measurements; they do not measure total project speedup or establish a universal hardware result. The benchmark used existing pilots and frozen models, without new training data or a new test accuracy analysis. All seven saved benchmark checks passed. [E6]')
p('Linear regression is somewhat faster and simpler to interpret than SVR, but both query times are small relative to the measured simulation path. The selected SVR trades a modest query cost increase for lower sampled prediction error. Simulation remains necessary for the trajectory, post bump movement, settling, energy and contact outputs. A separately timed full diagnostic path has no equivalent ML output, so no matching replacement ratio is claimed. [E6]')
sub('Later local profiling supplement')
p('A 12 October local study, later than the verified 11 October published checkpoint, profiled the unchanged full diagnostic nominal calculation. One warmup and three alternating unprofiled and profiled pairs produced seven solves. All non timing summary fields exactly matched the saved baseline, five study checks passed and 13 focused bookkeeping tests passed. The earlier full 433 test suite was not rerun. [E7]')
p('Unprofiled median wall time was 413.608 ms and profiled median 524.979 ms, with median paired overhead ratio 1.328. The integration path accounted cumulatively for 90.82 to 92.32% of each profile total; road height evaluation had the largest self time share at 25.55 to 25.83%. Cumulative parent and child times overlap and cannot be added as independent shares. These full diagnostic instrumented observations are not directly comparable with the earlier peak query benchmark. [E7]')
p('The saved decision retained the correct implementation, precision and diagnostics. A specialised scalar road height path is a possible future optimisation, without a measured improvement claim. The profiler identifies expensive call paths; it does not measure memory bandwidth, arithmetic intensity or FLOPS. Built in cProfile is a documented extension to the course profiling principles. [6, E7]')
sub('Preparation costs and trade offs')
p('Existing preparation timings cover partial and nested work. They do not establish a complete fresh build cost, so a numerical break even query count is unsupported. Numerical checks supported retaining the cheaper label settings. The selected surrogate improved sampled prediction accuracy over linear regression, and its warm query cost was measured separately from preparation. [E3, E6]')

# Page 8
page(); heading('8  Limitations reproducibility and engineering judgement')
sub('What the evidence establishes')
p('Numerical verification checks implementation consistency and resolution. ML evaluation checks simulated peak prediction on a reserved sample. Neither validates a specific physical vehicle. Fixed road input, linear forces and two varying parameters keep this task narrow; changing masses, tyre behaviour or the bump creates a different prediction problem. [E1–E4]')
p('Terminal mechanical energy bounds remaining relative movement in the ideal flat road model, supporting the finite horizon. It uses approximate states and does not certify integration error. The 1 N contact margin screens numerical labels; positive sampled force neither supplies a safety rating nor validates contact loss dynamics. [E1, E2]')
sub('Sampled trends and future work')
p('All 210 adjacent training grid damping increases lowered A, post bump peak and settling. Stiffness produced different rankings, as Section 6 illustrates. These sampled trends are not universal rules or continuous optima. Small A downturns of at most 0.02535 mm lack individual refinement and lie below the adopted 0.05 mm agreement criterion; their detailed significance remains unresolved. [E5]')
p('Future work could refine selected sensitivity locations, measure physical vehicle responses, introduce relevant nonlinearities, and test portability in a clean environment. A future scalar road height optimisation would need an equivalent workload and preserved output checks. If any model or setting is chosen using the consumed test results, genuinely new independent cases are needed for a new generalisation claim. No further experiment is implied by this draft.')
sub('Reproducibility and project organisation')
p('The repository separates code and results in Suspension_Model from decisions and AI records in Project_Setup. It includes a README, docstrings, HTML documentation, tests and an MIT licence for original software and authored documentation. Other materials retain their own terms. The saved 433 passing tests were not rerun for this report. [E1, E6, E8]')
p('A real GitHub Desktop clone at 8ba9808 passed three saved output audits on 11 October in the existing Windows and Anaconda Python 3.12.7 environment, without new simulation, fitting or test prediction. Strict final and runtime audits require matching excluded course sources through authorised access. Clean installation and a full rebuild remain unverified. Direct package pins do not completely lock transitive dependencies. [E8]')
sub('Conclusion and lessons supported by the results')
p('For the adopted two parameter simulation task, the development selected SVR provides lower sampled peak error than the linear baseline and inexpensive warm queries. The strongest methodological lessons are to define the response before fitting, separate numerical label error from regression error, and preserve data roles through selection and final evaluation. Physical interpretation still needs full response information: peak size, post bump size and settling measure different features of motion.')
flag('R6', 'Explain which result changed your engineering judgement and why. Confirm that you can defend the finite horizon and the separate peak and settling definitions. These evidence based lessons are not claims about what you personally learned.')

# Page 9
page(); heading('9  AI use reflection and student review')
p('The records disclose substantial assistance from Codex and AI review assistants in specification, source review, implementation, testing, interpretation and documentation. Exact historical model versions are not consistently verified. AI produced this report draft from saved evidence on 22 October 2026. Its contribution to drafting is substantial; a precise whole project contribution percentage is unestablished. [E9]')
p('Recorded purposes included connecting taught methods to the model, explaining unfamiliar ideas, creating inspectable stages and checking consistency. The student must confirm their own reasons for using AI, rather than adopt motives inferred by the assistant. [E9]')
sub('Checks errors and decisions')
p('Checks included numerical refinement, an analytical diagnostic, physical screens, software tests, frozen data roles and saved output audits. Another AI source review alone is not independent physical validation. This draft was checked against saved records and rendered pages; it generated no new scientific results.')
p('Recorded corrections include confusing an online SciPy documentation version with the installed version, 1.13.1, and incompletely restricting library threads in the first runtime preflight. That attempt stopped before timing; corrected v2 retained the workload. Earlier repository and submission guidance was also reconciled with dated evidence. These corrections illustrate why fluent AI output still requires checking. [E1, E6, E9]')
p('Student decisions included retaining the full response target, emphasising post bump motion, authorising stages and selecting MIT. The student performed the GitHub upload and clone steps. These actions and the limited walkthrough examples do not establish independent authorship of all code or full understanding of every method. [E9]')
flag('R7', 'Write your own reflection on why you used AI, the approximate contribution in each major task, what you checked yourself, advice you corrected or rejected, and how AI affected your understanding and workflow. State honestly what you can now explain and what remains difficult. Do not claim that the assistant’s checks were all your own work.')
sub('Items requiring confirmation before submission')
table(['Review item', 'Required student action'],[
    ['R1 and R2', 'Add identity and personal motivation; confirm intended use and avoid an unsupported acceptance threshold.'],
    ['R3 to R6', 'Supply your own explanations of force signs, verification, data roles and engineering lessons.'],
    ['R7', 'Replace the prompt with an honest personal AI reflection and contribution account.'],
    ['Approval and access', 'Preserve any teaching team topic approval record; verify the assessor can access the private repository.'],
    ['Final evidence and submission', 'Review and upload the intended final revision, including the local profiling supplement if used; create the required fresh clone ZIP and check current Moodle instructions.'],
], [1.65,5.25])
p('Working deadline supplied by the student: 23 October 2026 at 23:59 Australia/Sydney. The brief refers to the Unit Overview Spreadsheet for dates; the current spreadsheet and Moodle submission form were not available for independent confirmation. References and appendices are excluded from the brief’s ten page report limit. This draft has nine main report pages and a separate reference page. [E8, 7]')

# Page 10
page(); heading('References and repository evidence')
p('External sources support the formulation and methods. Repository records support the actual settings, calculations and chronology. No external source supplies the project’s generated dataset or validates its results experimentally. Reference links were checked on 22 October 2026; original project access dates remain in EVIDENCE.md.')

refs = [
    ('[1] Slaets P. A quarter car suspension. KU Leuven Computer Aided Simulation, section 1.6.2, equation 1.11. Formulation source recorded as S002.', 'https://fet-edu-em.pages.gitlab.kuleuven.be/computer-aided-simulation/course-material/t42cms-cas-book/t42cms-cas-lectures/Examples/Quarter_car_suspension/Quarter_car_suspension_model.html', 'Quarter car model'),
    ('[2] Soong M F, Ramli R and Saifizul A. 2017. Between simplicity and accuracy: Effect of adding modeling details on quarter vehicle model accuracy. PLOS ONE 12(6), e0179485. Table 2 supplies the nominal parameters.', 'https://doi.org/10.1371/journal.pone.0179485', 'Article and parameter table'),
    ('[3] MathWorks. Robust Control of Active Suspension. Time Domain Evaluation. The bump shape is adapted; this project changes its crossing duration.', 'https://www.mathworks.com/help/robust/gs/active-suspension-control-design.html', 'Suspension example'),
    ('[4] SciPy developers. SciPy 1.13.1 solve_ivp documentation. RK45, tolerance controls and dense output.', 'https://docs.scipy.org/doc/scipy-1.13.1/reference/generated/scipy.integrate.solve_ivp.html', 'RK45 documentation'),
    ('[5] scikit learn developers. SVR documentation, 1.5 series, displayed 1.5.2. The project used scikit learn 1.5.1; the documentation patch version differs.', 'https://scikit-learn.org/1.5/modules/generated/sklearn.svm.SVR.html', 'SVR documentation'),
    ('[6] Python Software Foundation. The Python Profilers. Python 3.12 documentation. Source for the later local cProfile extension.', 'https://docs.python.org/3.12/library/profile.html', 'Profiler documentation'),
]
for text,url,label in refs:
    para=p(text); link(para, ' '+label, url)
    para.paragraph_format.space_after=Pt(5)
    for run in para.runs: run.font.size=Pt(9.5)
p('[7] MMA3001 teaching team. MMA3001 2026 Project Brief, 15 pages. Requirements pp 4 to 8 and rubric pp 10 to 15. Local course source, excluded from redistribution. SHA256 begins 1029cf7c7c284416; full hash is in EVIDENCE.md. Relevant course notebooks cover Runge Kutta, regression, evaluation and profiling.').runs[0].font.size=Pt(9.5)
sub('Evidence index')
p('E1 to E7 paths are relative to Suspension_Model. After a comma, a bare filename inherits the preceding folder. Scientific outputs E1 to E6 are in checkpoint 8ba9808f10dcdc84330135870d8b7f92c189f0a8. E7 is local. E8 and E9 include later records whose dates distinguish publication from local work.').runs[0].font.size=Pt(9.5)
evidence = [
    ('E1', 'quarter_car.py; results/CHECK_RESULTS.md; results/summary.json. Model, settings and nominal response.'),
    ('E2', 'verification_results/CHECK_RESULTS.md, summary.json. Nine pilot comparisons, analytical and physical checks.'),
    ('E3', 'DATASET.md; dataset_v1/summary.json; ML_GUIDE.md; ml_development_v1/CHECK_RESULTS.md; ml_reference_v1/summary.json.'),
    ('E4', 'final_evaluation_v1/summary.json, frozen_plan.json, refit.json, test_access.json, CHECK_RESULTS.md. Figure 1 replots test_predictions.csv from that folder.'),
    ('E5', 'PHYSICS_REVIEW.md; interpretation_v1/review.json, CHECK_RESULTS.md. Figure 2 uses results/nominal_trace_1ms.csv.'),
    ('E6', 'runtime_benchmark_v2/summary.json, plan.json, CHECK_RESULTS.md; RUNTIME_GUIDE.md; runtime_benchmark_v1/FAILURE_NOTE.md.'),
    ('E7', 'PROFILING_GUIDE.md; profiling_v1/CHECK_RESULTS.md, TEST_RESULTS.md. Local 12 October supplement, not verified as uploaded.'),
    ('E8', 'Suspension_Model/REPRODUCING.md; Project_Setup/clone_review_v1/CHECK_RESULTS.md; Project_Setup/SUBMISSION_CHECKLIST.md. Reproduction and outstanding requirements.'),
    ('E9', 'Project_Setup/AI_USE_LOG.md, EVIDENCE.md, PROJECT_STATE.md, revision 033 at source review, plus the report drafting entry dated 22 October.'),
]
for code,text in evidence:
    para=p(f'[{code}] {text}'); para.paragraph_format.space_after=Pt(4)
    for run in para.runs: run.font.size=Pt(9.5)
para=p(); link(para,'Private project repository','https://github.com/weehaosiah/MMA3001-suspension-modelling')
para.paragraph_format.space_after=Pt(0)

doc.core_properties.title = 'Predicting peak suspension travel with numerical simulation and regression'
doc.core_properties.subject = 'MMA3001 report draft based on saved project evidence'
doc.core_properties.author = 'Student identity pending review'
doc.core_properties.keywords = 'MMA3001, suspension, RK45, RK4, SVR, report draft'
doc.save(DOCX)

# Plain text for claim review only. DOCX is the editable deliverable.
parts=[]
for para in doc.paragraphs:
    if para.text: parts.append(para.text)
for t in doc.tables:
    parts.append('\n'.join(' | '.join(c.text for c in row.cells) for row in t.rows))
(OUT/'report_text_for_review.txt').write_text('\n\n'.join(parts),encoding='utf-8')
print(DOCX)
