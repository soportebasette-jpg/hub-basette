import streamlit as st
import os
import pandas as pd
import plotly.express as px
import random
import base64
from datetime import datetime
from fpdf import FPDF

# 1. CONFIGURACIÓN
st.set_page_config(
    page_title="Basette Group | Hub", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Función para convertir imagen a base64 y que se vea en el HTML
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# Preparamos la imagen de Rosco
img_base64 = get_base64_of_bin_file("rosco.jpg")

# 2. CSS DE ALTA VISIBILIDAD (GENERAL)
st.markdown("""
    <style>
    /* ══ SIDEBAR SIEMPRE VISIBLE — botón colapsar/expandir ══ */
    /* Mostrar siempre el botón de toggle del sidebar */
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        background: linear-gradient(160deg, #c60b1e, #e07010, #f1bf00) !important;
        border-radius: 0 8px 8px 0 !important;
        width: 28px !important;
        color: white !important;
        box-shadow: 2px 0 6px rgba(0,0,0,0.2) !important;
    }
    [data-testid="collapsedControl"] svg {
        fill: white !important;
        color: white !important;
    }
    /* Botón de colapsar dentro del sidebar también visible */
    button[kind="header"] {
        background: rgba(255,255,255,0.3) !important;
        border-radius: 6px !important;
    }
    button[kind="header"] svg { fill: #000000 !important; }

    /* ══ FONDO PRINCIPAL BLANCO ══ */
    .stApp { background-color: #dce8f5 !important; color: #111111 !important; }
    .main .block-container { background-color: #dce8f5 !important; }

    /* ══ SIDEBAR — DEGRADADO NARANJA FUSIÓN ROJO+AMARILLO ══ */
    [data-testid="stSidebar"] {
        background: linear-gradient(160deg,
            #c60b1e 0%,
            #d4420a 25%,
            #e07010 50%,
            #e89b0a 75%,
            #f1bf00 100%
        ) !important;
        position: relative;
    }
    [data-testid="stSidebarContent"] { background: transparent !important; }

    /* Todos los textos del sidebar en negro */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #000000 !important;
        font-weight: 900 !important;
    }
    [data-testid="stSidebar"] hr { border-color: rgba(0,0,0,0.25) !important; }

    /* ══ CUADROS DE MENÚ ══ */
    .menu-box-comercial {
        background: rgba(255,255,255,0.30);
        border: 2px solid rgba(255,255,255,0.6);
        border-radius: 10px;
        padding: 2px 4px;
        margin-bottom: 6px;
        backdrop-filter: blur(4px);
    }
    .menu-box-directivos {
        background: rgba(255,255,255,0.30);
        border: 2px solid rgba(255,255,255,0.6);
        border-radius: 10px;
        padding: 2px 4px;
        margin-bottom: 6px;
        backdrop-filter: blur(4px);
    }
    .menu-box-title {
        font-size: 0.8rem;
        font-weight: 900;
        color: #ffffff !important;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    /* Botones del sidebar sobre gradiente naranja */
    [data-testid="stSidebar"] button {
        background: rgba(255,255,255,0.25) !important;
        border: 2px solid rgba(255,255,255,0.5) !important;
        color: #000000 !important;
        font-weight: 900 !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] button:hover {
        background: rgba(255,255,255,0.5) !important;
    }

    /* ══ CONTENIDO PRINCIPAL — FONDO BLANCO, TEXTO NEGRO ══ */
    .main p, .main span, .main div, .main li, .main td, .main th,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] li,
    .stText, .element-container p {
        color: #111111 !important;
    }
    h1, h2 { color: #c60b1e !important; font-weight: 900 !important; }
    h3, h4 { color: #8B0000 !important; font-weight: 800 !important; }
    h5, h6 { color: #333333 !important; }

    /* ══ BOTONES ══ */
    button p, .stDownloadButton button p, .stButton button p {
        color: #000000 !important;
        font-weight: 900 !important;
    }
    button, .stDownloadButton button, .stButton button {
        background-color: #ffffff !important;
        border: 2px solid #c60b1e !important;
    }
    button:hover, .stButton button:hover {
        background-color: #f1bf00 !important;
        border-color: #c60b1e !important;
    }
    [data-testid="stLinkButton"] a {
        background-color: #ffffff !important;
        border: 2px solid #c60b1e !important;
        color: #000000 !important;
        font-weight: 900 !important;
    }
    [data-testid="stLinkButton"] a p { color: #000000 !important; }

    /* ══ INPUTS Y SELECTBOX ══ */
    .stSelectbox div[data-baseweb="select"],
    .stMultiSelect div[data-baseweb="select"] {
        background-color: #eef4fb !important;
        color: #111111 !important;
        border: 1px solid #c60b1e !important;
    }
    .stTextInput input, .stTextArea textarea {
        background-color: #eef4fb !important;
        color: #111111 !important;
        border: 1px solid #c60b1e !important;
    }

    /* ══ DATAFRAME / TABLAS ══ */
    .stTable { background-color: white !important; border-radius: 10px; }
    .stTable td, .stTable th { color: #000000 !important; text-align: center !important; }
    [data-testid="stDataFrame"] { background: white !important; color: #111 !important; }

    /* ══ EXPANDERS ══ */
    [data-testid="stExpander"] {
        background-color: #eef4fb !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
    }
    [data-testid="stExpander"] summary p { color: #111111 !important; font-weight: 700 !important; }

    /* ══ TAGS / MULTISELECT ══ */
    span[data-baseweb="tag"] { background-color: #c60b1e !important; border-radius: 5px !important; }
    span[data-baseweb="tag"] span { color: white !important; font-weight: bold !important; }

    /* ══ LABELS ══ */
    header { visibility: hidden; }
    label[data-testid="stWidgetLabel"] p {
        color: #c60b1e !important;
        font-weight: 900 !important;
        font-size: 1.05rem !important;
    }

    /* ══ BLOCK-HEADER (titulos de secciones) ══ */
    .block-header {
        background: linear-gradient(90deg, #c60b1e 0%, #9b0016 100%);
        color: #ffffff !important;
        padding: 10px 24px;
        border-radius: 6px;
        border-left: 6px solid #f1bf00;
        font-weight: bold;
        margin-bottom: 20px;
        margin-top: 25px;
        display: inline-block;
        font-size: 1.05rem;
        letter-spacing: 0.03em;
        box-shadow: 2px 2px 6px rgba(198,11,30,0.18);
    }

    /* ══ CARDS DE PRECIOS ══ */
    .price-card {
        background-color: #eef4fb;
        border: 2px solid #c60b1e;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin-bottom: 15px;
        transition: transform 0.3s;
        height: 100%;
    }
    .price-card:hover { border-color: #f1bf00; transform: translateY(-5px); }
    .price-title { color: #c60b1e !important; font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; }
    .price-val { color: #111111 !important; font-size: 2rem; font-weight: 900; }
    .price-sub { color: #555555 !important; font-size: 0.85rem; margin-bottom: 5px; }

    /* ══ WINNER CARD ══ */
    .winner-card {
        background: linear-gradient(90deg, #c60b1e, #8B0000);
        padding: 25px; border-radius: 15px; color: white !important;
        text-align: center; font-weight: bold; font-size: 28px;
        margin-bottom: 25px; box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
    }

    /* ══ SOCIAL ICONS ══ */
    .social-container {
        display: flex; justify-content: flex-end;
        align-items: center; gap: 20px; padding: 10px;
    }
    .social-icon { transition: transform 0.3s; }
    .social-icon:hover { transform: scale(1.1); }

    /* ══ TABS ══ */
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #c60b1e !important; font-weight: 900 !important;
    }
    button[data-baseweb="tab"] p {
        color: #555555 !important; font-weight: 600 !important;
    }

    /* ══ INFO / WARNING / ERROR BOXES ══ */
    [data-testid="stAlert"] { color: #111111 !important; }
    </style>
    """, unsafe_allow_html=True)


# ── UTILIDADES GLOBALES DE EXCEL (accesibles desde cualquier tab) ──
import zipfile as _zipfile_mod, io as _io_mod, re as _re_mod

def leer_excel_safe(f, header=0, sheet_name=0):
    """Lee xlsx sin openpyxl usando solo stdlib."""
    raw = f.read() if hasattr(f, 'read') else f
    buf = _io_mod.BytesIO(raw)
    zf = _zipfile_mod.ZipFile(buf)
    shared_strings = []
    if 'xl/sharedStrings.xml' in zf.namelist():
        from xml.etree import ElementTree as _ET
        tree = _ET.parse(zf.open('xl/sharedStrings.xml'))
        ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        for si in tree.findall('.//s:si', ns):
            shared_strings.append(''.join(p.text or '' for p in si.findall('.//s:t', ns)))
    from xml.etree import ElementTree as _ET
    wb_tree = _ET.parse(zf.open('xl/workbook.xml'))
    wb_ns = {'w': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    sheets = wb_tree.findall('.//w:sheet', wb_ns)
    sheet_el = sheets[sheet_name] if isinstance(sheet_name, int) else next(
        (s for s in sheets if s.get('name') == sheet_name), sheets[0])
    rels_tree = _ET.parse(zf.open('xl/_rels/workbook.xml.rels'))
    rels_ns = {'r': 'http://schemas.openxmlformats.org/package/2006/relationships'}
    ns_rid = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    r_id = sheet_el.get(f'{{{ns_rid}}}id') or sheet_el.get('r:id')
    sheet_file = 'xl/worksheets/sheet1.xml'
    for rel in rels_tree.findall('r:Relationship', rels_ns):
        if rel.get('Id') == r_id:
            t = rel.get('Target', '').lstrip('/')
            sheet_file = t if t.startswith('xl/') else 'xl/' + t
            break
    ws_tree = _ET.parse(zf.open(sheet_file))
    ws_ns = {'w': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    def col2idx(s):
        v = 0
        for ch in s: v = v * 26 + (ord(ch) - 64)
        return v - 1
    rows_data, max_col = {}, 0
    for row_el in ws_tree.findall('.//w:row', ws_ns):
        r_num = int(row_el.get('r', 0))
        for c_el in row_el.findall('w:c', ws_ns):
            ref = c_el.get('r', '')
            m = _re_mod.match(r'([A-Z]+)', ref)
            if not m: continue
            col_idx = col2idx(m.group(1))
            max_col = max(max_col, col_idx)
            t_attr = c_el.get('t', '')
            v_el = c_el.find('w:v', ws_ns)
            val = None
            is_el = c_el.find('w:is', ws_ns)
            if is_el is not None:
                val = ''.join(p.text or '' for p in is_el.findall('.//w:t', ws_ns))
            elif v_el is not None and v_el.text is not None:
                if t_attr == 's':
                    i_s = int(v_el.text)
                    val = shared_strings[i_s] if i_s < len(shared_strings) else ''
                elif t_attr in ('str', 'b', 'e'):
                    val = v_el.text
                else:
                    try:
                        fv = float(v_el.text)
                        val = int(fv) if fv == int(fv) else fv
                    except (ValueError, OverflowError):
                        val = v_el.text
            rows_data.setdefault(r_num, {})[col_idx] = val
    if not rows_data:
        return pd.DataFrame()
    n_cols = max_col + 1
    records = [[rows_data[r].get(c) for c in range(n_cols)] for r in sorted(rows_data.keys())]
    df = pd.DataFrame(records)
    if header is None:
        return df
    if isinstance(header, int) and header < len(df):
        col_names = [str(v) if v is not None else f'col_{i}' for i, v in enumerate(df.iloc[header].tolist())]
        df.columns = col_names
        df = df.iloc[header + 1:].reset_index(drop=True)
    return df


def hacer_xlsx_nativo(sheets_dict):
    """Genera xlsx real usando solo stdlib. sheets_dict = {nombre: dataframe}"""
    import zipfile as zf2, io as io2
    from xml.etree import ElementTree as ET2

    def _prep(df_in):
        df_out = df_in.copy()
        for col in df_out.columns:
            try:
                df_out[col] = df_out[col].apply(lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else x)
            except Exception:
                pass
        return df_out

    def esc(s):
        return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;').replace("'",'&apos;')

    shared, shared_map = [], {}
    def get_si(val):
        s = str(val)
        if s not in shared_map:
            shared_map[s] = len(shared)
            shared.append(s)
        return shared_map[s]

    sheet_data = {}
    for sname, df in sheets_dict.items():
        df2p = _prep(df).reset_index(drop=True)
        rows = [list(df2p.columns)]
        for _, row in df2p.iterrows():
            rows.append(list(row))
        for row in rows:
            for cell in row:
                if cell is not None and str(cell) not in ['', 'nan', 'None']:
                    try: float(str(cell).replace(',','.'))
                    except (ValueError, TypeError): get_si(cell)
        sheet_data[sname] = rows

    buf = io2.BytesIO()
    col_letters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R',
                   'S','T','U','V','W','X','Y','Z','AA','AB','AC','AD','AE','AF','AG','AH',
                   'AI','AJ','AK','AL','AM','AN','AO','AP','AQ','AR','AS','AT','AU','AV','AW','AX']
    with zf2.ZipFile(buf, 'w', zf2.ZIP_DEFLATED) as z:
        ct = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n  <Default Extension="xml" ContentType="application/xml"/>\n  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>\n  <Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>\n  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>\n'
        for i in range(len(sheet_data)): ct += f'  <Override PartName="/xl/worksheets/sheet{i+1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>\n'
        ct += '</Types>'
        z.writestr('[Content_Types].xml', ct)
        z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>\n</Relationships>')
        wb_rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n  <Relationship Id="rId_ss" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/>\n  <Relationship Id="rId_st" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>\n'
        for i, sname in enumerate(sheet_data): wb_rels += f'  <Relationship Id="rId{i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i+1}.xml"/>\n'
        wb_rels += '</Relationships>'
        z.writestr('xl/_rels/workbook.xml.rels', wb_rels)
        wb_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">\n  <sheets>\n'
        for i, sname in enumerate(sheet_data): wb_xml += f'    <sheet name="{esc(sname)}" sheetId="{i+1}" r:id="rId{i+1}"/>\n'
        wb_xml += '  </sheets>\n</workbook>'
        z.writestr('xl/workbook.xml', wb_xml)
        z.writestr('xl/styles.xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts><font><sz val="11"/><name val="Calibri"/></font></fonts><fills><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills><borders><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs></styleSheet>')
        ss_xml = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="{len(shared)}" uniqueCount="{len(shared)}">\n'
        for s in shared: ss_xml += f'  <si><t xml:space="preserve">{esc(s)}</t></si>\n'
        ss_xml += '</sst>'
        z.writestr('xl/sharedStrings.xml', ss_xml)
        for si_idx, (sname, rows) in enumerate(sheet_data.items()):
            ws_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">\n  <sheetData>\n'
            for r_idx, row in enumerate(rows):
                ws_xml += f'    <row r="{r_idx+1}">\n'
                for c_idx, cell in enumerate(row):
                    col = col_letters[c_idx] if c_idx < len(col_letters) else f'A{c_idx}'
                    ref = f'{col}{r_idx+1}'
                    if cell is None or str(cell) in ['', 'nan', 'None']: ws_xml += f'      <c r="{ref}"/>\n'
                    else:
                        try:
                            num = float(str(cell).replace(',','.'))
                            ws_xml += f'      <c r="{ref}" t="n"><v>{num}</v></c>\n'
                        except (ValueError, TypeError):
                            si_n = shared_map.get(str(cell), 0)
                            ws_xml += f'      <c r="{ref}" t="s"><v>{si_n}</v></c>\n'
                ws_xml += '    </row>\n'
            ws_xml += '  </sheetData>\n</worksheet>'
            z.writestr(f'xl/worksheets/sheet{si_idx+1}.xml', ws_xml)
    buf.seek(0)
    return buf.read()

# --- FUNCIONES DE DATOS DASHBOARD ---
def get_csv_url(url):
    return url.replace('/edit?usp=sharing', '/export?format=csv').split('&ouid=')[0].split('?')[0] + '/export?format=csv'

URL_ENE = get_csv_url("https://docs.google.com/spreadsheets/d/1W-Eq63SnBBlOykJlP9XgASXDPpWQhQnVW-oFHUlSMcQ/edit?usp=sharing")
URL_TEL = get_csv_url("https://docs.google.com/spreadsheets/d/1HkI37_hUTZbsm_DwLjbi2kMTKcC23QsV/edit?usp=sharing")
URL_ALA = get_csv_url("https://docs.google.com/spreadsheets/d/17o4HSJ4DZBwMgp9AAiGhkd8NQCZEaaQ_/edit?usp=sharing")

@st.cache_data(ttl=60)
def load_and_clean_ranking():
    # ENERGÍA
    df_e = pd.read_csv(URL_ENE)
    df_e.columns = df_e.columns.str.strip()
    df_e['Fecha Creación'] = pd.to_datetime(df_e['Fecha Creación'], dayfirst=True, errors='coerce')
    df_e = df_e.dropna(subset=['Comercial', 'Fecha Creación'])
    df_e['Año'] = df_e['Fecha Creación'].dt.year.astype(str)
    df_e['Mes'] = df_e['Fecha Creación'].dt.strftime('%m - %B')
    df_e['V_Luz'] = df_e['CUPS Luz'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0)
    df_e['V_Gas'] = df_e['CUPS Gas'].apply(lambda x: 1 if pd.notnull(x) and str(x).strip() != "" else 0)
    df_e['Total_Ene'] = df_e['V_Luz'] + df_e['V_Gas']
    df_e['REF_Ene'] = df_e['Canal'].apply(lambda x: 1 if pd.notnull(x) and "REF" in str(x).upper() else 0) if 'Canal' in df_e.columns else 0
    
    # TELCO
    df_t = pd.read_csv(URL_TEL)
    df_t.columns = df_t.columns.str.strip()
    df_t['Fecha Creación'] = pd.to_datetime(df_t['Fecha Creación'], dayfirst=True, errors='coerce')
    df_t = df_t.dropna(subset=['Comercial', 'Fecha Creación'])
    df_t['Año'] = df_t['Fecha Creación'].dt.year.astype(str)
    df_t['Mes'] = df_t['Fecha Creación'].dt.strftime('%m - %B')
    df_t['REF_Tel'] = df_t['Canal'].apply(lambda x: 1 if pd.notnull(x) and "REF" in str(x).upper() else 0) if 'Canal' in df_t.columns else 0
    
    def get_telco_metrics(row):
        f, m = 0, 0
        t = str(row.get('Tipo Tarifa', '')).lower()
        if 'fibramovil' in t or ('fibra' in t and 'movil' in t): f, m = 1, 1
        elif 'fibra' in t: f = 1
        elif 'movil' in t: m = 1
        for col in ['Línea 2', 'Línea 3', 'Línea 4', 'Línea 5']:
            if col in row and pd.notnull(row[col]) and str(row[col]).strip() != "": m += 1
        return f, m, (f + m)

    res = df_t.apply(get_telco_metrics, axis=1)
    df_t['V_Fibra'] = res.apply(lambda x: x[0])
    df_t['V_Móvil'] = res.apply(lambda x: x[1])
    df_t['Total_Tel'] = res.apply(lambda x: x[2])

    # ALARMAS
    df_a = pd.read_csv(URL_ALA)
    df_a.columns = df_a.columns.str.strip()
    df_a['Fecha Creación'] = pd.to_datetime(df_a['Fecha Creación'], dayfirst=True, errors='coerce')
    df_a = df_a.dropna(subset=['Comercial', 'Fecha Creación'])
    df_a['Año'] = df_a['Fecha Creación'].dt.year.astype(str)
    df_a['Mes'] = df_a['Fecha Creación'].dt.strftime('%m - %B')
    df_a['V_Alarma'] = 1 
    df_a['REF_Ala'] = df_a['Canal'].apply(lambda x: 1 if pd.notnull(x) and "REF" in str(x).upper() else 0) if 'Canal' in df_a.columns else 0
    
    return df_e, df_t, df_a

# 3. BASE DE DATOS LUZ - PRECIOS ACTUALIZADOS GANA ENERGÍA
tarifas_luz = [
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "24H", "P1": 0.089, "P2": 0.089, "ENERGIA": 0.119, "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 1, "COMPAÑÍA": "GANA ENERGÍA", "TARIFA": "3T", "P1": 0.089, "P2": 0.089, "ENERGIA": "0,171/0,104/0,08", "EXCEDENTE": 0.05, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_gana.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "24H (POR USO)", "P1": 0.123, "P2": 0.037, "ENERGIA": 0.109, "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 2, "COMPAÑÍA": "NATURGY", "TARIFA": "3T (TARIF NOCHE)", "P1": 0.123, "P2": 0.037, "ENERGIA": "0,180/0,107/0,718", "EXCEDENTE": 0.06, "DTO": "0%", "BATERIA": "SI_GRATIS", "logo": "manuales/logo_naturgy.png"},
    {"PRIORIDAD": 3, "COMPAÑÍA": "TOTAL LUZ", "TARIFA": "24H (A TU AIRE)", "P1": 0.081, "P2": 0.081, "ENERGIA": 0.114, "EXCEDENTE": 0.07, "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_total.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "SOLAR", "P1": 0.093, "P2": 0.093, "ENERGIA": 0.138, "EXCEDENTE": 0.06, "DTO": "-7%", "BATERIA": "SI_2€", "logo": "manuales/logo_endesa.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "24H", "P1": 0.093, "P2": 0.093, "ENERGIA": 0.119, "EXCEDENTE": "NO TIENE", "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_endesa.png"},
    {"PRIORIDAD": 4, "COMPAÑÍA": "ENDESA", "TARIFA": "TU CASA 50", "P1": 0.093, "P2": 0.093, "ENERGIA": "HPROMO:0,076 RESTO:0,152", "EXCEDENTE": "NO TIENE", "DTO": "0%", "BATERIA": "NO", "logo": "manuales/logo_endesa.png"}
]

# 4. LOGIN
LOGO_PRINCIPAL = "1000233813.jpg"
QR_PLAN_AMIGO = "anunciosbasette/qr-plan amigo.png"

if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if "_pw_persist" not in st.session_state: st.session_state["_pw_persist"] = False
# Restore from persistent flag on rerun
if st.session_state.get("_pw_persist") and not st.session_state.get("password_correct"):
    st.session_state["password_correct"] = True
if not st.session_state["password_correct"]:
    _, col_auth, _ = st.columns([1, 1.2, 1])
    with col_auth:
        if os.path.exists(LOGO_PRINCIPAL): st.image(LOGO_PRINCIPAL)
        pwd = st.text_input("Introduce Clave Comercial:", type="password")
        if st.button("ACCEDER AL HUB"):
            if pwd == st.secrets["CLAVE_COMERCIAL"]:
                st.session_state["password_correct"] = True
                st.session_state["_pw_persist"] = True
                st.rerun()
            else: st.error("Clave incorrecta")
    st.stop()

# 5. NAVEGACIÓN
with st.sidebar:
    if os.path.exists(LOGO_PRINCIPAL): st.image(LOGO_PRINCIPAL)
    st.markdown("---")

    # ── Botón de cierre de sesión ──
    col_s1, col_s2 = st.columns([2,1])
    with col_s1:
        st.markdown('<p style="color:#000000; font-size:0.75rem; margin:0; font-weight:bold;">✅ Sesión activa</p>', unsafe_allow_html=True)
    with col_s2:
        if st.button("🚪 Salir", key="logout_btn", use_container_width=True):
            st.session_state["password_correct"] = False
            st.session_state["_pw_persist"] = False
            st.session_state["dir_auth"] = False
            st.session_state["_dir_auth_ts"] = False
            st.rerun()
    st.markdown("---")

    # ── MENÚ ACORDEÓN VERTICAL ──
    # Inicializar zona activa
    if "zona_activa" not in st.session_state:
        st.session_state["zona_activa"] = "comerciales"

    # ── BLOQUE COMERCIALES ──
    st.markdown('''<div class="menu-box-comercial" style="cursor:pointer; margin-bottom:4px;">''', unsafe_allow_html=True)
    _toggle_com = st.button("👔 COMERCIALES", key="btn_zona_com", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if _toggle_com:
        st.session_state["zona_activa"] = "comerciales"
        st.rerun()

    if st.session_state.get("zona_activa") == "comerciales":
        menu = st.radio(
            "Menú comerciales:",
            ["🚀 CRM", "📊 PRECIOS", "🔍 COMPARADORES", "📢 ANUNCIOS Y PLAN AMIGO",
             "📈 DASHBOARD Y RANKING", "📂 REPOSITORIO", "🕒 CONTROL LABORAL"],
            key="menu_comerciales",
            label_visibility="collapsed"
        )
    else:
        menu = None

    st.markdown("<br>", unsafe_allow_html=True)

    # ── BLOQUE ZONA BACKOFFICE ──
    st.markdown('''<div class="menu-box-directivos" style="cursor:pointer; margin-bottom:4px;">''', unsafe_allow_html=True)
    _toggle_dir = st.button("🔐 ZONA BACKOFFICE", key="btn_zona_dir", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if _toggle_dir:
        st.session_state["zona_activa"] = "directivos"
        st.rerun()

    if st.session_state.get("zona_activa") == "directivos":
        menu = "🔐 ZONA BACKOFFICE"

    if menu is None:
        menu = "🚀 CRM"  # fallback


# --- CRM ---
if menu == "🚀 CRM":
    col_t_izq, col_t_der = st.columns([2, 1])
    with col_t_izq:
        st.header("Portales de Gestión")
    with col_t_der:
        st.markdown(f"""
            <div class="social-container">
                <a href="https://www.facebook.com/profile.php?id=61589358886498" target="_blank">
                    <img src="https://cdn-icons-png.flaticon.com/512/733/733547.png" width="35" class="social-icon">
                </a>
                <a href="https://www.youtube.com/@tecomparotodo" target="_blank">
                    <img src="https://cdn-icons-png.flaticon.com/512/1384/1384060.png" width="35" class="social-icon">
                </a>
                <a href="https://x.com/tecomparotodo" target="_blank">
                    <img src="https://cdn-icons-png.flaticon.com/512/5968/5968958.png" width="35" class="social-icon">
                </a>
                <a href="https://www.instagram.com/tecomparotodo/" target="_blank">
                    <img src="https://cdn-icons-png.flaticon.com/512/174/174855.png" width="35" class="social-icon">
                </a>
                <a href="https://www.tiktok.com/@tecomparotodo?_r=1&_t=ZN-95nfhnoUU9W" target="_blank">
                    <img src="https://cdn-icons-png.flaticon.com/512/3046/3046121.png" width="35" class="social-icon">
                </a>
                <a href="http://www.tecomparotodo.es" target="_blank">
                    <img src="data:image/jpeg;base64,{img_base64}" width="100" style="border-radius:8px; border: 2px solid #d2ff00;" class="social-icon">
                </a>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="block-header">🕒 CONTROL LABORAL</div>', unsafe_allow_html=True)
    st.markdown(f'''<div style="background:#ffffff; padding:15px; border-radius:10px; border:2px solid #d2ff00; text-align:center; margin-bottom:10px;"><h4 style="color:#111111; margin:0;">REGISTRO DE JORNADA</h4></div>''', unsafe_allow_html=True)
    st.link_button(f"ENTRAR AL FORMULARIO", "https://forms.gle/icG7jFPoyGmFD6vC8", use_container_width=True)
    
    st.markdown('<div class="block-header">⭐ MARCADOR</div>', unsafe_allow_html=True)
    st.markdown(f'''<div style="background:#ffffff; padding:15px; border-radius:10px; border:2px solid #d2ff00; text-align:center; margin-bottom:10px;"><h4 style="color:#111111; margin:0;">MARCADOR PRINCIPAL</h4></div>''', unsafe_allow_html=True)
    st.link_button(f"ENTRAR AL MARCADOR", "https://grupobasette.vozipcenter.com/", use_container_width=True)
    
    st.markdown('<div class="block-header">💡 🔥 ENERGÍA</div>', unsafe_allow_html=True)
    energia = [
        {"n": "CRM BASETTE", "u": "https://crm.grupobasette.eu/login"}, 
        {"n": "GANA ENERGÍA", "u": "https://colaboradores.ganaenergia.com/"}, 
        {"n": "NATURGY", "u": "https://checkout.naturgy.es/backoffice"}, 
        {"n": "TOTAL ENERGY", "u": "https://totalenergiesespana.my.site.com/portalcolaboradores/s/login/?ec=302&startURL=%2Fportalcolaboradores%2Fs%2F"}, 
        {"n": "IBERDROLA", "u": "https://crm.gesventas.eu/login.php"}, 
        {"n": "NIBA", "u": "https://clientes.niba.es/"}, 
        {"n": "ENDESA", "u": "https://inergia.app"},
        {"n": "REPSOL", "u": "https://inergia.app/login.php"}
    ]
    cols_en = st.columns(3)
    for i, p in enumerate(energia):
        with cols_en[i % 3]:
            st.markdown(f'''<div style="background:#ffffff; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; margin-bottom:10px;"><h4 style="color:#111111; margin:0;">{p["n"]}</h4></div>''', unsafe_allow_html=True)
            st.link_button(f"ENTRAR", p["u"], use_container_width=True)
    
    st.markdown("---")
    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown('<div class="block-header">🛡️ 🚨 ALARMAS</div>', unsafe_allow_html=True)
        c_al1, c_al2 = st.columns(2)
        with c_al1:
            st.markdown('<div style="background:#ffffff; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; margin-bottom:10px;"><h4 style="color:#111111; margin:0;">SEGURMA</h4></div>', unsafe_allow_html=True)
            st.link_button("ENTRAR", "https://crm.segurma.com/web#action=619&cids=1&menu_id=200&model=sale.order&view_type=list", use_container_width=True)
        with c_al2:
            st.markdown('<div style="background:#ffffff; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; margin-bottom:10px;"><h4 style="color:#111111; margin:0;">3D</h4></div>', unsafe_allow_html=True)
            st.link_button("ENTRAR", "https://www.3dseguridad.es/reportes/menu.php", use_container_width=True)
            
    with col_der:
        st.markdown('<div class="block-header">📶 📱 TELECOMUNICACIONES</div>', unsafe_allow_html=True)
        c_t1, c_t2 = st.columns(2)
        with c_t1:
            st.markdown('<div style="background:#ffffff; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; margin-bottom:10px;"><h4 style="color:#111111; margin:0;">O2</h4></div>', unsafe_allow_html=True)
            st.link_button("ENTRAR O2", "https://o2online.es/auth/login/?next=%2Fventas%2F&type=retail", use_container_width=True)
        with c_t2:
            st.markdown('<div style="background:#ffffff; padding:15px; border-radius:10px; border:1px solid #30363d; text-align:center; margin-bottom:10px;"><h4 style="color:#111111; margin:0;">LOWI</h4></div>', unsafe_allow_html=True)
            st.link_button("ENTRAR LOWI", "https://vodafone.topgestion.es/login", use_container_width=True)

# --- PRECIOS ---
elif menu == "📊 PRECIOS":
    st.header("Tarifario Oficial")
    
    t1, t2, t3 = st.tabs(["⚡ LUZ Y GAS", "📶 TELECOMUNICACIONES", "🛡️ ALARMAS"])
    
    with t1:
        st.markdown('<div class="block-header">⚡ LUZ Y GAS</div>', unsafe_allow_html=True)
        # Buscar la imagen en varios formatos posibles
        img_luz_gas = None
        for ext in ["luz_gas.jpeg", "luz_gas.jpg", "luz_gas.png"]:
            ruta_candidata = f"tarifas_visuales/{ext}"
            if os.path.exists(ruta_candidata):
                img_luz_gas = ruta_candidata
                break
        if img_luz_gas:
            st.image(img_luz_gas, use_container_width=True)
        else:
            st.warning("Imagen de Luz y Gas no encontrada en tarifas_visuales/ (se busca luz_gas.jpeg / .jpg / .png)")

    with t2:
        st.markdown('<div class="block-header">📶 TELECOMUNICACIONES</div>', unsafe_allow_html=True)
        
        st.subheader("LOWI")
        if os.path.exists("tarifas_visuales/lowi.jpg"):
            st.image("tarifas_visuales/lowi.jpg", use_container_width=True)
        
        st.divider()
        
        st.subheader("O2")
        # --- BÚSQUEDA INTELIGENTE DE IMAGEN ---
        carpeta = "tarifas_visuales"
        archivos_en_carpeta = os.listdir(carpeta) if os.path.exists(carpeta) else []
        
        # Buscamos cualquier archivo que contenga "PRECIOS JUNIO O2" sin importar mayúsculas
        archivo_o2 = next((f for f in archivos_en_carpeta if "PRECIOS JUNIO O2" in f.upper()), None)
        
        if archivo_o2:
            st.image(f"{carpeta}/{archivo_o2}", use_container_width=True)
        else:
            st.error(f"No se encontró ninguna imagen para O2 en '{carpeta}'. Archivos hallados: {archivos_en_carpeta}")

    with t3:
        st.markdown('<div class="block-header">🛡️ ALARMAS</div>', unsafe_allow_html=True)
        
        st.subheader("SEGURMA")
        if os.path.exists("tarifas_visuales/segurma.jpg"):
            st.image("tarifas_visuales/segurma.jpg", use_container_width=True)
        st.markdown('<div style="background-color: #d2ff00; color: black; padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; font-size: 1.5rem;">PRIMEROS 12 MESES POR 19.90€</div>', unsafe_allow_html=True)
        
        st.divider()
        
        st.subheader("3D ALARMAS")
        if os.path.exists("tarifas_visuales/3d.jpg"):
            st.image("tarifas_visuales/3d.jpg", use_container_width=True)
        st.markdown('<div style="background-color: #d2ff00; color: black; padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; font-size: 1.5rem;">PRIMEROS 12 MESES POR 24.20€</div>', unsafe_allow_html=True)

# --- COMPARADORES ---
elif menu == "🔍 COMPARADORES":
    st.markdown('<div class="block-header">🔍 COMPARADORES</div>', unsafe_allow_html=True)
    st.markdown("""
        <div style="background:#ffffff; border:2px solid #d2ff00; border-radius:15px; padding:30px; text-align:center; margin-bottom:30px;">
            <h2 style="color:#d2ff00; margin-bottom:10px;">🔗 Herramientas de Comparación</h2>
            <p style="color:#8b949e; font-size:1rem; margin-bottom:20px;">Accede a las herramientas de comparación de tarifas para encontrar la mejor oferta para tu cliente.</p>
        </div>
    """, unsafe_allow_html=True)
    st.link_button("🧾 COMPARADOR FACTURAS LUZ Y GAS", "https://facturasenergia.tecomparotodo.es/", use_container_width=True)
    st.link_button("📶 COMPARADOR TARIFAS TELECO", "https://tarifastelco.tecomparotodo.es/", use_container_width=True)
    st.link_button("🔒 COMPARADOR TARIFAS ALARMAS", "https://tarifasalarmas.tecomparotodo.es/", use_container_width=True)
    st.link_button("⚡ COMPARADOR TARIFAS ENERGÍA", "https://tarifasenergia.tecomparotodo.es/", use_container_width=True)
# --- ANUNCIOS Y PLAN AMIGO ---
elif menu == "📢 ANUNCIOS Y PLAN AMIGO":
    st.header("📢 Anuncios y Plan Amigo")
    st.markdown('<div class="block-header">🖼️ MATERIAL PUBLICITARIO</div>', unsafe_allow_html=True)
    
    path_anuncios = "anunciosbasette/"
    
    # Búsqueda automática de archivos en la carpeta
    if os.path.exists(path_anuncios):
        # Listamos todos los archivos que sean imágenes (png, jpg, jpeg)
        archivos = [f for f in os.listdir(path_anuncios) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not archivos:
            st.info("La carpeta 'anunciosbasette' está vacía o no contiene imágenes.")
        else:
            # Mostramos en rejilla de 3 columnas
            cols = st.columns(3)
            for idx, file_name in enumerate(archivos):
                with cols[idx % 3]:
                    full_path = os.path.join(path_anuncios, file_name)
                    
                    # Mostrar imagen
                    st.image(full_path, use_container_width=True)
                    
                    # Botón de descarga
                    with open(full_path, "rb") as f_anuncio:
                        mime = "image/png" if file_name.lower().endswith('.png') else "image/jpeg"
                        st.download_button(
                            label=f"📥 {file_name[:18]}...", # Nombre truncado para evitar romper el diseño
                            data=f_anuncio.read(),
                            file_name=file_name,
                            mime=mime,
                            key=f"btn_{idx}"
                        )
    else:
        st.error(f"La carpeta '{path_anuncios}' no existe en el directorio del proyecto. Por favor, verifica la ruta.")

# 9. TOTALES INFERIORES BRUTOS
        st.markdown("---")
        st.markdown('<p style="color:#d2ff00; font-weight:bold; text-align:center;">📊 TOTALES BRUTOS (VENTAS SIN DESCUENTOS)</p>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        box = "background:#f0f0f0; border:2px solid #d2ff00; padding:15px; border-radius:10px; text-align:center;"
        
        # Usamos filter(like=...) para que no dé error si la columna no existe
        c1.markdown(f'<div style="{box}"><p style="color:#d2ff00;font-size:0.8rem;margin:0;">ENERGÍA BRUTA</p><h2 style="color:#111111;margin:0;">{int(rank.filter(like="V_Luz").sum().sum() + rank.filter(like="V_Gas").sum().sum())}</h2></div>', unsafe_allow_html=True)
        c2.markdown(f'<div style="{box}"><p style="color:#d2ff00;font-size:0.8rem;margin:0;">FIBRA BRUTA</p><h2 style="color:#111111;margin:0;">{int(rank.filter(like="V_Fibra").sum().sum())}</h2></div>', unsafe_allow_html=True)
        c3.markdown(f'<div style="{box}"><p style="color:#d2ff00;font-size:0.8rem;margin:0;">ALARMA BRUTA</p><h2 style="color:#111111;margin:0;">{int(rank.filter(like="V_Alarma").sum().sum())}</h2></div>', unsafe_allow_html=True)
        c4.markdown(f'<div style="{box} background:#d2ff00;"><p style="color:black;font-weight:bold;margin:0;">TOTAL BRUTO</p><h2 style="color:black;margin:0;">{int(rank["Ventas_Sin_Movil"].sum())}</h2></div>', unsafe_allow_html=True)

        # 10. CUADROS: CANCELACIONES, BAJAS Y PTE FIRMA (Corregidos)
        st.markdown("<br>", unsafe_allow_html=True)
        cx1, cx2, cx3, cx4, cx5 = st.columns(5)
        box_alt = "background:#ffffff; border:1px solid #ff4b4b; padding:15px; border-radius:10px; text-align:center;"
        
        # Filtramos por columnas que contengan 'Cancel' o 'Baja' para no depender de nombres exactos
        cx1.markdown(f'<div style="{box_alt}"><p style="color:#ff4b4b;font-size:0.75rem;margin:0;">CANCEL. ENERGÍA</p><h3 style="color:#111111;margin:0;">{int(rank.filter(like="Cancel_E").sum().sum())}</h3></div>', unsafe_allow_html=True)
        cx2.markdown(f'<div style="{box_alt}"><p style="color:#ff4b4b;font-size:0.75rem;margin:0;">CANCEL. FIBRA</p><h3 style="color:#111111;margin:0;">{int(rank.filter(like="Cancel_F").sum().sum())}</h3></div>', unsafe_allow_html=True)
        cx3.markdown(f'<div style="{box_alt}"><p style="color:#ff4b4b;font-size:0.75rem;margin:0;">BAJAS ENERGÍA</p><h3 style="color:#111111;margin:0;">{int(rank.filter(like="Baja_E").sum().sum())}</h3></div>', unsafe_allow_html=True)
        cx4.markdown(f'<div style="{box_alt}"><p style="color:#ff4b4b;font-size:0.75rem;margin:0;">BAJAS FIBRA</p><h3 style="color:#111111;margin:0;">{int(rank.filter(like="Baja_F").sum().sum())}</h3></div>', unsafe_allow_html=True)
        cx5.markdown(f'<div style="{box_alt} border:1px solid #d2ff00;"><p style="color:#d2ff00;font-size:0.75rem;margin:0;">PTE. FIRMA</p><h3 style="color:#111111;margin:0;">{int(rank["Pte_Firma_Total"].sum())}</h3></div>', unsafe_allow_html=True)
# --- DASHBOARD Y RANKING ---
elif menu == "📈 DASHBOARD Y RANKING":
    try:
        # 1. FUNCIÓN PARA IMÁGENES
        def get_img_64(file_path):
            import base64
            import os
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            return None

        # 2. GLOBOS MOTIVACIONALES — cambian cada día
        _frases_mot = [
            "🎯 El éxito es la suma de pequeños esfuerzos repetidos cada día.",
            "🚀 No cuentes los días, haz que los días cuenten.",
            "💪 Cada cliente es una oportunidad de demostrar quién eres.",
            "⭐ La disciplina es el puente entre las metas y los logros.",
            "🔥 Un NO es solo el comienzo de la negociación.",
            "🏆 Los campeones no nacen, se forjan con constancia.",
            "💡 La energía y la persistencia lo conquistan todo.",
            "🌟 El único límite es el que tú mismo te pones.",
            "🎪 Vende como si fuera el último día, planifica como si fuera el primero.",
            "⚡ El momento de actuar es ahora. Siempre ahora.",
            "🦁 El trabajo duro supera al talento cuando el talento no trabaja duro.",
            "🎸 Convierte cada objeción en una razón para comprar.",
            "🏅 Los resultados hablan por ti, trabaja para que hablen fuerte.",
        ]
        from datetime import date as _dfr
        _frase_dia = _frases_mot[_dfr.today().timetuple().tm_yday % len(_frases_mot)]
        _globos_items = ""
        for _gi in range(20):
            _gl = random.randint(2, 97)
            _gd = random.uniform(0, 5)
            _gdu = random.uniform(4, 9)
            _gs = random.randint(24, 48)
            _globos_items += f'<div class="globo-up" style="left:{_gl}%;animation-delay:{_gd}s;animation-duration:{_gdu}s;font-size:{_gs}px;">🎈</div>'
        st.markdown(f"""
            <div style="position:fixed;top:0;left:0;width:100%;height:100%;z-index:9998;pointer-events:none;overflow:hidden;">
                {_globos_items}
            </div>
            <style>
                .globo-up{{position:absolute;top:110vh;opacity:0.9;animation:subir-g linear forwards;}}
                @keyframes subir-g{{0%{{top:110vh;opacity:1;transform:translateX(0);}}50%{{transform:translateX(12px);}}100%{{top:-15vh;opacity:0;transform:translateX(-8px);}}}}
            </style>
            <div style="text-align:center;background:linear-gradient(90deg,#c60b1e,#e07010,#f1bf00);border-radius:12px;padding:14px 24px;margin:0 0 18px 0;box-shadow:0 3px 10px rgba(0,0,0,0.15);">
                <p style="color:#ffffff;font-size:1.05rem;font-weight:800;margin:0;text-shadow:0 1px 3px rgba(0,0,0,0.3);">{_frase_dia}</p>
            </div>
        """, unsafe_allow_html=True)

        # 3. CARGA DE DATOS
        de, dt, da = load_and_clean_ranking()

        # 4. FILTROS (IZQUIERDA) Y VIDEO (DERECHA)
        c_filtros, c_video = st.columns([2, 1])
        
        with c_filtros:
            st.markdown('<p style="color:#d2ff00; font-weight:bold; margin-bottom:0;">📅 FILTROS</p>', unsafe_allow_html=True)
            meses_disp = sorted(list(set(de['Mes']) | set(dt['Mes']) | set(da['Mes'])))
            f_mes = st.multiselect("Mes:", meses_disp, default=[meses_disp[-1]] if meses_disp else [])
            
            coms_disp = sorted(list(set(de['Comercial']) | set(dt['Comercial']) | set(da['Comercial'])))
            f_coms = st.multiselect("Comerciales:", coms_disp, default=coms_disp)

        with c_video:
            video_file = "WhatsApp Video 2026-04-28 at 00.31.03.mp4"
            st.markdown('<p style="color:#d2ff00; font-size:0.7rem; text-align:right; margin-bottom:0;">🔊 Música Rosco</p>', unsafe_allow_html=True)
            st.video(video_file, format="video/mp4")

        # 4. APLICAR FILTROS
        f_de = de[(de['Mes'].isin(f_mes)) & (de['Comercial'].isin(f_coms))].copy()
        f_dt = dt[(dt['Mes'].isin(f_mes)) & (dt['Comercial'].isin(f_coms))].copy()
        f_da = da[(da['Mes'].isin(f_mes)) & (da['Comercial'].isin(f_coms))].copy()

        # 5. PROCESAMIENTO DETALLADO
        if not f_de.empty:
            f_de['V_REF'] = f_de['Canal'].apply(lambda x: 1 if str(x).strip().upper() == "REF" else 0) if 'Canal' in f_de.columns else 0
            f_de['Baja_E'] = f_de['Estado'].apply(lambda x: 1 if str(x).strip().upper() == "BAJA" else 0) if 'Estado' in f_de.columns else 0
            f_de['Cancel_E'] = f_de['Estado'].apply(lambda x: 1 if str(x).strip().upper() == "CANCELADO" else 0) if 'Estado' in f_de.columns else 0

        if not f_dt.empty:
            f_dt['V_REF'] = f_dt['Canal'].apply(lambda x: 1 if str(x).strip().upper() == "REF" else 0) if 'Canal' in f_dt.columns else 0
            f_dt['Baja_F'] = f_dt['Estado'].apply(lambda x: 1 if str(x).strip().upper() == "BAJA" else 0) if 'Estado' in f_dt.columns else 0
            f_dt['Cancel_F'] = f_dt['Estado'].apply(lambda x: 1 if str(x).strip().upper() == "CANCELADO" else 0) if 'Estado' in f_dt.columns else 0

        if not f_da.empty:
            f_da['V_REF'] = f_da['Canal'].apply(lambda x: 1 if str(x).strip().upper() == "REF" else 0) if 'Canal' in f_da.columns else 0
            f_da['Baja_A'] = f_da['Estado'].apply(lambda x: 1 if str(x).strip().upper() == "BAJA" else 0) if 'Estado' in f_da.columns else 0
            f_da['Cancel_A'] = f_da['Estado'].apply(lambda x: 1 if str(x).strip().upper() == "CANCELADO" else 0) if 'Estado' in f_da.columns else 0

        r1 = f_de.groupby('Comercial')[['V_Luz', 'V_Gas', 'V_REF', 'Baja_E', 'Cancel_E']].sum() if not f_de.empty else pd.DataFrame()
        r2 = f_dt.groupby('Comercial')[['V_Fibra', 'V_Móvil', 'V_REF', 'Baja_F', 'Cancel_F']].sum() if not f_dt.empty else pd.DataFrame()
        r3 = f_da.groupby('Comercial')[['V_Alarma', 'V_REF']].sum() if not f_da.empty else pd.DataFrame()
        
        rank = pd.concat([r1, r2, r3], axis=1).fillna(0)
        rank['REF'] = rank.filter(like='V_REF').sum(axis=1)
        rank['Bajas_Total'] = rank.filter(like='Baja_').sum(axis=1)
        rank['Cancel_Total'] = rank.filter(like='Cancel_').sum(axis=1)
        rank['Ventas_Sin_Movil'] = (rank.get('V_Luz',0) + rank.get('V_Gas',0) + rank.get('V_Fibra',0) + rank.get('V_Alarma',0))
        
        # Total Neto para el objetivo individual
        rank['Total Neto'] = rank['Ventas_Sin_Movil'] - rank['Bajas_Total'] - rank['Cancel_Total']
        # Solo MARIA JOSE ARACIL tiene objetivo (25). Raquel Guadalupe no tiene.
        def _faltan(nombre):
            n = str(nombre).upper()
            if "MARIA JOSE" in n and "ARACIL" in n:
                return max(0, 25 - int(rank.loc[nombre, 'Total Neto']))
            return 0
        rank['Faltan para 25'] = rank.index.to_series().apply(_faltan)

        # 6. CABECERA TÍTULO (Sin Nº1)
        st.markdown("""
            <div style="text-align: center; margin: 20px 0;">
                <h1 style="color: #d2ff00; font-size: 2.1rem; margin-bottom:5px;">"EL ÉXITO ES EL RESULTADO DE LA DISCIPLINA DIARIA"</h1>
            </div>
        """, unsafe_allow_html=True)

        # 7. OBJETIVO EQUIPO
        v_equipo_neta = int(rank['Total Neto'].sum())
        v_falta_equipo = max(0, 25 - v_equipo_neta)  # Objetivo equipo = 25 (1 comercial activa)
        st.markdown(f'<div style="background:#ffffff;padding:15px;border-radius:15px;border:1px solid #30363d;margin:0 auto 20px auto;text-align:center;max-width:320px;"><p style="color:#d2ff00;margin:0;font-weight:bold;font-size:0.9rem;">🚀 FALTAN PARA EL OBJETIVO</p><h1 style="color:#111111;margin:0;font-size:2.8rem;">{v_falta_equipo}</h1></div>', unsafe_allow_html=True)

        # 8. TABLA DE RANKING
        df_vis = rank.rename(columns={'V_Luz':'Luz','V_Gas':'Gas','V_Fibra':'Fibra','V_Móvil':'Móvil','V_Alarma':'Alarma','Bajas_Total':'Bajas','Cancel_Total':'Cancelados'})
        cols_tab = ['Luz','Gas','Fibra','Móvil','Alarma','REF','Bajas','Cancelados','Total Neto','Faltan para 25']
        st.table(df_vis[[c for c in cols_tab if c in df_vis.columns]].astype(int).sort_values('Total Neto', ascending=False).style.apply(
            lambda x: ['background-color: rgba(210, 255, 0, 0.2); color: #d2ff00; font-weight: bold' if x.name in ['Total Neto', 'Faltan para 25'] else '' for i in x], axis=1))

        # 9. TOTALES INFERIORES BRUTOS
        st.markdown("---")
        st.markdown('<p style="color:#d2ff00; font-weight:bold; text-align:center;">📊 TOTALES BRUTOS (VENTAS SIN DESCUENTOS)</p>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        box = "background:#f0f0f0; border:2px solid #d2ff00; padding:15px; border-radius:10px; text-align:center;"
        
        c1.markdown(f'<div style="{box}"><p style="color:#d2ff00;font-size:0.8rem;margin:0;">ENERGÍA BRUTA</p><h2 style="color:#111111;margin:0;">{int(rank["V_Luz"].sum() + rank["V_Gas"].sum()) if "V_Luz" in rank else 0}</h2></div>', unsafe_allow_html=True)
        c2.markdown(f'<div style="{box}"><p style="color:#d2ff00;font-size:0.8rem;margin:0;">FIBRA BRUTA</p><h2 style="color:#111111;margin:0;">{int(rank["V_Fibra"].sum()) if "V_Fibra" in rank else 0}</h2></div>', unsafe_allow_html=True)
        c3.markdown(f'<div style="{box}"><p style="color:#d2ff00;font-size:0.8rem;margin:0;">ALARMA BRUTA</p><h2 style="color:#111111;margin:0;">{int(rank["V_Alarma"].sum()) if "V_Alarma" in rank else 0}</h2></div>', unsafe_allow_html=True)
        c4.markdown(f'<div style="{box} background:#d2ff00;"><p style="color:black;font-weight:bold;margin:0;">TOTAL BRUTO</p><h2 style="color:black;margin:0;">{int(rank["Ventas_Sin_Movil"].sum())}</h2></div>', unsafe_allow_html=True)

        # 10. NUEVOS CUADROS: CANCELACIONES Y BAJAS
        st.markdown("<br>", unsafe_allow_html=True)
        cx1, cx2, cx3, cx4 = st.columns(4)
        box_alt = "background:#ffffff; border:1px solid #ff4b4b; padding:15px; border-radius:10px; text-align:center;"
        
        cx1.markdown(f'<div style="{box_alt}"><p style="color:#ff4b4b;font-size:0.75rem;margin:0;">CANCEL. ENERGÍA</p><h3 style="color:#111111;margin:0;">{int(rank["Cancel_E"].sum()) if "Cancel_E" in rank else 0}</h3></div>', unsafe_allow_html=True)
        cx2.markdown(f'<div style="{box_alt}"><p style="color:#ff4b4b;font-size:0.75rem;margin:0;">CANCEL. FIBRA</p><h3 style="color:#111111;margin:0;">{int(rank["Cancel_F"].sum()) if "Cancel_F" in rank else 0}</h3></div>', unsafe_allow_html=True)
        cx3.markdown(f'<div style="{box_alt}"><p style="color:#ff4b4b;font-size:0.75rem;margin:0;">BAJAS ENERGÍA</p><h3 style="color:#111111;margin:0;">{int(rank["Baja_E"].sum()) if "Baja_E" in rank else 0}</h3></div>', unsafe_allow_html=True)
        cx4.markdown(f'<div style="{box_alt}"><p style="color:#ff4b4b;font-size:0.75rem;margin:0;">BAJAS FIBRA</p><h3 style="color:#111111;margin:0;">{int(rank["Baja_F"].sum()) if "Baja_F" in rank else 0}</h3></div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error en Dashboard: {e}")


#-----REPOSITORIO----
elif menu == "📂 REPOSITORIO":
    import os  # Crucial para que funcionen las carpetas
    st.markdown('<div class="block-header">📂 REPOSITORIO DE DOCUMENTACIÓN</div>', unsafe_allow_html=True)

    # Función Maestra: Escanea la carpeta y genera botones para CADA archivo válido
    def mostrar_contenido_carpeta(nombre_carpeta, titulo_visible, icono="📁"):
        # Construimos la ruta buscando exactamente como se llaman tus carpetas
        ruta_especifica = os.path.join("manuales", nombre_carpeta)
        
        if os.path.exists(ruta_especifica):
            with st.expander(f"{icono} {titulo_visible}"):
                try:
                    # Listamos todos los archivos reales (.pdf, .jpg, .png, etc.)
                    archivos = [f for f in os.listdir(ruta_especifica) if os.path.isfile(os.path.join(ruta_especifica, f))]
                    
                    if archivos:
                        for filename in archivos:
                            ruta_archivo = os.path.join(ruta_especifica, filename)
                            with open(ruta_archivo, "rb") as f:
                                contenido = f.read()
                                ext = filename.split('.')[-1].lower()
                                
                                # Filtrar y asignar el MIME type adecuado para los formatos solicitados
                                if ext == "pdf":
                                    m_type = "application/pdf"
                                elif ext == "docx":
                                    m_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                elif ext in ["jpg", "jpeg", "png"]:
                                    m_type = f"image/{ext}"
                                else:
                                    m_type = "application/octet-stream"  # Tipo genérico por si hay algún otro archivo
                                
                                st.download_button(
                                    label=f"📄 Ver/Descargar: {filename}",
                                    data=contenido,
                                    file_name=filename,
                                    mime=m_type,
                                    key=f"btn_{nombre_carpeta}_{filename}".replace(" ", "_")
                                )
                    else:
                        st.write("ℹ️ Esta carpeta está vacía.")
                except Exception as e:
                    st.error(f"Error al leer la carpeta {nombre_carpeta}: {e}")
        else:
            # Si sale este mensaje es que el nombre de la carpeta no coincide con el disco duro
            st.caption(f"🚫 No detectada: manuales/{nombre_carpeta}")


    # --- DISTRIBUCIÓN SEGÚN TUS CARPETAS EN MAYÚSCULAS ---
    col_a, col_b = st.columns(2)

    with col_a:
        mostrar_contenido_carpeta("MARCADOR", "MANUAL DEL MARCADOR", "📂")
        mostrar_contenido_carpeta("ARGUMENTARIO", "ARGUMENTARIOS DE VENTAS", "📝")
        mostrar_contenido_carpeta("TARIFAS O2", "TARIFAS O2", "📱")
        mostrar_contenido_carpeta("TARIFAS LOWI", "TARIFAS LOWI", "📱")
        mostrar_contenido_carpeta("TARIFAS SEGURMA", "DOCUMENTACIÓN SEGURMA", "🛡️")

    with col_b:
        mostrar_contenido_carpeta("TARIFAS ENDESA", "TARIFAS ENDESA", "⚡")
        mostrar_contenido_carpeta("TARIFAS IBERDROLA", "TARIFAS IBERDROLA", "⚡")
        mostrar_contenido_carpeta("TARIFAS NATURGY", "TARIFAS NATURGY", "⚡")
        mostrar_contenido_carpeta("TARIFAS TOTAL", "TARIFAS TOTAL ENERGIES", "⚡")
        mostrar_contenido_carpeta("TARIFAS GANA", "TARIFAS GANA ENERGÍA", "⚡")
        # Nueva carpeta añadida manteniendo el formato y los iconos correspondientes
        mostrar_contenido_carpeta("TARIFAS 3D", "TARIFAS 3D", "⚡")

    st.markdown("---")

# --- CONTROL LABORAL ---
elif menu == "🕒 CONTROL LABORAL":
    import pandas as pd
    import calendar
    from datetime import datetime, time, date
    st.markdown('<div class="block-header">🕒 CONTROL LABORAL Y ASISTENCIA</div>', unsafe_allow_html=True)
    
    # ── BAJAS DE EMPRESA ── (no cuentan como falta durante su periodo en la empresa)
    # fecha_alta: primer día que trabaja | fecha_baja: último día que trabaja (None = sigue activa)
    empleados_empresa = {
        "BELEN TRONCOSO CAMPOS":      {"alta": date(2026, 3, 16), "baja": date(2026, 5, 20)},
        "DEBORAH RODRIGUEZ URBINA":   {"alta": date(2026, 3, 16), "baja": date(2026, 5, 13)},
        "LORENA POZO ALVAREZ":        {"alta": date(2026, 3, 16), "baja": date(2026, 6, 17)},
        "MACARENA BACA LOPEZ":        {"alta": date(2026, 3, 16), "baja": date(2026, 3, 19)},
        "LUIS RODRIGUEZ GOMEZ":       {"alta": date(2025, 4,  6), "baja": date(2026, 4, 24)},
        "MARIA JOSE MORENO":          {"alta": date(2026, 5,  4), "baja": date(2026, 5, 18)},
        "LAURA RUBIO GARCIA":         {"alta": date(2026, 5, 25), "baja": date(2026, 5, 27)},
        "MARIA JOSE ARACIL RUEDA":    {"alta": date(2026, 5,  4), "baja": None},   # activa
        "RAQUEL GUADALUPE CASTILLO":  {"alta": date(2026, 3, 2), "baja": None},    # activa
    }

    # Periodo de gracia: del 02/03 al 18/03 Raquel aparece como OK aunque no haya fichado
    PERIODOS_GRACIA = {
        "RAQUEL GUADALUPE CASTILLO": (date(2026, 3, 2), date(2026, 3, 18)),
    }

    def empleado_activo_en_fecha(nombre_comercial, fecha):
        nombre_up = nombre_comercial.upper()
        for emp, periodos in empleados_empresa.items():
            if emp.upper() in nombre_up or nombre_up in emp.upper():
                alta = periodos["alta"]
                baja = periodos["baja"]
                if alta <= fecha:
                    if baja is None or fecha <= baja:
                        return True
        return False

    def en_periodo_gracia(nombre_comercial, fecha):
        nombre_up = nombre_comercial.upper()
        for emp, (inicio, fin) in PERIODOS_GRACIA.items():
            if emp.upper() in nombre_up or nombre_up in emp.upper():
                if inicio <= fecha <= fin:
                    return True
        return False

    # ── VACACIONES ──
    vacaciones = {
        "RAQUEL GUADALUPE": (date(2026, 6, 22), date(2026, 6, 28)),
        "MARIA JOSE ARACIL": (date(2026, 8, 3), date(2026, 8, 9))
    }

    # ── PANEL DE INFO ──
    tab_vac, tab_emp = st.tabs(["🏖️ Vacaciones Programadas", "👥 Plantilla / Bajas Empresa"])

    with tab_vac:
        cols = st.columns(len(vacaciones))
        for i, (nombre, (inicio, fin)) in enumerate(vacaciones.items()):
            dias_hasta = (inicio - date.today()).days
            estado_color = "#d2ff00" if dias_hasta > 7 else "#ffaa00" if dias_hasta > 0 else "#7ee787"
            cols[i].markdown(f"""
                <div style="background:#ffffff; padding:15px; border-radius:10px; border:2px solid {estado_color}; text-align:center;">
                <p style="margin:0; font-size:0.85rem; color:{estado_color}; font-weight:bold;">{nombre}</p>
                <b style="font-size:1rem; color:white;">{inicio.strftime('%d/%m/%Y')} → {fin.strftime('%d/%m/%Y')}</b>
                <p style="margin:4px 0 0 0; font-size:0.75rem; color:#8b949e;">{(fin - inicio).days + 1} días laborables</p>
                </div>
            """, unsafe_allow_html=True)

    with tab_emp:
        st.markdown('<p style="color:#8b949e; font-size:0.85rem; margin-bottom:10px;">Los días fuera del rango Alta–Baja se marcan como <b style="color:#888">BAJA EMPRESA</b> y no computan como falta.</p>', unsafe_allow_html=True)
        activas = {k: v for k, v in empleados_empresa.items() if v["baja"] is None}
        bajas   = {k: v for k, v in empleados_empresa.items() if v["baja"] is not None}
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<p style="color:#7ee787; font-weight:bold;">✅ Activas en plantilla</p>', unsafe_allow_html=True)
            for nombre, p in activas.items():
                st.markdown(f'<div style="background:#f0fff4; border:1px solid #7ee787; border-radius:8px; padding:8px 12px; margin-bottom:6px;"><span style="color:#111111; font-size:0.9rem;">{nombre}</span><br><span style="color:#8b949e; font-size:0.75rem;">Alta: {p["alta"].strftime("%d/%m/%Y")}</span></div>', unsafe_allow_html=True)
        with col_b:
            st.markdown('<p style="color:#ff4b4b; font-weight:bold;">📋 Bajas procesadas</p>', unsafe_allow_html=True)
            for nombre, p in bajas.items():
                st.markdown(f'<div style="background:#fff0f0; border:1px solid #30363d; border-radius:8px; padding:8px 12px; margin-bottom:6px;"><span style="color:#8b949e; font-size:0.9rem;">{nombre}</span><br><span style="color:#8b949e; font-size:0.75rem;">Alta: {p["alta"].strftime("%d/%m/%Y")} · Baja: {p["baja"].strftime("%d/%m/%Y")}</span></div>', unsafe_allow_html=True)

    st.markdown("---")

    try:
        # ── CARGA Y LIMPIEZA ──
        sheet_id = "175LGa4j6dAhsjQ7Wiy-8tZnKWuDC9_C9uy6SYC-i-LY"
        url_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        df_laboral = pd.read_csv(url_csv)
        df_laboral.columns = [str(c).strip().upper() for c in df_laboral.columns]
        
        col_comercial = next((c for c in df_laboral.columns if "QUIÉN" in c or "COMERCIAL" in c), None)
        col_temporal  = next((c for c in df_laboral.columns if "TEMPORAL" in c or "MARCA" in c), None)
        col_accion    = next((c for c in df_laboral.columns if "HACER" in c), None)
        
        df_laboral[col_temporal] = pd.to_datetime(df_laboral[col_temporal], dayfirst=True, errors='coerce')
        df_laboral = df_laboral.dropna(subset=[col_temporal, col_comercial])

        # ── FILTROS ──
        col_f1, col_f2 = st.columns(2)
        coms    = sorted(df_laboral[col_comercial].unique().astype(str))
        com_sel = col_f1.selectbox("👤 Selecciona Comercial", coms)
        mes_sel = col_f2.selectbox("📅 Selecciona Mes", range(1, 13), index=datetime.now().month - 1)

        # ── BADGE HORARIO DEL COMERCIAL SELECCIONADO ──
        if "RAQUEL" in com_sel.upper() and "GUADALUPE" in com_sel.upper():
            st.markdown('<div style="background:#fffbf0; border:2px solid #f1bf00; border-radius:8px; padding:8px 16px; margin-bottom:10px; display:inline-block;"><span style="color:#b38a00; font-weight:bold;">⏰ Horario:</span> <span style="color:#111111;">09:00 – 14:30 · 17:00 – 19:30 (turno partido)</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background:#ffffff; border:1px solid #30363d; border-radius:8px; padding:8px 16px; margin-bottom:10px; display:inline-block;"><span style="color:#d2ff00; font-weight:bold;">⏰ Horario:</span> <span style="color:#111111;">09:30 – 14:30</span></div>', unsafe_allow_html=True)

        # ── LÓGICA DE AUDITORÍA ──
        festivos = [
            date(2026, 4, 2), date(2026, 4, 3), date(2026, 4, 22),
            date(2026, 5, 1), date(2026, 5, 29), date(2026, 6, 4)
        ]

        # ── HORARIOS POR COMERCIAL ──
        # General: 9:30 – 14:30 (comerciales)
        # Raquel:  9:00 – 14:30 + 17:00 – 19:30 (turno partido)
        def get_horario(nombre):
            if "RAQUEL" in nombre.upper() and "GUADALUPE" in nombre.upper():
                return {
                    "entrada": time(9, 0),
                    "partido": True,
                    "tarde_inicio": time(17, 0),
                    "tarde_fin":    time(19, 30),
                }
            return {
                "entrada": time(9, 30),
                "partido": False,
            }

        datos = df_laboral[
            (df_laboral[col_comercial] == com_sel) &
            (df_laboral[col_temporal].dt.month == mes_sel)
        ].copy()

        horario = get_horario(com_sel)
        hora_entrada_limite = horario["entrada"]
        es_turno_partido = horario.get("partido", False)

        min_ret, faltas, dias_vac, dias_baja_emp = 0, 0, 0, 0
        historial_diario = []
        dias_mes = calendar.monthrange(2026, mes_sel)[1]

        for d in range(1, dias_mes + 1):
            fecha = date(2026, mes_sel, d)
            if fecha > date.today(): break
            if fecha.weekday() >= 5 or fecha in festivos: continue

            # ── Baja de empresa: no computa ──
            activo = empleado_activo_en_fecha(com_sel, fecha)
            if not activo:
                dias_baja_emp += 1
                historial_diario.append({
                    "Fecha": fecha, "Entrada": "-", "Salida": "-",
                    "Incidencia": "🔴 BAJA EMPRESA"
                })
                continue

            # ── Vacaciones ──
            es_vac = any(com_sel.upper() in nom.upper() and i <= fecha <= f for nom, (i, f) in vacaciones.items())
            if es_vac:
                dias_vac += 1
                historial_diario.append({
                    "Fecha": fecha, "Entrada": "-", "Salida": "-",
                    "Incidencia": "🏖️ VACACIONES"
                })
                continue

            dia_data = datos[datos[col_temporal].dt.date == fecha]
            entradas = dia_data[dia_data[col_accion].str.contains("ENTRADA", case=False, na=False)]
            salidas  = dia_data[dia_data[col_accion].str.contains("SALIDA",  case=False, na=False)]

            h_in  = entradas[col_temporal].min().time() if not entradas.empty else None
            h_out = salidas[col_temporal].max().time()  if not salidas.empty  else None

            if not entradas.empty:
                incidencia = "✅ OK"

                # ── Cálculo retraso entrada ──
                if h_in > hora_entrada_limite:
                    retraso = (datetime.combine(fecha, h_in) - datetime.combine(fecha, hora_entrada_limite)).total_seconds() / 60
                    min_ret += retraso
                    incidencia = f"⚠️ RETRASO ENTRADA ({int(retraso)}m)"

                # ── Turno partido (Raquel): usa un único login/logout, no se comprueba tarde ──
                if es_turno_partido:
                    historial_diario.append({
                        "Fecha":    fecha,
                        "Entrada":  str(h_in)[:5] if h_in else "-",
                        "Salida":   str(h_out)[:5] if h_out else "—",
                        "Incidencia": incidencia
                    })
                else:
                    historial_diario.append({
                        "Fecha":   fecha,
                        "Entrada": str(h_in)[:5] if h_in else "-",
                        "Salida":  str(h_out)[:5] if h_out else "—",
                        "Incidencia": incidencia
                    })
            else:
                # Periodo de gracia → OK aunque no haya fichaje
                if en_periodo_gracia(com_sel, fecha):
                    historial_diario.append({
                        "Fecha": fecha, "Entrada": "—", "Salida": "—", "Incidencia": "✅ OK"
                    })
                else:
                    faltas += 1
                    historial_diario.append({
                        "Fecha": fecha, "Entrada": "-", "Salida": "-", "Incidencia": "❌ FALTA"
                    })

        # ── DASHBOARD MÉTRICAS ──
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div style="background:#fff0f0; padding:15px; border-radius:10px; border-left:8px solid #ff4b4b; text-align:center;"><p style="color:#c60b1e; font-size:0.8rem; margin:0; font-weight:bold;">⏰ RETRASO ACUM.</p><h1 style="color:#111111; margin:5px 0;">{int(min_ret)} m</h1></div>', unsafe_allow_html=True)
        c2.markdown(f'<div style="background:#fffbf0; padding:15px; border-radius:10px; border-left:8px solid #f1bf00; text-align:center;"><p style="color:#b38a00; font-size:0.8rem; margin:0; font-weight:bold;">❌ FALTAS</p><h1 style="color:#111111; margin:5px 0;">{faltas}</h1></div>', unsafe_allow_html=True)
        c3.markdown(f'<div style="background:#f0fff4; padding:15px; border-radius:10px; border-left:8px solid #22c55e; text-align:center;"><p style="color:#166534; font-size:0.8rem; margin:0; font-weight:bold;">🏖️ VACACIONES</p><h1 style="color:#111111; margin:5px 0;">{dias_vac} d</h1></div>', unsafe_allow_html=True)
        c4.markdown(f'<div style="background:#f5f5f5; padding:15px; border-radius:10px; border-left:8px solid #6b7280; text-align:center;"><p style="color:#374151; font-size:0.8rem; margin:0; font-weight:bold;">🔴 BAJA EMPRESA</p><h1 style="color:#111111; margin:5px 0;">{dias_baja_emp} d</h1></div>', unsafe_allow_html=True)
        
        st.markdown("---")

        # ── TABLA HISTORIAL ──
        if historial_diario:
            df_hist = pd.DataFrame(historial_diario).sort_values("Fecha", ascending=False)
            df_hist["Fecha"] = df_hist["Fecha"].apply(lambda x: x.strftime("%a %d/%m/%Y").upper())

            def color_incidencia(val):
                if "FALTA" in val:       return "background-color: rgba(255,75,75,0.2); color: #ff4b4b; font-weight:bold"
                if "RETRASO" in val:     return "background-color: rgba(255,170,0,0.2); color: #ffaa00; font-weight:bold"
                if "VACACIONES" in val:  return "background-color: rgba(126,231,135,0.15); color: #7ee787"
                if "BAJA EMPRESA" in val:return "background-color: rgba(139,148,158,0.15); color: #8b949e"
                return "color: #7ee787"

            try:
                styled = df_hist.style.map(color_incidencia, subset=["Incidencia"])
            except AttributeError:
                styled = df_hist.style.applymap(color_incidencia, subset=["Incidencia"])
            st.dataframe(styled, use_container_width=True, height=450)
        else:
            st.info("Sin registros en este periodo.")

    except Exception as e:
        st.error(f"Error procesando datos: {e}")

# ══════════════════════════════════════════════════════
# --- ZONA BACKOFFICE ---
# ══════════════════════════════════════════════════════
elif menu == "🔐 ZONA BACKOFFICE":
    import os
    from datetime import datetime

    # ── CSS adicional para la zona backoffice ──
    st.markdown("""
        <style>
        .dir-header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            border: 2px solid #gold;
            border-image: linear-gradient(135deg, #FFD700, #FFA500) 1;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            margin-bottom: 30px;
        }
        .dir-card {
            background: linear-gradient(135deg, #161b22, #1c2430);
            border: 1px solid #FFD700;
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 12px;
            transition: all 0.3s;
        }
        .dir-card:hover { border-color: #FFA500; transform: translateY(-3px); }
        .gold-badge {
            background: linear-gradient(135deg, #FFD700, #FFA500);
            color: black;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    # ── AUTENTICACIÓN DIRECTIVOS ──
    # Preservar dir_auth explícitamente en cada rerun
    if "dir_auth" not in st.session_state:
        st.session_state["dir_auth"] = False
    # Re-leer para asegurar persistencia
    _dir_auth_ok = st.session_state.get("dir_auth", False)

    if not _dir_auth_ok:
        st.markdown("""
            <div style="background:linear-gradient(135deg,#f0f4ff,#e8eeff); border:2px solid #FFD700;
                        border-radius:20px; padding:40px; text-align:center; max-width:450px; margin:60px auto;">
                <h1 style="color:#FFD700; font-size:2.5rem; margin-bottom:5px;">🔐</h1>
                <h2 style="color:#FFD700; margin-bottom:5px;">ZONA BACKOFFICE</h2>
                <p style="color:#8b949e; font-size:0.9rem;">Acceso restringido · Basette Group</p>
            </div>
        """, unsafe_allow_html=True)

        _, col_dir, _ = st.columns([1, 1.2, 1])
        with col_dir:
            pwd_dir = st.text_input("🔑 Clave Directivos:", type="password", key="pwd_dir_input")
            if st.button("ACCEDER A ZONA BACKOFFICE", use_container_width=True):
                if pwd_dir == st.secrets["CLAVE_DIRECTIVOS"]:
                    st.session_state["dir_auth"] = True
                    st.session_state["_dir_auth_ts"] = True  # flag extra de persistencia
                    st.rerun()
                else:
                    st.error("❌ Clave incorrecta. Acceso denegado.")
        st.stop()

    # Consolidar auth en session_state antes de cualquier widget
    if st.session_state.get("_dir_auth_ts", False):
        st.session_state["dir_auth"] = True
    if st.session_state.get("dir_auth", False):
        st.session_state["_dir_auth_ts"] = True

    if st.session_state.get("dir_auth", False):
        # ── CONTENIDO ZONA BACKOFFICE (solo si autenticado) ──
        st.markdown("""
            <div style="background:linear-gradient(135deg,#f0f4ff,#e8eeff); border:2px solid #FFD700;
                        border-radius:15px; padding:25px; text-align:center; margin-bottom:25px;">
                <h2 style="color:#FFD700; margin:0;">🏛️ ZONA BACKOFFICE · BASETTE GROUP</h2>
                <p style="color:#8b949e; margin:5px 0 0 0; font-size:0.85rem;">Área de acceso restringido · Documentación confidencial</p>
            </div>
        """, unsafe_allow_html=True)

        # Botón cerrar sesión directivos
        col_cerrar = st.columns([5, 1])
        with col_cerrar[1]:
            if st.button("🔒 Cerrar sesión", key="cerrar_dir"):
                st.session_state["dir_auth"] = False
                st.rerun()

        # ── MENÚ VERTICAL LATERAL ──
        _opciones_menu = [
            "👥 PERSONAL",
            "💰 MARCOS RETRIBUTIVOS",
            "💼 NÓMINAS",
            "📊 LIQUIDACIONES",
            "🔀 CRUCES CIAS",
            "📁 DOCS EMPRESA",
            "🛠️ SOPORTE"
        ]
        with st.sidebar:
            st.markdown('<p style="color:#FFD700; font-weight:bold; font-size:0.8rem; margin:0 0 8px 4px;">⚙️ MENÚ DIRECTIVOS</p>', unsafe_allow_html=True)
            _menu_sel = st.radio(
                "Sección directivos:",
                _opciones_menu,
                key="dir_menu_sel",
                label_visibility="collapsed"
            )
            st.markdown("---")

        # Mapear selección a variables compatibles con el código existente
        _sel = _menu_sel

        # ══════════════════════════════════════════════════════
        # ── GOOGLE DRIVE — ID raíz de BASETTE_DIRECTIVOS ──
        # ══════════════════════════════════════════════════════
        DRIVE_ROOT_ID = "1BC-HcnyFYnHZKM3BoOhKNkR4m7GSCVng"
        DRIVE_API_KEY = st.secrets["DRIVE_API_KEY"]

        import urllib.request, urllib.parse, json as _json

        @st.cache_data(ttl=300, show_spinner=False)
        def drive_list_folder(folder_id):
            """Lista todo el contenido de una carpeta de Drive usando API Key."""
            try:
                q      = urllib.parse.quote(f"'{folder_id}' in parents and trashed=false")
                fields = urllib.parse.quote("files(id,name,mimeType,size)")
                url = (
                    f"https://www.googleapis.com/drive/v3/files"
                    f"?q={q}&fields={fields}&orderBy=name&key={DRIVE_API_KEY}"
                )
                with urllib.request.urlopen(url, timeout=10) as r:
                    data = _json.loads(r.read())
                return data.get("files", [])
            except Exception:
                return []

        @st.cache_data(ttl=300, show_spinner=False)
        def drive_find_subfolder(parent_id, name):
            """Devuelve el ID de subcarpeta: primero exacto (sin acento/espacios), luego contiene."""
            items = drive_list_folder(parent_id)
            name_norm = name.strip().upper()
            # 1. Exact match (case-insensitive)
            for item in items:
                if (item.get("mimeType") == "application/vnd.google-apps.folder"
                        and item.get("name", "").strip().upper() == name_norm):
                    return item["id"]
            # 2. Contains match (busca si el nombre de Drive contiene nuestra búsqueda)
            for item in items:
                if (item.get("mimeType") == "application/vnd.google-apps.folder"
                        and name_norm in item.get("name", "").strip().upper()):
                    return item["id"]
            # 3. Our name contains the Drive name (nombre Drive es prefijo del nuestro)
            for item in items:
                drv = item.get("name", "").strip().upper()
                if (item.get("mimeType") == "application/vnd.google-apps.folder"
                        and drv and drv in name_norm):
                    return item["id"]
            return None

        @st.cache_data(ttl=300, show_spinner=False)
        def drive_folder_id_by_path(path_tuple):
            """Navega la jerarquía por nombres. path_tuple = ("NOMINAS","2026","JUNIO")"""
            current_id = DRIVE_ROOT_ID
            for part in path_tuple:
                current_id = drive_find_subfolder(current_id, part)
                if not current_id:
                    return None
            return current_id

        def _render_drive_items(folder_id, icono="📄", depth=0):
            """Renderiza archivos y subcarpetas de una carpeta Drive de forma recursiva."""
            items = drive_list_folder(folder_id)
            if not items:
                if depth == 0:
                    st.info("📭 Carpeta vacía o sin acceso.")
                return

            archivos   = [f for f in items if f.get("mimeType") != "application/vnd.google-apps.folder"]
            subcarpetas = [f for f in items if f.get("mimeType") == "application/vnd.google-apps.folder"]

            # Mostrar subcarpetas primero como expanders
            for sub in subcarpetas:
                with st.expander(f"📁 {sub['name']}", expanded=False):
                    _render_drive_items(sub["id"], icono, depth + 1)

            # Mostrar archivos
            for f in archivos:
                fid      = f["id"]
                fname    = f["name"]
                size_kb  = int(f.get("size", 0)) // 1024 if f.get("size") else 0
                size_str = f" · {size_kb} KB" if size_kb else ""
                # Enlace para visualizar; para Google Docs usar export
                mime = f.get("mimeType", "")
                if "spreadsheet" in mime:
                    view_url = f"https://docs.google.com/spreadsheets/d/{fid}/edit"
                elif "document" in mime:
                    view_url = f"https://docs.google.com/document/d/{fid}/edit"
                elif "presentation" in mime:
                    view_url = f"https://docs.google.com/presentation/d/{fid}/edit"
                else:
                    view_url = f"https://drive.google.com/file/d/{fid}/view"

                col_a, col_b = st.columns([5, 1])
                with col_a:
                    st.markdown(
                        f'<div style="background:#eef4fb; border:1px solid #c0d8ee; border-radius:8px; '
                        f'padding:8px 12px; margin-bottom:4px;">'
                        f'<span style="color:#111111; font-size:0.9rem;">{icono} {fname}</span>'
                        f'<span style="color:#666666; font-size:0.75rem;">{size_str}</span></div>',
                        unsafe_allow_html=True
                    )
                with col_b:
                    st.link_button("⬇️ Abrir", view_url, use_container_width=True)

        def mostrar_carpeta_drive(path_parts, icono="📄"):
            """Muestra archivos Y subcarpetas de una carpeta Drive."""
            folder_id = drive_folder_id_by_path(tuple(path_parts))
            if not folder_id:
                # Mostrar diagnóstico: qué hay en el padre
                if len(path_parts) > 1:
                    parent_id = drive_folder_id_by_path(tuple(path_parts[:-1]))
                    if parent_id:
                        items_padre = drive_list_folder(parent_id)
                        carpetas_padre = [i["name"] for i in items_padre if i.get("mimeType") == "application/vnd.google-apps.folder"]
                        st.warning(f"⚠️ No encontré '{path_parts[-1]}'. Carpetas disponibles en el padre: {carpetas_padre}")
                        return
                st.caption(f"🚫 Carpeta no encontrada: {' / '.join(path_parts)}")
                return
            _render_drive_items(folder_id, icono)

        def mostrar_carpeta_dir(ruta_base, nombre_carpeta, icono="📄"):
            """Wrapper de compatibilidad: traduce rutas locales a path_parts de Drive."""
            parts = [p for p in nombre_carpeta.replace("\\", "/").split("/") if p]
            mostrar_carpeta_drive(parts, icono)


            # ── TAB PERSONAL ──
        if _sel == "👥 PERSONAL":
            st.markdown('<div class="block-header">👥 GESTIÓN DE PERSONAL</div>', unsafe_allow_html=True)


            # Resumen de plantilla actual
            from datetime import date
            empleados_dir = {
                "RAQUEL GUADALUPE CASTILLO":  {"alta": date(2026, 3, 2),  "baja": None,           "estado": "✅ ACTIVA"},
                "MARIA JOSE ARACIL RUEDA":    {"alta": date(2026, 5,  4), "baja": None,           "estado": "✅ ACTIVA"},
                "BELEN TRONCOSO CAMPOS":      {"alta": date(2026, 3, 16), "baja": date(2026, 5, 20), "estado": "🔴 BAJA"},
                "DEBORAH RODRIGUEZ URBINA":   {"alta": date(2026, 3, 16), "baja": date(2026, 5, 13), "estado": "🔴 BAJA"},
                "LORENA POZO ALVAREZ":        {"alta": date(2026, 3, 16), "baja": date(2026, 6, 17), "estado": "🔴 BAJA"},
                "MACARENA BACA LOPEZ":        {"alta": date(2026, 3, 16), "baja": date(2026, 3, 19), "estado": "🔴 BAJA"},
                "LUIS RODRIGUEZ GOMEZ":       {"alta": date(2025, 4,  6), "baja": date(2026, 4, 24), "estado": "🔴 BAJA"},
                "MARIA JOSE MORENO":          {"alta": date(2026, 5,  4), "baja": date(2026, 5, 18), "estado": "🔴 BAJA"},
                "LAURA RUBIO GARCIA":         {"alta": date(2026, 5, 25), "baja": date(2026, 5, 27), "estado": "🔴 BAJA"},
            }

            activos = [k for k, v in empleados_dir.items() if v["baja"] is None]
            bajas_e = [k for k, v in empleados_dir.items() if v["baja"] is not None]

            col_res1, col_res2, col_res3 = st.columns(3)
            col_res1.markdown(f'<div style="background:#f0fff4;border:2px solid #7ee787;border-radius:12px;padding:20px;text-align:center;"><p style="color:#7ee787;margin:0;font-weight:bold;font-size:0.85rem;">ACTIVOS</p><h1 style="color:#111111;margin:5px 0;">{len(activos)}</h1></div>', unsafe_allow_html=True)
            col_res2.markdown(f'<div style="background:#fff0f0;border:2px solid #ff4b4b;border-radius:12px;padding:20px;text-align:center;"><p style="color:#ff4b4b;margin:0;font-weight:bold;font-size:0.85rem;">BAJAS HISTÓRICAS</p><h1 style="color:#111111;margin:5px 0;">{len(bajas_e)}</h1></div>', unsafe_allow_html=True)
            col_res3.markdown(f'<div style="background:#ffffff;border:2px solid #FFD700;border-radius:12px;padding:20px;text-align:center;"><p style="color:#FFD700;margin:0;font-weight:bold;font-size:0.85rem;">TOTAL HISTORIAL</p><h1 style="color:#111111;margin:5px 0;">{len(empleados_dir)}</h1></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            df_personal = pd.DataFrame([
                {
                    "Nombre": k,
                    "Alta": v["alta"].strftime("%d/%m/%Y"),
                    "Baja": v["baja"].strftime("%d/%m/%Y") if v["baja"] else "—",
                    "Estado": v["estado"],
                    "Días en empresa": (v["baja"] - v["alta"]).days if v["baja"] else (date.today() - v["alta"]).days
                }
                for k, v in empleados_dir.items()
            ])
            st.dataframe(df_personal, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown('<div class="block-header">📂 DOCUMENTACIÓN DE PERSONAL</div>', unsafe_allow_html=True)
            st.markdown("""
                <div style="background:#ffffff; border-left:4px solid #FFD700; padding:12px; border-radius:8px; margin-bottom:16px;">
                    <p style="color:#8b949e; margin:0; font-size:0.82rem;">Archivos desde Google Drive · Carpeta <b style="color:#FFD700;">PERSONAL</b></p>
                </div>
            """, unsafe_allow_html=True)

            # Carpetas y archivos según Drive real
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                with st.expander("👥 Empleados Actuales"):
                    mostrar_carpeta_drive(["PERSONAL", "EMPLEADOS ACTUALES"], "👤")
                with st.expander("🚫 Bajas / No Incorporaciones"):
                    mostrar_carpeta_drive(["PERSONAL", "BAJAS EMPLEADOS O NO INCORPORACIONES"], "📤")
                with st.expander("🖼️ Fotos"):
                    mostrar_carpeta_drive(["PERSONAL", "FOTOS"], "🖼️")
            with col_p2:
                with st.expander("📋 Plantillas, Certificados y Costes"):
                    mostrar_carpeta_drive(["PERSONAL", "PLANTILLAS BAJAS, CERTIFICADOS Y COSTES EMPLEADOS"], "📋")
                with st.expander("📊 Datos Empleados (Excel suelto)"):
                    # Buscar solo el Excel en la raíz de PERSONAL, sin mostrar subcarpetas
                    _pid = drive_folder_id_by_path(("PERSONAL",))
                    if _pid:
                        _items = drive_list_folder(_pid)
                        _excels = [f for f in _items
                                   if f.get("mimeType") != "application/vnd.google-apps.folder"
                                   and "DATOS EMPLEADOS" in f.get("name","").upper()]
                        if _excels:
                            for _f in _excels:
                                _url = f"https://docs.google.com/spreadsheets/d/{_f['id']}/edit"
                                _col1, _col2 = st.columns([5,1])
                                with _col1:
                                    st.markdown(f'<div style="background:#eef4fb;border:1px solid #c0d8ee;border-radius:8px;padding:8px 12px;">📊 {_f["name"]} · {int(_f.get("size",0))//1024} KB</div>', unsafe_allow_html=True)
                                with _col2:
                                    st.link_button("⬇️ Abrir", _url, use_container_width=True)
                        else:
                            st.info("No se encontró DATOS EMPLEADOS.xlsx en la carpeta PERSONAL.")
                    else:
                        st.warning("Carpeta PERSONAL no encontrada.")

        # ── TAB MARCOS RETRIBUTIVOS ──
        if _sel == "💰 MARCOS RETRIBUTIVOS":
            st.markdown('<div class="block-header">💰 MARCOS RETRIBUTIVOS</div>', unsafe_allow_html=True)
            st.markdown("""
                <div style="background:#ffffff; border-left:4px solid #FFD700; padding:15px; border-radius:8px; margin-bottom:20px;">
                    <p style="color:#FFD700; font-weight:bold; margin:0;">ℹ️ ÁREA CONFIDENCIAL</p>
                    <p style="color:#8b949e; margin:5px 0 0 0; font-size:0.85rem;">Los documentos de estructura salarial, bandas retributivas y comisiones se gestionan aquí.</p>
                </div>
            """, unsafe_allow_html=True)
            col_ret1, col_ret2 = st.columns(2)
            with col_ret1:
                with st.expander("📈 Escala de Comisiones"):
                    mostrar_carpeta_dir("directivos", "COMISIONES", "💰")
                with st.expander("🏷️ Bandas Salariales"):
                    mostrar_carpeta_dir("directivos", "BANDAS_SALARIALES", "💼")
            with col_ret2:
                with st.expander("🎯 Objetivos e Incentivos"):
                    mostrar_carpeta_dir("directivos", "INCENTIVOS", "🎯")
                with st.expander("📋 Contratos y Acuerdos"):
                    mostrar_carpeta_dir("directivos", "CONTRATOS", "📋")

        # ── TAB NÓMINAS ──
        if _sel == "💼 NÓMINAS":
            st.markdown('<div class="block-header">💼 GESTIÓN DE NÓMINAS</div>', unsafe_allow_html=True)
            st.markdown("""
                <div style="background:#ffffff; border-left:4px solid #FFD700; padding:15px; border-radius:8px; margin-bottom:20px;">
                    <p style="color:#8b949e; margin:0; font-size:0.85rem;">Los archivos se leen desde Google Drive · Carpeta <b style="color:#FFD700;">NOMINAS / AÑO / MES</b></p>
                </div>
            """, unsafe_allow_html=True)

            meses_nom = ["ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO",
                         "JULIO","AGOSTO","SEPTIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE"]
            col_nom_sel1, col_nom_sel2 = st.columns(2)
            anio_nom = col_nom_sel1.selectbox("📅 Año", ["2026", "2025", "2024"], key="anio_nom")
            mes_nom  = col_nom_sel2.selectbox("📅 Mes", meses_nom, index=datetime.now().month - 1, key="mes_nom")

            mostrar_carpeta_drive(["NOMINAS", anio_nom, mes_nom], "💼")

        # ── TAB LIQUIDACIONES ──
        if _sel == "📊 LIQUIDACIONES":
            st.markdown('<div class="block-header">📊 LIQUIDACIONES AUTOMÁTICAS</div>', unsafe_allow_html=True)

            # ══════════════════════════════════════════════════════
            # ── FUNCIONES DE CRUCE DE LIQUIDACIONES ──
            # ══════════════════════════════════════════════════════

            def normalize_cup(cup):
                """Normaliza CUP a 20 dígitos para comparación (si tiene 22, trunca)."""
                if cup is None or (hasattr(cup, '__class__') and cup.__class__.__name__ == 'float'):
                    return None
                import math
                try:
                    if math.isnan(float(str(cup))):
                        return None
                except (ValueError, TypeError):
                    pass
                s = str(cup).strip().upper()
                if not s or s in ['NAN', 'NONE', '']:
                    return None
                # Si tiene 22 chars, los primeros 20 son el CUP canónico
                if len(s) == 22:
                    return s[:20]
                return s

            def extraer_meta_liquidacion(df_raw):
                """Extrae metadatos del encabezado de la liquidación."""
                meta = {'mes': '', 'anio': '', 'factura': '', 'nombre': '', 'empresa': ''}
                for i in range(0, 12):
                    row = df_raw.iloc[i]
                    vals = row.tolist()
                    for j, v in enumerate(vals):
                        sv = str(v).strip()
                        if sv == 'Mes:' and j + 2 < len(vals):
                            try:
                                meta['mes'] = str(int(float(str(vals[j+2]))))
                            except Exception:
                                pass
                        if sv == 'Año:' and j + 2 < len(vals):
                            try:
                                meta['anio'] = str(int(float(str(vals[j+2]))))
                            except Exception:
                                pass
                        if sv == 'Nº Factura:' and j + 3 < len(vals):
                            nf = str(vals[j+3]).strip()
                            if nf not in ['nan', 'NaT', '']:
                                meta['factura'] = nf
                        if sv == 'Nombre:' and j + 6 < len(vals):
                            nb = str(vals[j+6]).strip()
                            if nb not in ['nan', 'NaT', '']:
                                meta['nombre'] = nb
                        if sv == 'Empresa:' and j + 6 < len(vals):
                            em = str(vals[j+6]).strip()
                            if em not in ['nan', 'NaT', '']:
                                meta['empresa'] = em
                return meta

            def leer_excel_safe(f, header=0, sheet_name=0):
                """
                Lee un xlsx usando solo librerias estandar (zipfile + xml.etree).
                No necesita openpyxl, xlrd ni ningun paquete externo.
                """
                import zipfile, io, re
                from xml.etree import ElementTree as ET

                raw = f.read() if hasattr(f, 'read') else f
                buf = io.BytesIO(raw)
                zf = zipfile.ZipFile(buf)

                # Shared strings
                shared_strings = []
                if 'xl/sharedStrings.xml' in zf.namelist():
                    tree = ET.parse(zf.open('xl/sharedStrings.xml'))
                    ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                    for si in tree.findall('.//s:si', ns):
                        parts = si.findall('.//s:t', ns)
                        shared_strings.append(''.join(p.text or '' for p in parts))

                # Encontrar hoja
                wb_tree = ET.parse(zf.open('xl/workbook.xml'))
                wb_ns = {'w': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                sheets = wb_tree.findall('.//w:sheet', wb_ns)
                sheet_el = sheets[sheet_name] if isinstance(sheet_name, int) else next(
                    (s for s in sheets if s.get('name') == sheet_name), sheets[0])

                rels_tree = ET.parse(zf.open('xl/_rels/workbook.xml.rels'))
                rels_ns = {'r': 'http://schemas.openxmlformats.org/package/2006/relationships'}
                ns_rid = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
                r_id = sheet_el.get(f'{{{ns_rid}}}id') or sheet_el.get('r:id')
                sheet_file = 'xl/worksheets/sheet1.xml'
                for rel in rels_tree.findall('r:Relationship', rels_ns):
                    if rel.get('Id') == r_id:
                        t = rel.get('Target', '').lstrip('/')
                        sheet_file = t if t.startswith('xl/') else 'xl/' + t
                        break

                # Parsear celdas
                ws_tree = ET.parse(zf.open(sheet_file))
                ws_ns = {'w': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

                def col2idx(s):
                    v = 0
                    for ch in s:
                        v = v * 26 + (ord(ch) - 64)
                    return v - 1

                rows_data, max_col = {}, 0
                for row_el in ws_tree.findall('.//w:row', ws_ns):
                    r_num = int(row_el.get('r', 0))
                    for c_el in row_el.findall('w:c', ws_ns):
                        ref = c_el.get('r', '')
                        m = re.match(r'([A-Z]+)', ref)
                        if not m:
                            continue
                        col_idx = col2idx(m.group(1))
                        max_col = max(max_col, col_idx)
                        t_attr = c_el.get('t', '')
                        v_el = c_el.find('w:v', ws_ns)
                        val = None
                        # Inline strings usan <is><t> en vez de <v>
                        is_el = c_el.find('w:is', ws_ns)
                        if is_el is not None:
                            t_parts = is_el.findall('.//w:t', ws_ns)
                            val = ''.join(p.text or '' for p in t_parts)
                        elif v_el is not None and v_el.text is not None:
                            if t_attr == 's':
                                i_s = int(v_el.text)
                                val = shared_strings[i_s] if i_s < len(shared_strings) else ''
                            elif t_attr in ('str', 'b', 'e'):
                                val = v_el.text
                            else:
                                try:
                                    fv = float(v_el.text)
                                    val = int(fv) if fv == int(fv) else fv
                                except (ValueError, OverflowError):
                                    val = v_el.text
                        rows_data.setdefault(r_num, {})[col_idx] = val

                if not rows_data:
                    return pd.DataFrame()

                n_cols = max_col + 1
                records = [[rows_data[r].get(c) for c in range(n_cols)]
                           for r in sorted(rows_data.keys())]
                df = pd.DataFrame(records)

                if header is None:
                    return df

                if isinstance(header, int) and header < len(df):
                    col_names = [str(v) if v is not None else f'col_{i}'
                                 for i, v in enumerate(df.iloc[header].tolist())]
                    df.columns = col_names
                    df = df.iloc[header + 1:].reset_index(drop=True)
                return df


            def leer_liquidacion(uploaded_file):
                """Lee y limpia una liquidación de compañía (formato Naturgy y similares)."""
                df_raw = leer_excel_safe(uploaded_file, header=None)
                meta = extraer_meta_liquidacion(df_raw)

                # Detectar fila de cabecera buscando 'CIF/NIF' o 'CUPSElectricidad'
                header_row = None
                for i in range(0, 20):
                    vals = [str(v) for v in df_raw.iloc[i].tolist()]
                    if any('CIF' in v or 'CUPS' in v.upper() or 'CONTRATO' in v.upper() for v in vals):
                        header_row = i
                        break

                if header_row is None:
                    return None, meta, "No se encontró la cabecera de datos en el archivo."

                # Mapear columnas por nombre desde la fila header
                header_vals = [str(v).strip() for v in df_raw.iloc[header_row].tolist()]
                def col_idx(names):
                    """Devuelve el índice de la primera columna que contenga alguno de los nombres."""
                    for name in names:
                        for j, h in enumerate(header_vals):
                            if name.upper() in h.upper():
                                return j
                    return None

                idx_cif       = col_idx(['CIF/NIF', 'CIF', 'NIF'])
                idx_gas       = col_idx(['CUPSGas', 'CUPS Gas', 'Gas'])
                idx_luz       = col_idx(['CUPSElectricidad', 'CUPS Luz', 'Electri'])
                idx_producto  = col_idx(['Producto', 'Grupo Tarifa'])
                idx_fbaja     = col_idx(['Fecha Baja', 'FechaBaja', 'Baja'])
                idx_falta     = col_idx(['Fecha', 'Alta'])
                idx_comision  = col_idx(['Comision', 'Comisión'])
                idx_contrato  = col_idx(['Contrato Darwin', 'Darwin', 'Contrato'])

                # Fallback a posiciones fijas si no se detectan por nombre
                if idx_cif      is None: idx_cif      = 5
                if idx_gas      is None: idx_gas      = 15
                if idx_luz      is None: idx_luz      = 18
                if idx_producto is None: idx_producto = 19
                if idx_fbaja    is None: idx_fbaja    = 14
                if idx_falta    is None: idx_falta    = 11
                if idx_comision is None: idx_comision = 27
                if idx_contrato is None: idx_contrato = 26

                n_cols = len(df_raw.columns)

                def safe_iloc(row, idx):
                    """Acceso seguro a columna por índice."""
                    if idx is None or idx >= n_cols: return None
                    v = row.iloc[idx]
                    return None if (v is None or str(v).strip() in ['nan','None','']) else v

                rows = []
                for i in range(header_row + 1, len(df_raw)):
                    row = df_raw.iloc[i]
                    cif = safe_iloc(row, idx_cif)
                    if cif is None or str(cif).strip() in ['nan', '', 'CIF/NIF']:
                        continue
                    cups_gas_raw  = safe_iloc(row, idx_gas)
                    cups_luz_raw  = safe_iloc(row, idx_luz)
                    producto      = str(safe_iloc(row, idx_producto) or '').strip()
                    fecha_baja    = safe_iloc(row, idx_fbaja)
                    comision      = safe_iloc(row, idx_comision)
                    contrato_darwin = safe_iloc(row, idx_contrato)

                    rows.append({
                        'CIF': str(cif).strip(),
                        'Fecha Alta': safe_iloc(row, idx_falta),
                        'Fecha Baja': fecha_baja,
                        'CUPS Gas Raw': str(cups_gas_raw).strip() if cups_gas_raw is not None else None,
                        'CUPS Luz Raw': str(cups_luz_raw).strip() if cups_luz_raw is not None else None,
                        'CUPS Gas Norm': normalize_cup(cups_gas_raw),
                        'CUPS Luz Norm': normalize_cup(cups_luz_raw),
                        'Producto': producto,
                        'Tipo': 'GAS' if cups_gas_raw is not None and str(cups_gas_raw).strip() not in ['nan', ''] else 'LUZ',
                        'Contrato Darwin': str(contrato_darwin).strip() if contrato_darwin is not None else '',
                        'Comisión_liq': comision if comision is not None else 0,
                        'Descomisionado': fecha_baja is not None,
                    })
                df = pd.DataFrame(rows)
                return df, meta, None

            def cruzar_con_contratos(df_liq, df_contratos):
                """Cruza la liquidación con el Excel de contratos por CUP normalizado."""
                # Normalizar CUPs en contratos
                df_contratos = df_contratos.copy()
                df_contratos['CUPS Luz Norm'] = df_contratos['CUPS Luz'].apply(normalize_cup)
                df_contratos['CUPS Gas Norm'] = df_contratos['CUPS Gas'].apply(normalize_cup)

                # Separar registros de luz y gas en la liquidación
                df_luz = df_liq[df_liq['CUPS Luz Norm'].notna()].copy()
                df_gas = df_liq[df_liq['CUPS Gas Norm'].notna()].copy()

                cols_crm = ['ID', 'ID Contrato Externo', 'Cliente', 'Comercial', 'Estado',
                            'Comercializadora', 'Tarifa', 'DNI Cliente', 'CUPS Luz Norm', 'Comisión']

                # Merge LUZ
                if not df_luz.empty:
                    crm_luz = df_contratos[df_contratos['CUPS Luz Norm'].notna()][
                        [c for c in cols_crm if c != 'CUPS Gas Norm']
                    ].drop_duplicates('CUPS Luz Norm')
                    df_luz = pd.merge(df_luz, crm_luz, on='CUPS Luz Norm', how='left', suffixes=('_liq', '_crm'))
                    df_luz['CUP Cruce'] = df_luz['CUPS Luz Norm']
                else:
                    df_luz['ID'] = None

                # Merge GAS
                cols_crm_gas = ['ID', 'ID Contrato Externo', 'Cliente', 'Comercial', 'Estado',
                                'Comercializadora', 'Tarifa', 'DNI Cliente', 'CUPS Gas Norm', 'Comisión']
                if not df_gas.empty:
                    crm_gas = df_contratos[df_contratos['CUPS Gas Norm'].notna()][
                        [c for c in cols_crm_gas]
                    ].drop_duplicates('CUPS Gas Norm')
                    df_gas = pd.merge(df_gas, crm_gas, on='CUPS Gas Norm', how='left', suffixes=('_liq', '_crm'))
                    df_gas['CUP Cruce'] = df_gas['CUPS Gas Norm']
                else:
                    df_gas['ID'] = None

                # Unir
                df_resultado = pd.concat([df_luz, df_gas], ignore_index=True)

                # Clasificar cada registro
                def clasificar(row):
                    try:
                        com_liq = float(row.get('Comisión_liq', 0) or 0)
                    except (TypeError, ValueError):
                        com_liq = 0
                    # Descomisionado: tiene fecha de baja O comisión negativa
                    if row.get('Descomisionado') or com_liq < 0:
                        return '🔴 DESCOMISIONADO'
                    # Sin match: no está en CRM (ID nulo o vacío)
                    id_val = row.get('ID')
                    sin_match = (id_val is None or
                                 (hasattr(id_val, '__class__') and
                                  id_val.__class__.__name__ == 'float' and
                                  id_val != id_val) or  # NaN check
                                 str(id_val).strip() in ['', 'nan', 'None'])
                    if sin_match:
                        return '⚠️ SIN MATCH EN CRM'
                    # Tiene match en CRM y comisión > 0: PAGADO
                    if com_liq > 0:
                        return '✅ PAGADO'
                    # Tiene match pero comisión 0: pendiente de revisar
                    return '❓ PENDIENTE REVISAR'

                df_resultado['Estado Liquidación'] = df_resultado.apply(clasificar, axis=1)
                return df_resultado

            # ══════════════════════════════════════════════════════
            # ── INTERFAZ ──
            # ══════════════════════════════════════════════════════

            st.markdown("""
                <div style="background:#ffffff; border-left:4px solid #FFD700; padding:15px; border-radius:8px; margin-bottom:20px;">
                    <p style="color:#FFD700; font-weight:bold; margin:0 0 6px 0;">⚙️ CRUCE AUTOMÁTICO DE LIQUIDACIONES</p>
                    <p style="color:#8b949e; margin:0; font-size:0.85rem;">
                        Sube la liquidación de la compañía (ej: <b>liqui_naturgy_abril.xlsx</b>) y el Excel de contratos.
                        El sistema cruza por CUP (20 ó 22 dígitos), detecta lo pagado, lo descomisionado (gas y luz)
                        y lo pendiente de reclamar.
                    </p>
                </div>
            """, unsafe_allow_html=True)

            liq_tab_nat, liq_tab_gana, liq_tab_total = st.tabs([
                "🔥 NATURGY", "⚡ GANA ENERGÍA", "🌍 TOTAL ENERGIES"
            ])

            with liq_tab_nat:
                    col_up1, col_up2 = st.columns(2)
                    with col_up1:
                        st.markdown('<p style="color:#d2ff00; font-weight:bold; font-size:1rem; margin-bottom:4px;">📄 Liquidación compañía</p>', unsafe_allow_html=True)
                        f_liquidacion = st.file_uploader(
                            "Sube la liquidación (.xlsx)",
                            type=['xlsx'],
                            key="liq_upload",
                            label_visibility="collapsed"
                        )
                    with col_up2:
                        st.markdown('<p style="color:#d2ff00; font-weight:bold; font-size:1rem; margin-bottom:4px;">📋 Contratos Energía (CRM)</p>', unsafe_allow_html=True)
                        f_contratos = st.file_uploader(
                            "Sube contratos_energia.xlsx",
                            type=['xlsx'],
                            key="con_upload",
                            label_visibility="collapsed"
                        )

                    if f_liquidacion and f_contratos:
                        with st.spinner("⏳ Procesando cruce de liquidación..."):
                            try:
                                # Leer archivos
                                df_liq_raw, meta, err = leer_liquidacion(f_liquidacion)
                                if err:
                                    st.error(f"❌ Error leyendo liquidación: {err}")
                                    st.stop()

                                df_con_raw = leer_excel_safe(f_contratos)
                                df_con_raw.columns = df_con_raw.columns.str.strip()

                                # Detectar nombre compañía del archivo
                                nombre_archivo = f_liquidacion.name.lower()
                                companias_conocidas = ['naturgy', 'endesa', 'gana', 'iberdrola', 'total', 'repsol']
                                compania_detectada = next((c.upper() for c in companias_conocidas if c in nombre_archivo), 'COMPAÑÍA')

                                # Filtrar contratos solo de esa compañía si aplica
                                if 'Comercializadora' in df_con_raw.columns and compania_detectada != 'COMPAÑÍA':
                                    df_con_filtrado = df_con_raw[
                                        df_con_raw['Comercializadora'].str.contains(compania_detectada, case=False, na=False)
                                    ].copy()
                                    n_total = len(df_con_raw)
                                    n_filtrado = len(df_con_filtrado)
                                else:
                                    df_con_filtrado = df_con_raw.copy()
                                    n_total = n_filtrado = len(df_con_raw)

                                # Cruce
                                df_resultado = cruzar_con_contratos(df_liq_raw, df_con_filtrado)


                                # ── SVA: extraer de la misma liquidación (filas con producto SVA) ──
                                # Productos de energía pura vs SVA
                                PRODUCTOS_ENERGIA = {'TARIFA POR USO LUZ', 'PLAN FIJO LUZ 24H', 'PLAN FIJO LUZ',
                                                     'TARIFA POR USO GAS', 'TARIFA PLANA GAS', 'PLAN FIJO GAS'}
                                def es_sva(producto):
                                    return (producto is not None and
                                            str(producto).strip() != '' and
                                            str(producto).strip().upper() not in PRODUCTOS_ENERGIA)

                                df_sva_resultado = pd.DataFrame()
                                sva_pagados_n, sva_descom_n, sva_sinmatch_n = 0, 0, 0
                                sva_total_pagado, sva_total_descom = 0.0, 0.0


                                # ── HEADER RESUMEN ──
                                meses_es = {'1':'Enero','2':'Febrero','3':'Marzo','4':'Abril','5':'Mayo','6':'Junio',
                                            '7':'Julio','8':'Agosto','9':'Septiembre','10':'Octubre','11':'Noviembre','12':'Diciembre'}
                                mes_nombre = meses_es.get(meta.get('mes',''), meta.get('mes',''))
                                st.markdown(f"""
                                    <div style="background:linear-gradient(135deg,#f0f4ff,#e8eeff); border:2px solid #FFD700;
                                                border-radius:12px; padding:18px 24px; margin:10px 0 20px 0;">
                                        <h3 style="color:#FFD700; margin:0 0 4px 0;">⚡ {compania_detectada} · {mes_nombre} {meta.get('anio','')}</h3>
                                        <p style="color:#8b949e; margin:0; font-size:0.82rem;">
                                            Factura: <b style="color:#111111;">{meta.get('factura','-')}</b> &nbsp;·&nbsp;
                                            Empresa: <b style="color:#111111;">{meta.get('nombre','-')}</b> &nbsp;·&nbsp;
                                            Registros liquidación: <b style="color:#111111;">{len(df_liq_raw)}</b> &nbsp;·&nbsp;
                                            Contratos {compania_detectada} en CRM: <b style="color:#111111;">{n_filtrado}</b>
                                        </p>
                                    </div>
                                """, unsafe_allow_html=True)

                                # ── KPIs ──
                                pagados = df_resultado[df_resultado['Estado Liquidación'] == '✅ PAGADO']
                                descomisionados = df_resultado[df_resultado['Estado Liquidación'] == '🔴 DESCOMISIONADO']
                                sin_match = df_resultado[df_resultado['Estado Liquidación'] == '⚠️ SIN MATCH EN CRM']
                                pendientes = df_resultado[df_resultado['Estado Liquidación'] == '❓ PENDIENTE REVISAR']

                                pagados_luz = pagados[pagados['Tipo'] == 'LUZ']
                                pagados_gas = pagados[pagados['Tipo'] == 'GAS']
                                descom_luz = descomisionados[descomisionados['Tipo'] == 'LUZ']
                                descom_gas = descomisionados[descomisionados['Tipo'] == 'GAS']

                                total_cobrado = float(pagados['Comisión_liq'].sum()) if 'Comisión_liq' in pagados.columns else 0
                                total_descom = abs(float(descomisionados['Comisión_liq'].sum())) if 'Comisión_liq' in descomisionados.columns else 0
                                total_a_reclamar = float(sin_match['Comisión_liq'].sum()) + float(pendientes['Comisión_liq'].sum()) if 'Comisión_liq' in df_resultado.columns else 0

                                k1, k2, k3, k4, k5 = st.columns(5)
                                box_k = "border-radius:10px; padding:14px 8px; text-align:center; margin-bottom:10px;"
                                k1.markdown(f'<div style="background:#f0fff4; border:2px solid #7ee787; {box_k}"><p style="color:#7ee787; font-size:0.72rem; font-weight:bold; margin:0;">✅ PAGADOS</p><h2 style="color:#111111; margin:4px 0;">{len(pagados)}</h2><p style="color:#7ee787; font-size:0.75rem; margin:0;">💡{len(pagados_luz)} 🔥{len(pagados_gas)}</p><p style="color:#7ee787; font-size:0.8rem; margin:4px 0 0 0;font-weight:bold;">{total_cobrado:,.0f}€</p></div>', unsafe_allow_html=True)
                                k2.markdown(f'<div style="background:#fff0f0; border:2px solid #ff4b4b; {box_k}"><p style="color:#ff4b4b; font-size:0.72rem; font-weight:bold; margin:0;">🔴 DESCOMISIONADOS</p><h2 style="color:#111111; margin:4px 0;">{len(descomisionados)}</h2><p style="color:#ff4b4b; font-size:0.75rem; margin:0;">💡{len(descom_luz)} 🔥{len(descom_gas)}</p><p style="color:#ff4b4b; font-size:0.8rem; margin:4px 0 0 0;font-weight:bold;">-{total_descom:,.0f}€</p></div>', unsafe_allow_html=True)
                                k3.markdown(f'<div style="background:#fffbf0; border:2px solid #ffaa00; {box_k}"><p style="color:#ffaa00; font-size:0.72rem; font-weight:bold; margin:0;">⚠️ SIN MATCH CRM</p><h2 style="color:#111111; margin:4px 0;">{len(sin_match)}</h2><p style="color:#ffaa00; font-size:0.75rem; margin:0;">Verificar manualmente</p></div>', unsafe_allow_html=True)
                                k4.markdown(f'<div style="background:#ffffff; border:2px solid #8b949e; {box_k}"><p style="color:#8b949e; font-size:0.72rem; font-weight:bold; margin:0;">❓ PENDIENTE REVISAR</p><h2 style="color:#111111; margin:4px 0;">{len(pendientes)}</h2><p style="color:#8b949e; font-size:0.75rem; margin:0;"> </p></div>', unsafe_allow_html=True)
                                k5.markdown(f'<div style="background:#f0fff4; border:2px solid #22c55e; {box_k}"><p style="color:#166534; font-size:0.72rem; font-weight:bold; margin:0;">💰 A RECLAMAR</p><h2 style="color:#111111; margin:4px 0;">{len(sin_match)+len(pendientes)}</h2><p style="color:#d2ff00; font-size:0.8rem; margin:0;font-weight:bold;">{total_a_reclamar:,.0f}€</p></div>', unsafe_allow_html=True)

                                st.markdown("<br>", unsafe_allow_html=True)

                                # ── SVA: extraer filas SVA del df_resultado (ya cruzadas con CRM) ──
                                df_sva_resultado = df_resultado[df_resultado['Producto'].apply(es_sva)].copy()
                                df_energia_resultado = df_resultado[~df_resultado['Producto'].apply(es_sva)].copy()

                                # Recalcular subsets usando solo energía (sin SVA)
                                pagados       = df_energia_resultado[df_energia_resultado['Estado Liquidación']=='✅ PAGADO']
                                descomisionados = df_energia_resultado[df_energia_resultado['Estado Liquidación']=='🔴 DESCOMISIONADO']
                                sin_match     = df_energia_resultado[df_energia_resultado['Estado Liquidación']=='⚠️ SIN MATCH EN CRM']
                                pendientes    = df_energia_resultado[df_energia_resultado['Estado Liquidación']=='❓ PENDIENTE REVISAR']

                                pagados_luz   = pagados[pagados['Tipo'] == 'LUZ']
                                pagados_gas   = pagados[pagados['Tipo'] == 'GAS']
                                descom_luz    = descomisionados[descomisionados['Tipo'] == 'LUZ']
                                descom_gas    = descomisionados[descomisionados['Tipo'] == 'GAS']

                                total_cobrado     = float(pagados['Comisión_liq'].sum()) if 'Comisión_liq' in pagados.columns else 0
                                total_descom      = abs(float(descomisionados['Comisión_liq'].sum())) if 'Comisión_liq' in descomisionados.columns else 0
                                total_a_reclamar  = float(sin_match['Comisión_liq'].sum()) + float(pendientes['Comisión_liq'].sum()) if 'Comisión_liq' in df_resultado.columns else 0

                                # SVA stats
                                sva_pagados_n     = len(df_sva_resultado[df_sva_resultado['Estado Liquidación']=='✅ PAGADO'])
                                sva_descom_n      = len(df_sva_resultado[df_sva_resultado['Estado Liquidación']=='🔴 DESCOMISIONADO'])
                                sva_sinmatch_n    = len(df_sva_resultado[df_sva_resultado['Estado Liquidación']=='⚠️ SIN MATCH EN CRM'])
                                sva_total_pagado  = float(df_sva_resultado[df_sva_resultado['Estado Liquidación']=='✅ PAGADO']['Comisión_liq'].sum()) if not df_sva_resultado.empty else 0.0
                                sva_total_descom  = float(df_sva_resultado[df_sva_resultado['Estado Liquidación']=='🔴 DESCOMISIONADO']['Comisión_liq'].sum()) if not df_sva_resultado.empty else 0.0

                                st.markdown("<br>", unsafe_allow_html=True)

                                # ── KPI SVA (si hay SVA en la liquidación) ──
                                if not df_sva_resultado.empty:
                                    st.markdown('<p style="color:#a78bfa; font-weight:bold; font-size:0.85rem; margin:0 0 6px 0;">⚡ SVA</p>', unsafe_allow_html=True)
                                    ks1, ks2, ks3, ks4 = st.columns(4)
                                    box_ks = "border-radius:8px; padding:10px 8px; text-align:center; margin-bottom:12px;"
                                    ks1.markdown(f'<div style="background:#f0f4ff; border:2px solid #a78bfa; {box_ks}"><p style="color:#a78bfa; font-size:0.7rem; font-weight:bold; margin:0;">⚡ SVA PAGADOS</p><h3 style="color:#111111; margin:4px 0;">{sva_pagados_n}</h3><p style="color:#a78bfa; font-size:0.8rem; margin:0;font-weight:bold;">{sva_total_pagado:,.0f}€</p></div>', unsafe_allow_html=True)
                                    ks2.markdown(f'<div style="background:#fff0f0; border:2px solid #ff4b4b; {box_ks}"><p style="color:#ff4b4b; font-size:0.7rem; font-weight:bold; margin:0;">🔴 SVA DESCOM</p><h3 style="color:#111111; margin:4px 0;">{sva_descom_n}</h3><p style="color:#ff4b4b; font-size:0.8rem; margin:0;font-weight:bold;">{sva_total_descom:,.0f}€</p></div>', unsafe_allow_html=True)
                                    ks3.markdown(f'<div style="background:#fffbf0; border:2px solid #ffaa00; {box_ks}"><p style="color:#ffaa00; font-size:0.7rem; font-weight:bold; margin:0;">⚠️ SVA SIN MATCH</p><h3 style="color:#111111; margin:4px 0;">{sva_sinmatch_n}</h3></div>', unsafe_allow_html=True)
                                    ks4.markdown(f'<div style="background:#f0f4ff; border:2px solid #d2ff00; {box_ks}"><p style="color:#1d4ed8; font-size:0.7rem; font-weight:bold; margin:0;">📋 SVA TOTAL</p><h3 style="color:#111111; margin:4px 0;">{len(df_sva_resultado)}</h3></div>', unsafe_allow_html=True)
                                    st.markdown("<br>", unsafe_allow_html=True)

                                # ── TABS DE DETALLE ──
                                _tab_labels = [
                                    f"✅ PAGADOS ({len(pagados)})",
                                    f"🔴 DESCOMISIONADOS ({len(descomisionados)})",
                                    f"💰 A RECLAMAR ({len(sin_match)+len(pendientes)})",
                                    f"⚠️ SIN MATCH ({len(sin_match)})",
                                    f"📋 COMPLETO ({len(df_energia_resultado)})",
                                ]
                                if not df_sva_resultado.empty:
                                    _tab_labels.append(f"⚡ SVA ({len(df_sva_resultado)})")

                                _tabs = st.tabs(_tab_labels)
                                t_pagado   = _tabs[0]
                                t_descom   = _tabs[1]
                                t_reclamar = _tabs[2]
                                t_sinmatch = _tabs[3]
                                t_todo     = _tabs[4]
                                t_sva      = _tabs[5] if not df_sva_resultado.empty else None


                                # Columnas a mostrar
                                cols_display = ['Tipo', 'CIF', 'Cliente', 'Comercial', 'Estado', 'CUP Cruce',
                                                'Producto', 'Comisión_liq', 'Fecha Alta', 'Fecha Baja']
                                cols_display = [c for c in cols_display if c in df_energia_resultado.columns]

                                def df_to_show(df_sub):
                                    """Prepara dataframe para mostrar."""
                                    df_s = df_sub[cols_display].copy()
                                    if 'Fecha Alta' in df_s.columns:
                                        df_s['Fecha Alta'] = pd.to_datetime(df_s['Fecha Alta'], errors='coerce').dt.strftime('%d/%m/%Y').fillna('-')
                                    if 'Fecha Baja' in df_s.columns:
                                        df_s['Fecha Baja'] = pd.to_datetime(df_s['Fecha Baja'], errors='coerce').dt.strftime('%d/%m/%Y').fillna('-')
                                    if 'Comisión_liq' in df_s.columns:
                                        df_s = df_s.rename(columns={'Comisión_liq': 'Comisión €'})
                                    return df_s.reset_index(drop=True)

                                with t_pagado:
                                    st.markdown(f'<p style="color:#7ee787;">Total cobrado: <b>{total_cobrado:,.0f} €</b> — Luz: {len(pagados_luz)} suministros | Gas: {len(pagados_gas)} suministros</p>', unsafe_allow_html=True)
                                    if not pagados.empty:
                                        st.dataframe(df_to_show(pagados), use_container_width=True, height=400)
                                    else:
                                        st.info("No hay registros pagados.")

                                with t_descom:
                                    st.markdown(f'<p style="color:#ff4b4b;">Total descomisionado: <b>-{total_descom:,.0f} €</b> — Luz: {len(descom_luz)} | Gas: {len(descom_gas)}</p>', unsafe_allow_html=True)
                                    if not descomisionados.empty:
                                        st.dataframe(df_to_show(descomisionados), use_container_width=True, height=400)
                                    else:
                                        st.success("✅ Sin descomisiones en esta liquidación.")

                                with t_reclamar:
                                    df_reclamar = pd.concat([sin_match, pendientes], ignore_index=True)
                                    st.markdown(f'<p style="color:#d2ff00;">Importe total a reclamar: <b>{total_a_reclamar:,.0f} €</b></p>', unsafe_allow_html=True)
                                    if not df_reclamar.empty:
                                        st.dataframe(df_to_show(df_reclamar), use_container_width=True, height=400)
                                    else:
                                        st.success("✅ Todo está abonado o identificado.")

                                with t_sinmatch:
                                    st.markdown('<p style="color:#ffaa00;">Estos CUPs de la liquidación no se encuentran en el Excel de contratos. Verificar si pertenecen a otra compañía o si faltan en el CRM.</p>', unsafe_allow_html=True)
                                    if not sin_match.empty:
                                        cols_sm = ['Tipo', 'CIF', 'CUP Cruce', 'Producto', 'Comisión_liq']
                                        cols_sm = [c for c in cols_sm if c in sin_match.columns]
                                        st.dataframe(sin_match[cols_sm].reset_index(drop=True), use_container_width=True)
                                    else:
                                        st.success("✅ Todos los CUPs están en el CRM.")

                                with t_todo:
                                    cols_todo = cols_display + ['Estado Liquidación']
                                    cols_todo = [c for c in cols_todo if c in df_resultado.columns]
                                    df_todo_show = df_energia_resultado[cols_todo].copy()
                                    if 'Fecha Alta' in df_todo_show.columns:
                                        df_todo_show['Fecha Alta'] = pd.to_datetime(df_todo_show['Fecha Alta'], errors='coerce').dt.strftime('%d/%m/%Y').fillna('-')
                                    if 'Fecha Baja' in df_todo_show.columns:
                                        df_todo_show['Fecha Baja'] = pd.to_datetime(df_todo_show['Fecha Baja'], errors='coerce').dt.strftime('%d/%m/%Y').fillna('-')
                                    if 'Comisión_liq' in df_todo_show.columns:
                                        df_todo_show = df_todo_show.rename(columns={'Comisión_liq': 'Comisión €'})
                                    st.dataframe(df_todo_show.reset_index(drop=True), use_container_width=True, height=500)


                                if t_sva is not None and not df_sva_resultado.empty:
                                    with t_sva:
                                        st.markdown('<p style="color:#a78bfa;">SVA extraídos de la misma liquidación (filas con producto distinto a energía), cruzados con contratos por su CUPS.</p>', unsafe_allow_html=True)

                                        cols_sva_show = ['CIF', 'Cliente', 'Comercial', 'Estado', 'CUP Cruce',
                                                         'Producto', 'Comisión_liq', 'Estado Liquidación']
                                        cols_sva_show = [c for c in cols_sva_show if c in df_sva_resultado.columns]

                                        # ── Pagados SVA ──
                                        sva_p = df_sva_resultado[df_sva_resultado['Estado Liquidación']=='✅ PAGADO']
                                        sva_d = df_sva_resultado[df_sva_resultado['Estado Liquidación']=='🔴 DESCOMISIONADO']
                                        sva_r = df_sva_resultado[~df_sva_resultado['Estado Liquidación'].isin(['✅ PAGADO','🔴 DESCOMISIONADO'])]

                                        st.markdown(f'**✅ SVA PAGADOS** — {len(sva_p)} registros · {sva_p["Comisión_liq"].sum():,.0f}€')
                                        if not sva_p.empty:
                                            df_sp = sva_p[cols_sva_show].copy()
                                            df_sp = df_sp.rename(columns={'Comisión_liq': 'IMPORTE SVA €'})
                                            st.dataframe(df_sp.reset_index(drop=True), use_container_width=True, height=250)

                                        if not sva_d.empty:
                                            st.markdown(f'**🔴 SVA DESCOMISIONADOS** — {len(sva_d)} registros · {sva_d["Comisión_liq"].sum():,.0f}€')
                                            df_sd = sva_d[cols_sva_show].copy()
                                            df_sd = df_sd.rename(columns={'Comisión_liq': 'IMPORTE SVA €'})
                                            st.dataframe(df_sd.reset_index(drop=True), use_container_width=True, height=200)

                                        if not sva_r.empty:
                                            st.markdown(f'**⚠️ SVA A RECLAMAR / SIN MATCH** — {len(sva_r)} registros · {sva_r["Comisión_liq"].sum():,.0f}€')
                                            df_sr = sva_r[cols_sva_show].copy()
                                            df_sr = df_sr.rename(columns={'Comisión_liq': 'IMPORTE SVA €'})
                                            st.dataframe(df_sr.reset_index(drop=True), use_container_width=True, height=200)
                                        else:
                                            st.success("✅ Todos los SVA están abonados.")


                                # ── DESCARGA RESULTADO ──
                                st.markdown("---")
                                import io, importlib, zipfile as _zf, struct as _struct

                                def prep_df_export(df_in):
                                    """Convierte datetime/Timestamp a string para exportar."""
                                    df_out = df_in.copy()
                                    for col in df_out.columns:
                                        try:
                                            df_out[col] = df_out[col].apply(
                                                lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else x
                                            )
                                        except Exception:
                                            pass
                                    return df_out

                                def hacer_xlsx_nativo(sheets_dict):
                                    """
                                    Genera un xlsx real (formato Office Open XML) usando solo stdlib.
                                    sheets_dict = {'NombreHoja': dataframe, ...}
                                    Soporta strings, números y celdas vacías. Sin estilos avanzados.
                                    """
                                    import zipfile as zf2, io as io2
                                    from xml.etree.ElementTree import Element, SubElement, tostring

                                    def esc(s):
                                        return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;').replace("'",'&apos;')

                                    shared = []
                                    shared_map = {}
                                    def get_si(val):
                                        s = str(val)
                                        if s not in shared_map:
                                            shared_map[s] = len(shared)
                                            shared.append(s)
                                        return shared_map[s]

                                    # Pre-scan all data to build shared strings
                                    sheet_data = {}
                                    for sname, df in sheets_dict.items():
                                        df2p = prep_df_export(df).reset_index(drop=True)
                                        rows = [list(df2p.columns)]
                                        for _, row in df2p.iterrows():
                                            rows.append(list(row))
                                        for row in rows:
                                            for cell in row:
                                                if cell is not None and str(cell) not in ['', 'nan', 'None']:
                                                    try:
                                                        float(str(cell).replace(',','.'))
                                                    except (ValueError, TypeError):
                                                        get_si(cell)
                                        sheet_data[sname] = rows

                                    buf = io2.BytesIO()
                                    with zf2.ZipFile(buf, 'w', zf2.ZIP_DEFLATED) as z:
                                        # [Content_Types].xml
                                        ct_parts = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
              <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
              <Default Extension="xml" ContentType="application/xml"/>
              <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
              <Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>
              <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
            '''
                                        for i in range(len(sheet_data)):
                                            ct_parts += f'  <Override PartName="/xl/worksheets/sheet{i+1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>\n'
                                        ct_parts += '</Types>'
                                        z.writestr('[Content_Types].xml', ct_parts)

                                        # _rels/.rels
                                        z.writestr('_rels/.rels', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
              <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
            </Relationships>''')

                                        # xl/_rels/workbook.xml.rels
                                        wb_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
              <Relationship Id="rId_ss" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/>
              <Relationship Id="rId_st" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
            '''
                                        for i, sname in enumerate(sheet_data):
                                            wb_rels += f'  <Relationship Id="rId{i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i+1}.xml"/>\n'
                                        wb_rels += '</Relationships>'
                                        z.writestr('xl/_rels/workbook.xml.rels', wb_rels)

                                        # xl/workbook.xml
                                        wb_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
                      xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
              <sheets>
            '''
                                        for i, sname in enumerate(sheet_data):
                                            wb_xml += f'    <sheet name="{esc(sname)}" sheetId="{i+1}" r:id="rId{i+1}"/>\n'
                                        wb_xml += '  </sheets>\n</workbook>'
                                        z.writestr('xl/workbook.xml', wb_xml)

                                        # xl/styles.xml (mínimo)
                                        z.writestr('xl/styles.xml', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
              <fonts><font><sz val="11"/><name val="Calibri"/></font></fonts>
              <fills><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>
              <borders><border><left/><right/><top/><bottom/><diagonal/></border></borders>
              <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
              <cellXfs><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>
            </styleSheet>''')

                                        # xl/sharedStrings.xml
                                        ss_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="''' + str(len(shared)) + '''" uniqueCount="''' + str(len(shared)) + '''">
            '''
                                        for s in shared:
                                            ss_xml += f'  <si><t xml:space="preserve">{esc(s)}</t></si>\n'
                                        ss_xml += '</sst>'
                                        z.writestr('xl/sharedStrings.xml', ss_xml)

                                        # xl/worksheets/sheetN.xml
                                        col_letters = ['A','B','C','D','E','F','G','H','I','J','K','L','M',
                                                       'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
                                                       'AA','AB','AC','AD','AE','AF','AG','AH','AI','AJ','AK','AL',
                                                       'AM','AN','AO','AP','AQ','AR','AS','AT','AU','AV','AW','AX']

                                        for si_idx, (sname, rows) in enumerate(sheet_data.items()):
                                            ws_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
              <sheetData>
            '''
                                            for r_idx, row in enumerate(rows):
                                                ws_xml += f'    <row r="{r_idx+1}">\n'
                                                for c_idx, cell in enumerate(row):
                                                    col = col_letters[c_idx] if c_idx < len(col_letters) else f'A{c_idx}'
                                                    ref = f'{col}{r_idx+1}'
                                                    if cell is None or str(cell) in ['', 'nan', 'None']:
                                                        ws_xml += f'      <c r="{ref}"/>\n'
                                                    else:
                                                        try:
                                                            num = float(str(cell).replace(',','.'))
                                                            ws_xml += f'      <c r="{ref}" t="n"><v>{num}</v></c>\n'
                                                        except (ValueError, TypeError):
                                                            si_n = shared_map.get(str(cell), 0)
                                                            ws_xml += f'      <c r="{ref}" t="s"><v>{si_n}</v></c>\n'
                                                ws_xml += '    </row>\n'
                                            ws_xml += '  </sheetData>\n</worksheet>'
                                            z.writestr(f'xl/worksheets/sheet{si_idx+1}.xml', ws_xml)

                                    buf.seek(0)
                                    return buf.read()

                                # ── Preparar DataFrames para exportar con columnas limpias y totales ──
                                def df_pagados_export(df_p):
                                    """Pagados: columnas clave + importe abonado."""
                                    cols = ['Tipo', 'CIF', 'Cliente', 'Comercial', 'Estado', 'CUP Cruce',
                                            'Producto', 'Fecha Alta', 'Fecha Baja']
                                    cols = [c for c in cols if c in df_p.columns]
                                    df_e = prep_df_export(df_p[cols].copy())
                                    # Añadir importe abonado
                                    if 'Comisión_liq' in df_p.columns:
                                        df_e['IMPORTE ABONADO €'] = df_p['Comisión_liq'].values
                                    # Fila de total
                                    total = df_p['Comisión_liq'].sum() if 'Comisión_liq' in df_p.columns else 0
                                    total_row = {c: '' for c in df_e.columns}
                                    total_row[df_e.columns[-2] if len(df_e.columns) > 1 else df_e.columns[0]] = 'TOTAL'
                                    total_row['IMPORTE ABONADO €'] = round(total, 2)
                                    df_e = pd.concat([df_e, pd.DataFrame([total_row])], ignore_index=True)
                                    return df_e

                                def df_descom_export(df_d):
                                    """Descomisionados: columnas clave + importe descomisión."""
                                    cols = ['Tipo', 'CIF', 'Cliente', 'Comercial', 'Estado', 'CUP Cruce',
                                            'Producto', 'Fecha Alta', 'Fecha Baja']
                                    cols = [c for c in cols if c in df_d.columns]
                                    df_e = prep_df_export(df_d[cols].copy())
                                    if 'Comisión_liq' in df_d.columns:
                                        df_e['IMPORTE DESCOMISIÓN €'] = df_d['Comisión_liq'].values
                                    total = df_d['Comisión_liq'].sum() if 'Comisión_liq' in df_d.columns else 0
                                    total_row = {c: '' for c in df_e.columns}
                                    total_row[df_e.columns[-2] if len(df_e.columns) > 1 else df_e.columns[0]] = 'TOTAL'
                                    total_row['IMPORTE DESCOMISIÓN €'] = round(total, 2)
                                    df_e = pd.concat([df_e, pd.DataFrame([total_row])], ignore_index=True)
                                    return df_e

                                def df_reclamar_export(df_r):
                                    cols = ['Tipo', 'CIF', 'Cliente', 'Comercial', 'Estado', 'CUP Cruce',
                                            'Producto', 'Comisión_liq', 'Fecha Alta', 'Fecha Baja']
                                    cols = [c for c in cols if c in df_r.columns]
                                    df_e = prep_df_export(df_r[cols].copy())
                                    if 'Comisión_liq' in df_e.columns:
                                        df_e = df_e.rename(columns={'Comisión_liq': 'IMPORTE A RECLAMAR €'})
                                    return df_e

                                nombre_base = f"cruce_{compania_detectada.lower()}_{meta.get('mes','')}_{meta.get('anio','')}"
                                df_a_reclamar = pd.concat([sin_match, pendientes]) if (not sin_match.empty or not pendientes.empty) else pd.DataFrame()

                                # Intentar engine xlsx instalado; si no, usar generador nativo
                                _writer_engine = None
                                for _eng in ['xlsxwriter', 'openpyxl']:
                                    try:
                                        importlib.import_module(_eng)
                                        _writer_engine = _eng
                                        break
                                    except ImportError:
                                        pass

                                def df_sva_export(df_s):
                                    """SVA export: CUP, cliente CRM, producto, importe pagado/descom."""
                                    cols_s = ['Tipo','CIF','Cliente','Comercial','Estado','CUP Cruce',
                                              'Producto','Comisión_liq','Estado Liquidación']
                                    cols_s = [c for c in cols_s if c in df_s.columns]
                                    df_e = prep_df_export(df_s[cols_s].copy())
                                    if 'Comisión_liq' in df_e.columns:
                                        df_e = df_e.rename(columns={'Comisión_liq': 'IMPORTE SVA €'})
                                    # Fila total
                                    total_sva = df_s['Comisión_liq'].sum() if 'Comisión_liq' in df_s.columns else 0
                                    if not df_e.empty:
                                        total_row = {c: '' for c in df_e.columns}
                                        total_row[df_e.columns[-2] if len(df_e.columns) > 1 else df_e.columns[0]] = 'TOTAL'
                                        total_row['IMPORTE SVA €'] = round(total_sva, 2)
                                        df_e = pd.concat([df_e, pd.DataFrame([total_row])], ignore_index=True)
                                    return df_e

                                sheets_export = {
                                    'Cruce Completo':   prep_df_export(df_resultado),
                                    'Pagados':          df_pagados_export(pagados),
                                    'Descomisionados':  df_descom_export(descomisionados),
                                    'A Reclamar':       df_reclamar_export(df_a_reclamar),
                                }
                                if not df_sva_resultado.empty:
                                    sheets_export['SVA Cruce'] = df_sva_export(df_sva_resultado)
                                    sheets_export['SVA Pagados'] = df_sva_export(
                                        df_sva_resultado[df_sva_resultado['Estado Liquidación']=='✅ PAGADO'])
                                    sva_reclamar = df_sva_resultado[
                                        ~df_sva_resultado['Estado Liquidación'].isin(['✅ PAGADO','🔴 DESCOMISIONADO'])]
                                    if not sva_reclamar.empty:
                                        sheets_export['SVA A Reclamar'] = df_sva_export(sva_reclamar)

                                if _writer_engine:
                                    output = io.BytesIO()
                                    with pd.ExcelWriter(output, engine=_writer_engine) as writer:
                                        for sname, df_s in sheets_export.items():
                                            df_s.to_excel(writer, sheet_name=sname, index=False)
                                    output.seek(0)
                                    xlsx_bytes = output.read()
                                else:
                                    xlsx_bytes = hacer_xlsx_nativo(sheets_export)

                                st.download_button(
                                    label=f"⬇️ DESCARGAR RESULTADO EXCEL — {nombre_base}.xlsx",
                                    data=xlsx_bytes,
                                    file_name=f"{nombre_base}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                            except Exception as e:
                                import traceback
                                st.error(f"❌ Error en el cruce: {e}")
                                st.code(traceback.format_exc())

                    else:
                        st.markdown("""
                            <div style="background:#f0f0f0; border:2px dashed #30363d; border-radius:12px; padding:40px; text-align:center; margin-top:20px;">
                                <p style="color:#8b949e; font-size:1rem; margin:0;">
                                    👆 Sube la <b style="color:#d2ff00;">liquidación de la compañía</b> y el archivo de 
                                    <b style="color:#d2ff00;">contratos_energia.xlsx</b> para iniciar el cruce automático
                                </p>
                            </div>
                        """, unsafe_allow_html=True)



            with liq_tab_gana:
                st.markdown('<div class="block-header" style="font-size:1rem;">⚡ LIQUIDACIÓN GANA ENERGÍA</div>', unsafe_allow_html=True)
                st.markdown("""
                    <div style="background:#f0f0f0; border:2px dashed #30363d; border-radius:12px; padding:40px; text-align:center; margin-top:20px;">
                        <p style="color:#22c55e; font-size:1.2rem; margin:0 0 8px 0;">⚡ GANA ENERGÍA</p>
                        <p style="color:#8b949e; margin:0; font-size:0.9rem;">Liquidación en construcción — próximamente disponible.</p>
                    </div>
                """, unsafe_allow_html=True)


            with liq_tab_total:
                st.markdown('<div class="block-header" style="font-size:1rem;">🌍 LIQUIDACIÓN TOTAL ENERGIES</div>', unsafe_allow_html=True)
                st.markdown("""
                    <div style="background:#ffffff; border-left:4px solid #3b82f6; padding:15px; border-radius:8px; margin-bottom:20px;">
                        <p style="color:#3b82f6; font-weight:bold; margin:0 0 6px 0;">⚙️ CRUCE AUTOMÁTICO TOTAL ENERGIES</p>
                        <p style="color:#8b949e; margin:0; font-size:0.82rem;">
                            Sube la liquidación de Total Energies y el Excel de contratos.
                            El sistema cruza por <b>Nº Contrato</b> (NombreOferta ↔ ID Contrato Externo),
                            filtra automáticamente Total Energies, y muestra pagado, pendiente y descomisionado por comercial.
                        </p>
                    </div>
                """, unsafe_allow_html=True)

                t_col1, t_col2 = st.columns(2)
                with t_col1:
                    st.markdown('<p style="color:#3b82f6; font-weight:bold; font-size:1rem; margin-bottom:4px;">📄 Liquidación Total Energies</p>', unsafe_allow_html=True)
                    f_total_liq = st.file_uploader("Liquidación Total Energies", type=['xlsx'], key="total_liq_upload", label_visibility="collapsed")
                with t_col2:
                    st.markdown('<p style="color:#3b82f6; font-weight:bold; font-size:1rem; margin-bottom:4px;">📋 Contratos Energía (CRM)</p>', unsafe_allow_html=True)
                    f_total_con = st.file_uploader("Contratos energía Total", type=['xlsx'], key="total_con_upload", label_visibility="collapsed")

                if f_total_liq and f_total_con:
                    with st.spinner("⏳ Procesando liquidación Total Energies..."):
                        try:
                            def fmt_fecha_total(val):
                                if val is None or str(val).strip() in ['','nan','None','NaT']: return ''
                                s = str(val).strip()
                                if len(s) >= 10 and s[2] == '/': return s[:10]
                                if len(s) >= 10 and s[4] == '-':
                                    try:
                                        from datetime import datetime
                                        return datetime.strptime(s[:10], '%Y-%m-%d').strftime('%d/%m/%Y')
                                    except: return s[:10]
                                try:
                                    from datetime import date, timedelta
                                    return (date(1899,12,30)+timedelta(days=int(float(s)))).strftime('%d/%m/%Y')
                                except: return s

                            def norm_contrato(val):
                                """Normaliza nº contrato eliminando ceros a la izquierda."""
                                if val is None or str(val).strip() in ['','nan','None']: return None
                                try: return str(int(float(str(val).strip()))).lstrip('0') or '0'
                                except: return str(val).strip().lstrip('0') or str(val).strip()

                            # Leer liquidación Total (tiene header en fila 0)
                            df_t_liq = leer_excel_safe(f_total_liq, header=0)
                            df_t_liq.columns = [str(c).strip() for c in df_t_liq.columns]

                            # Detectar columnas clave
                            col_contrato_liq = next((c for c in df_t_liq.columns if 'NOMBREOFERTA' in c.upper() or 'NOMBRE' in c.upper() and 'OFERTA' in c.upper()), None)
                            col_agente      = next((c for c in df_t_liq.columns if 'AGENTE' in c.upper() or 'ASESOR' in c.upper()), None)
                            col_energia     = next((c for c in df_t_liq.columns if 'ENERGIA' in c.upper() or 'ENERGÍA' in c.upper()), None)
                            col_concepto    = next((c for c in df_t_liq.columns if 'CONCEPTO' in c.upper()), None)
                            col_comision    = next((c for c in df_t_liq.columns if 'COMISION' in c.upper() or 'COMISIÓN' in c.upper()), None)
                            col_fecha_liq   = next((c for c in df_t_liq.columns if 'LIQUIDACION' in c.upper() or 'LIQUIDACIÓN' in c.upper()), None)
                            col_fecha_venta = next((c for c in df_t_liq.columns if 'VENTA' in c.upper()), None)
                            col_fecha_act   = next((c for c in df_t_liq.columns if 'ACTIVACION' in c.upper() or 'ACTIVACIÓN' in c.upper()), None)
                            col_fecha_baja  = next((c for c in df_t_liq.columns if 'BAJA' in c.upper()), None)
                            col_id_linea    = next((c for c in df_t_liq.columns if 'IDLINEA' in c.upper() or 'LINEAOFERTA' in c.upper()), None)

                            if not col_contrato_liq or not col_comision:
                                st.error("❌ No se encontraron columnas NombreOferta o Comision en la liquidación de Total.")
                                st.stop()

                            # Normalizar clave de contrato
                            df_t_liq['contrato_key'] = df_t_liq[col_contrato_liq].apply(norm_contrato)

                            # Formatear fechas
                            for fc in [col_fecha_liq, col_fecha_venta, col_fecha_act, col_fecha_baja]:
                                if fc and fc in df_t_liq.columns:
                                    df_t_liq[fc] = df_t_liq[fc].apply(fmt_fecha_total)

                            # Leer contratos CRM
                            df_t_con = leer_excel_safe(f_total_con, header=0)
                            df_t_con.columns = [str(c).strip() for c in df_t_con.columns]

                            # Filtrar Total Energies
                            if 'Comercializadora' in df_t_con.columns:
                                df_total_crm = df_t_con[
                                    df_t_con['Comercializadora'].str.contains('Total', case=False, na=False)
                                ].copy()
                            else:
                                df_total_crm = df_t_con.copy()

                            col_id_ext = next((c for c in df_total_crm.columns if 'ID CONTRATO' in c.upper() or 'CONTRATO EXTERNO' in c.upper()), None)
                            if not col_id_ext:
                                col_id_ext = 'ID Contrato Externo'

                            df_total_crm['contrato_key'] = df_total_crm[col_id_ext].apply(norm_contrato) if col_id_ext in df_total_crm.columns else None

                            # Formatear fechas CRM
                            for fc in ['Fecha Creación','Fecha Activación']:
                                if fc in df_total_crm.columns:
                                    df_total_crm[fc] = df_total_crm[fc].apply(fmt_fecha_total)

                            # ── CRUCE: nuestros contratos ↔ liquidación Total ──
                            keys_crm = set(df_total_crm['contrato_key'].dropna())

                            # Filtrar liq solo a nuestros contratos
                            df_liq_nuestros = df_t_liq[df_t_liq['contrato_key'].isin(keys_crm)].copy()

                            # Agrupar por contrato + concepto para resumen de comisiones
                            # Conceptos que son comisión real: LUZ, GAS, FACILITA, FACILITADUALPLUSHOGAR, FACILITALUZHOGA...
                            conceptos_comision = {'LUZ','GAS','FACILITA','FACILITADUALPLUSH OGARES','FACILITALUZHOGAR ES','BAJUSTE'}

                            # Merge liq → CRM para añadir datos del contrato
                            cols_crm_merge = ['ID','Cliente','Comercial','Estado','CUPS Luz','CUPS Gas','Comisión','contrato_key']
                            cols_crm_merge = [c for c in cols_crm_merge if c in df_total_crm.columns]
                            df_merged = pd.merge(
                                df_liq_nuestros,
                                df_total_crm[cols_crm_merge],
                                on='contrato_key', how='left', suffixes=('','_crm')
                            )

                            # Estado liquidación por fila
                            def clasif_total(row):
                                fb = str(row.get(col_fecha_baja,'')).strip() if col_fecha_baja else ''
                                com = float(row.get(col_comision, 0) or 0)
                                if fb and fb not in ['','nan','None']: return '🔴 DESCOMISIONADO'
                                if com < 0: return '🔴 DESCOMISIONADO'
                                if com > 0: return '✅ PAGADO'
                                return '❓ PENDIENTE'

                            df_merged['Estado Liq'] = df_merged.apply(clasif_total, axis=1)

                            # Contratos nuestros NO encontrados en liq
                            keys_en_liq = set(df_liq_nuestros['contrato_key'].dropna())
                            df_no_en_liq = df_total_crm[~df_total_crm['contrato_key'].isin(keys_en_liq)].copy()

                            # ── KPIs ──
                            pagados    = df_merged[df_merged['Estado Liq']=='✅ PAGADO']
                            descom     = df_merged[df_merged['Estado Liq']=='🔴 DESCOMISIONADO']
                            pendiente  = df_merged[df_merged['Estado Liq']=='❓ PENDIENTE']

                            total_cobrado = float(pagados[col_comision].sum()) if col_comision in pagados.columns else 0
                            total_descom  = float(descom[col_comision].sum()) if col_comision in descom.columns else 0
                            n_no_liq      = len(df_no_en_liq)

                            st.markdown("---")
                            kt1, kt2, kt3, kta, ktb = st.columns(5)
                            box_t = "border-radius:10px; padding:14px 8px; text-align:center; margin-bottom:10px;"
                            kt1.markdown(f'<div style="background:#f0fff4; border:2px solid #22c55e; {box_t}"><p style="color:#22c55e; font-size:0.7rem; font-weight:bold; margin:0;">✅ PAGADOS</p><h2 style="color:#111111; margin:4px 0;">{len(pagados)}</h2><p style="color:#22c55e; font-size:0.8rem; font-weight:bold; margin:0;">{total_cobrado:,.0f}€</p></div>', unsafe_allow_html=True)
                            kt2.markdown(f'<div style="background:#fff0f0; border:2px solid #ff4b4b; {box_t}"><p style="color:#ff4b4b; font-size:0.7rem; font-weight:bold; margin:0;">🔴 DESCOMISIONADOS</p><h2 style="color:#111111; margin:4px 0;">{len(descom)}</h2><p style="color:#ff4b4b; font-size:0.8rem; font-weight:bold; margin:0;">{total_descom:,.0f}€</p></div>', unsafe_allow_html=True)
                            kt3.markdown(f'<div style="background:#ffffff; border:2px solid #8b949e; {box_t}"><p style="color:#8b949e; font-size:0.7rem; font-weight:bold; margin:0;">❓ PENDIENTE</p><h2 style="color:#111111; margin:4px 0;">{len(pendiente)}</h2></div>', unsafe_allow_html=True)
                            kta.markdown(f'<div style="background:#f8f0ff; border:2px solid #a78bfa; {box_t}"><p style="color:#a78bfa; font-size:0.7rem; font-weight:bold; margin:0;">⚠️ NO EN LIQ</p><h2 style="color:#111111; margin:4px 0;">{n_no_liq}</h2></div>', unsafe_allow_html=True)
                            ktb.markdown(f'<div style="background:#f0f4ff; border:2px solid #3b82f6; {box_t}"><p style="color:#3b82f6; font-size:0.7rem; font-weight:bold; margin:0;">📋 TOTAL CRM</p><h2 style="color:#111111; margin:4px 0;">{len(df_total_crm)}</h2></div>', unsafe_allow_html=True)

                            # ── Columnas resultado ──
                            cols_show_t = []
                            for c in ['ID','Cliente','Comercial','Estado','CUPS Luz','CUPS Gas']:
                                if c in df_merged.columns: cols_show_t.append(c)
                            for c in [col_agente, col_energia, col_concepto, col_comision,
                                       col_fecha_venta, col_fecha_act, col_fecha_baja, col_fecha_liq]:
                                if c and c in df_merged.columns and c not in cols_show_t:
                                    cols_show_t.append(c)
                            cols_show_t.append('Estado Liq')
                            cols_show_t = [c for c in cols_show_t if c in df_merged.columns]

                            # ── Resumen por comercial (filtrable) ──
                            if 'Comercial' in df_merged.columns and col_comision in df_merged.columns:
                                resumen_comercial = df_merged.groupby('Comercial').agg(
                                    Contratos=('contrato_key', 'nunique'),
                                    Total_Cobrado=(col_comision, lambda x: x[df_merged.loc[x.index,'Estado Liq']=='✅ PAGADO'].sum()),
                                    Filas_Pagadas=('Estado Liq', lambda x: (x=='✅ PAGADO').sum()),
                                    Descomisionados=('Estado Liq', lambda x: (x=='🔴 DESCOMISIONADO').sum()),
                                ).reset_index().sort_values('Total_Cobrado', ascending=False)
                                resumen_comercial['Total_Cobrado'] = resumen_comercial['Total_Cobrado'].round(2)

                            # ── Tabs ──
                            tt0, tt1, tt2, tt3, tt4 = st.tabs([
                                f"👤 POR COMERCIAL",
                                f"✅ PAGADOS ({len(pagados)})",
                                f"🔴 DESCOMISIONADOS ({len(descom)})",
                                f"⚠️ NO EN LIQ ({n_no_liq})",
                                f"📋 COMPLETO ({len(df_merged)})"
                            ])

                            def df_display_total(df_sub):
                                d = df_sub[cols_show_t].copy().reset_index(drop=True)
                                return d

                            with tt0:
                                st.markdown('<p style="color:#3b82f6; font-size:0.85rem;">Resumen de comisiones abonadas por comercial. Filtra por comercial para ver el detalle.</p>', unsafe_allow_html=True)
                                if 'Comercial' in df_merged.columns:
                                    # Selector de comercial
                                    comerciales = ['Todos'] + sorted(df_merged['Comercial'].dropna().unique().tolist())
                                    sel_com = st.selectbox("Filtrar por comercial:", comerciales, key="total_comercial_sel")
                                    if 'Comercial' in df_merged.columns and col_comision in df_merged.columns:
                                        st.dataframe(resumen_comercial, use_container_width=True, height=280)
                                        st.markdown("---")
                                        if sel_com != 'Todos':
                                            df_fil = df_merged[df_merged['Comercial']==sel_com]
                                        else:
                                            df_fil = df_merged
                                        st.markdown(f'**Detalle filas** — {sel_com}:')
                                        st.dataframe(df_display_total(df_fil), use_container_width=True, height=360)

                            with tt1:
                                st.markdown(f'<p style="color:#22c55e;">Total abonado: <b>{total_cobrado:,.0f}€</b></p>', unsafe_allow_html=True)
                                st.dataframe(df_display_total(pagados), use_container_width=True, height=420)
                                st.download_button("⬇️ Descargar PAGADOS",
                                    hacer_xlsx_nativo({'Pagados Total': df_display_total(pagados)}),
                                    file_name="total_energy_pagados.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True)

                            with tt2:
                                st.markdown(f'<p style="color:#ff4b4b;">Total descomisionado: <b>{total_descom:,.0f}€</b></p>', unsafe_allow_html=True)
                                if not descom.empty:
                                    st.dataframe(df_display_total(descom), use_container_width=True, height=420)
                                    st.download_button("⬇️ Descargar DESCOMISIONADOS",
                                        hacer_xlsx_nativo({'Descomisionados': df_display_total(descom)}),
                                        file_name="total_energy_descomisionados.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        use_container_width=True)
                                else:
                                    st.success("✅ Sin descomisiones.")

                            with tt3:
                                st.markdown('<p style="color:#a78bfa;">Contratos nuestros con Total Energies que no aparecen en la liquidación — verificar o reclamar.</p>', unsafe_allow_html=True)
                                cols_no_liq = [c for c in ['ID','ID Contrato Externo','Cliente','Comercial','Estado','Fecha Creación','Fecha Activación','CUPS Luz','CUPS Gas','Comisión'] if c in df_no_en_liq.columns]
                                if not df_no_en_liq.empty:
                                    st.dataframe(df_no_en_liq[cols_no_liq].reset_index(drop=True), use_container_width=True, height=420)
                                    st.download_button("⬇️ Descargar NO EN LIQUIDACIÓN",
                                        hacer_xlsx_nativo({'No en Liq': df_no_en_liq[cols_no_liq].reset_index(drop=True)}),
                                        file_name="total_energy_no_liquidados.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        use_container_width=True)
                                else:
                                    st.success("✅ Todos los contratos aparecen en la liquidación.")

                            with tt4:
                                df_comp_t = df_display_total(df_merged)
                                st.dataframe(df_comp_t, use_container_width=True, height=460)
                                st.download_button("⬇️ Descargar CRUCE COMPLETO",
                                    hacer_xlsx_nativo({
                                        'Completo': df_comp_t,
                                        'Pagados': df_display_total(pagados),
                                        'Descomisionados': df_display_total(descom) if not descom.empty else pd.DataFrame(),
                                        'No en Liq': df_no_en_liq[cols_no_liq].reset_index(drop=True) if not df_no_en_liq.empty else pd.DataFrame(),
                                    }),
                                    file_name="total_energy_cruce_completo.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True)

                        except Exception as _et:
                            import traceback
                            st.error(f"❌ Error en liquidación Total Energies: {_et}")
                            st.code(traceback.format_exc())
                else:
                    st.markdown("""
                        <div style="background:#f0f0f0; border:2px dashed #30363d; border-radius:12px; padding:30px; text-align:center; margin-top:10px;">
                            <p style="color:#8b949e; margin:0;">👆 Sube la liquidación de Total Energies y el archivo de contratos para iniciar el cruce</p>
                        </div>
                    """, unsafe_allow_html=True)

            # ── ARCHIVOS EN DRIVE ──
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="block-header">📁 LIQUIDACIONES EN DRIVE</div>', unsafe_allow_html=True)
            col_liq1, col_liq2 = st.columns(2)
            with col_liq1:
                with st.expander("⚡ Liquidaciones Energía"):
                    mostrar_carpeta_dir("directivos", "LIQUIDACIONES/ENERGIA", "⚡")
                with st.expander("📶 Liquidaciones Telco"):
                    mostrar_carpeta_dir("directivos", "LIQUIDACIONES/TELCO", "📶")
            with col_liq2:
                with st.expander("🛡️ Liquidaciones Alarmas"):
                    mostrar_carpeta_dir("directivos", "LIQUIDACIONES/ALARMAS", "🛡️")
                with st.expander("📋 Liquidaciones Generales"):
                    mostrar_carpeta_dir("directivos", "LIQUIDACIONES/GENERAL", "📋")

        # ── TAB DOCS EMPRESA ──
        # ══════════════════════════════════════════════════════
        # ── TAB CRUCES CIAS ──
        # ══════════════════════════════════════════════════════
        if _sel == "🔀 CRUCES CIAS":
            st.markdown('<div class="block-header">🔀 CRUCES CON COMPAÑÍAS</div>', unsafe_allow_html=True)
            st.markdown("""
                <div style="background:#ffffff; border-left:4px solid #FFD700; padding:15px; border-radius:8px; margin-bottom:20px;">
                    <p style="color:#8b949e; margin:0; font-size:0.85rem;">
                        Cruce de nuestras ventas con los archivos de cada compañía para detectar discrepancias,
                        contratos no reconocidos y estados incorrectos.
                    </p>
                </div>
            """, unsafe_allow_html=True)

            cia_tab_gana, cia_tab_naturgy, cia_tab_total = st.tabs([
                "⚡ GANA ENERGÍA", "🔥 NATURGY", "🌍 TOTAL ENERGIES"
            ])

            # ─────────────────────────────────────────────────────
            # ── GANA ENERGÍA — CRUCE COMPLETO ──
            # ─────────────────────────────────────────────────────
            with cia_tab_gana:
                st.markdown('<div class="block-header" style="font-size:1rem;">⚡ CRUCE GANA ENERGÍA</div>', unsafe_allow_html=True)
                st.markdown("""
                    <div style="background:#f0f0f0; border-left:4px solid #22c55e; padding:12px; border-radius:8px; margin-bottom:16px;">
                        <p style="color:#8b949e; margin:0; font-size:0.82rem;">
                            Sube <b style="color:#22c55e;">nuestras ventas</b> (export CRM con CUPS) y el archivo de
                            <b style="color:#22c55e;">Gana Energía</b>. El sistema cruza por CUP (20 ó 22 dígitos) y
                            muestra qué contratos están en Gana, cuáles no aparecen y las discrepancias de estado.
                        </p>
                    </div>
                """, unsafe_allow_html=True)

                gc1, gc2 = st.columns(2)
                with gc1:
                    st.markdown('<p style="color:#22c55e; font-weight:bold; font-size:0.95rem; margin-bottom:4px;">📋 Nuestras Ventas (CRM)</p>', unsafe_allow_html=True)
                    f_gana_nuestras = st.file_uploader("Nuestras ventas", type=['xlsx'], key="gana_nuestras", label_visibility="collapsed")
                with gc2:
                    st.markdown('<p style="color:#22c55e; font-weight:bold; font-size:0.95rem; margin-bottom:4px;">⚡ Archivo Gana Energía</p>', unsafe_allow_html=True)
                    f_gana_cia = st.file_uploader("Archivo Gana", type=['xlsx'], key="gana_cia", label_visibility="collapsed")

                if f_gana_nuestras and f_gana_cia:
                    with st.spinner("⏳ Cruzando datos con Gana Energía..."):
                        try:
                            # ── Funciones de normalización ──
                            def norm16(cup):
                                """Normaliza CUP a 16 chars comparables (Gana enmascara los últimos 4 con ****)."""
                                if cup is None: return None
                                s = str(cup).strip().upper().replace('*', '')
                                if len(s) >= 22: s = s[:20]  # truncar de 22 a 20
                                return s[:16] if len(s) >= 16 else s

                            def fmt_f(val):
                                """Convierte cualquier valor a dd/mm/yyyy."""
                                if val is None or str(val).strip() in ['','nan','None','NaT']: return ''
                                s = str(val).strip()
                                # Ya en dd/mm/yyyy
                                if len(s) >= 10 and s[2] == '/': return s[:10]
                                # yyyy-mm-dd (con o sin hora)
                                if len(s) >= 10 and s[4] == '-':
                                    try:
                                        from datetime import datetime
                                        return datetime.strptime(s[:10], '%Y-%m-%d').strftime('%d/%m/%Y')
                                    except: return s[:10]
                                # Serial numérico de Excel
                                try:
                                    from datetime import date, timedelta
                                    return (date(1899,12,30) + timedelta(days=int(float(s)))).strftime('%d/%m/%Y')
                                except: return s

                            # ── Leer nuestras ventas (CRM export) ──
                            df_crm_full = leer_excel_safe(f_gana_nuestras, header=0)
                            df_crm_full.columns = [str(c).strip() for c in df_crm_full.columns]

                            # Estados que NO deben aparecer en el cruce con Gana
                            ESTADOS_EXCLUIR_GANA = {
                                'Error - Contrato mal generado',
                                'Firmado - Anulado CS',
                                'Firmado - Anulado',
                                'Sin Firmar - Anulado',
                                'Sin Firmar',
                            }

                            # Filtrar solo contratos Gana
                            if 'Comercializadora' in df_crm_full.columns:
                                df_crm = df_crm_full[
                                    df_crm_full['Comercializadora'].apply(lambda x: 'gana' in str(x).lower())
                                ].copy()
                            else:
                                df_crm = df_crm_full.copy()

                            # Excluir estados que no deben aparecer
                            if 'Estado' in df_crm.columns:
                                df_crm = df_crm[~df_crm['Estado'].isin(ESTADOS_EXCLUIR_GANA)].copy()

                            # Normalizar CUPs a 16 chars
                            if 'CUPS Luz' in df_crm.columns:
                                df_crm['CUP_Luz_16'] = df_crm['CUPS Luz'].apply(norm16)
                            if 'CUPS Gas' in df_crm.columns:
                                df_crm['CUP_Gas_16'] = df_crm['CUPS Gas'].apply(norm16)

                            # ── Filtro de fecha de creación (MM/AAAA) ──
                            def mes_anio_g(fecha_str):
                                try: return fecha_str[3:5] + '/' + fecha_str[6:10]
                                except: return ''

                            fechas_g = []
                            if 'Fecha Creación' in df_crm.columns:
                                df_crm['_mes_anio'] = df_crm['Fecha Creación'].apply(mes_anio_g)
                                fechas_g = sorted([f for f in df_crm['_mes_anio'].unique() if f], reverse=True)
                            sel_fg = st.multiselect(
                                "🗓️ Filtrar por mes/año de creación (puedes elegir varios):",
                                options=fechas_g,
                                default=[],
                                key="gana_fecha_sel",
                                placeholder="Sin filtro — mostrando todos los meses"
                            )
                            # df_crm_vista = filtrado para mostrar / df_crm = base completa para lookup
                            df_crm_vista = df_crm[df_crm['_mes_anio'].isin(sel_fg)].copy() if (sel_fg and '_mes_anio' in df_crm.columns) else df_crm.copy()
                            # ── Leer archivo Gana CIA ──
                            df_cia = leer_excel_safe(f_gana_cia, header=0)
                            df_cia.columns = [str(c).strip() for c in df_cia.columns]

                            # Detectar columna CUPS en archivo Gana
                            cup_col = None
                            for col in df_cia.columns:
                                nn = df_cia[col].dropna()
                                if not nn.empty and str(nn.iloc[0]).upper().startswith('ES0'):
                                    cup_col = col
                                    break
                            if not cup_col:
                                st.warning("⚠️ No se encontró columna CUPS en el archivo de Gana.")
                                cup_col = None

                            fecha_cols_cia = [c for c in df_cia.columns if 'FECHA' in str(c).upper() or 'DATE' in str(c).upper()]
                            for fc in fecha_cols_cia:
                                df_cia[fc] = df_cia[fc].apply(fmt_f)

                            df_cia['CUP_16'] = df_cia[cup_col].apply(norm16)

                            # ── CRUCE: CRM vista (filtrado) ↔ Gana CIA por CUP ──
                            # Cuando hay filtro activo usamos df_crm_vista como base (nuestros contratos
                            # del mes seleccionado) y buscamos su match en Gana.
                            # Sin filtro: usamos df_crm completo.
                            cols_crm_merge = [c for c in ['ID','ID Contrato Externo','Cliente','Comercial',
                                              'Estado','Tarifa','Comisión','CUPS Luz','CUPS Gas',
                                              'Fecha Creación','Fecha Activación'] if c in df_crm_vista.columns]

                            # Construir lookup Gana: CUP_16 → fila Gana
                            cia_cols_show = [c for c in df_cia.columns if c != 'CUP_16']
                            df_cia_lookup = df_cia[df_cia['CUP_16'].notna()].drop_duplicates('CUP_16')

                            # Merge: CRM_VISTA (base) ← Gana (lookup) por CUP
                            crm_luz_rows = []
                            crm_gas_rows = []
                            if 'CUP_Luz_16' in df_crm_vista.columns:
                                crm_luz_rows = df_crm_vista[df_crm_vista['CUP_Luz_16'].notna()][cols_crm_merge + ['CUP_Luz_16']].rename(columns={'CUP_Luz_16':'_cup_match'})
                            if 'CUP_Gas_16' in df_crm_vista.columns:
                                crm_gas_rows = df_crm_vista[df_crm_vista['CUP_Gas_16'].notna()][cols_crm_merge + ['CUP_Gas_16']].rename(columns={'CUP_Gas_16':'_cup_match'})

                            df_crm_for_merge = pd.concat(
                                [r for r in [crm_luz_rows, crm_gas_rows] if isinstance(r, pd.DataFrame) and not r.empty],
                                ignore_index=True
                            ).drop_duplicates(subset=['ID'] if 'ID' in cols_crm_merge else ['_cup_match']) if (isinstance(crm_luz_rows, pd.DataFrame) or isinstance(crm_gas_rows, pd.DataFrame)) else pd.DataFrame()

                            if not df_crm_for_merge.empty:
                                df_merged = pd.merge(
                                    df_crm_for_merge,
                                    df_cia_lookup[['CUP_16'] + cia_cols_show].rename(columns={'CUP_16':'_cup_match'}),
                                    on='_cup_match', how='left', suffixes=('','_cia')
                                )
                            else:
                                df_merged = pd.DataFrame(columns=cols_crm_merge + cia_cols_show)

                            # Estado Cruce: si tiene col Gana (ej: FECHA DE CREACIÓN) entonces matchó
                            _cia_check = cia_cols_show[0] if cia_cols_show else None
                            if _cia_check and _cia_check in df_merged.columns:
                                df_merged['ESTADO CRUCE'] = df_merged[_cia_check].apply(
                                    lambda x: '✅ En Gana' if (x is not None and str(x) not in ['','nan','None']) else '❌ No en Gana')
                            else:
                                df_merged['ESTADO CRUCE'] = '❌ No en Gana' 

                            # ── CRUCE 2: Nuestros no en Gana → usa df_crm_vista (filtrado) ──
                            cups_gana_16 = set(df_cia['CUP_16'].dropna())
                            _v = df_crm_vista.copy()
                            if 'CUP_Luz_16' in _v.columns:
                                _v['_en_g'] = _v['CUP_Luz_16'].apply(lambda c: c in cups_gana_16 if c else False)
                            else:
                                _v['_en_g'] = False
                            if 'CUP_Gas_16' in _v.columns:
                                _v['_en_g2'] = _v['CUP_Gas_16'].apply(lambda c: c in cups_gana_16 if c else False)
                            else:
                                _v['_en_g2'] = False
                            df_nuestros_no_gana = _v[~_v['_en_g'] & ~_v['_en_g2']].copy()
                            for fc in ['Fecha Creación','Fecha Activación']:
                                if fc in df_nuestros_no_gana.columns:
                                    df_nuestros_no_gana[fc] = df_nuestros_no_gana[fc].apply(fmt_f)

                            # ── KPIs ──
                            n_en_crm   = (df_merged['ESTADO CRUCE'] == '✅ En Gana').sum()
                            n_no_crm   = (df_merged['ESTADO CRUCE'] == '❌ No en Gana').sum()
                            n_no_gana  = len(df_nuestros_no_gana)

                            st.markdown("---")
                            if sel_fg:
                                st.info(f"🗓️ Mostrando: {', '.join(sel_fg)} — {len(df_crm_vista)} de {len(df_crm)} contratos Gana en CRM")
                            k1, k2, k3, k4 = st.columns(4)
                            box_g = "border-radius:10px; padding:14px 8px; text-align:center; margin-bottom:10px;"
                            k1.markdown(f'<div style="background:#f0fff4; border:2px solid #22c55e; {box_g}"><p style="color:#22c55e; font-size:0.7rem; font-weight:bold; margin:0;">✅ GANA CON MATCH CRM</p><h2 style="color:#111111; margin:4px 0;">{n_en_crm}</h2></div>', unsafe_allow_html=True)
                            k2.markdown(f'<div style="background:#fff0f0; border:2px solid #ff4b4b; {box_g}"><p style="color:#ff4b4b; font-size:0.7rem; font-weight:bold; margin:0;">❌ GANA SIN CRM</p><h2 style="color:#111111; margin:4px 0;">{n_no_crm}</h2></div>', unsafe_allow_html=True)
                            k3.markdown(f'<div style="background:#f8f0ff; border:2px solid #a78bfa; {box_g}"><p style="color:#a78bfa; font-size:0.7rem; font-weight:bold; margin:0;">⚠️ NUESTROS NO EN GANA</p><h2 style="color:#111111; margin:4px 0;">{n_no_gana}</h2></div>', unsafe_allow_html=True)
                            k4.markdown(f'<div style="background:#ffffff; border:2px solid #8b949e; {box_g}"><p style="color:#8b949e; font-size:0.7rem; font-weight:bold; margin:0;">📋 TOTAL EN GANA</p><h2 style="color:#111111; margin:4px 0;">{len(df_cia)}</h2></div>', unsafe_allow_html=True)

                            # ── Columnas resultado: CRM (base) + Gana (lookup) ──
                            crm_cols_display = [c for c in ['ESTADO CRUCE','Comercial','CUPS Luz','CUPS Gas',
                                'Fecha Creación','Fecha Activación','ID','Cliente','Estado',
                                'Tarifa','Comisión','ID Contrato Externo'] if c in df_merged.columns]
                            cia_cols_display = [c for c in df_merged.columns
                                if c not in crm_cols_display and not c.startswith('_')]
                            cols_result = crm_cols_display + cia_cols_display
                            cols_result = [c for c in cols_result if c in df_merged.columns]
                            # Columnas para nuestros no en Gana
                            cols_nuestros = [c for c in ['ID','ID Contrato Externo','Cliente','Comercial',
                                                          'Estado','Comercializadora','Tarifa',
                                                          'Fecha Creación','Fecha Activación',
                                                          'CUPS Luz','CUPS Gas','Comisión']
                                              if c in df_nuestros_no_gana.columns]

                            def _safe_xlsx(sheets):
                                """Genera xlsx evitando crash si un df está vacío."""
                                clean = {}
                                for k, v in sheets.items():
                                    clean[k] = v if (isinstance(v, pd.DataFrame) and not v.empty) else pd.DataFrame({'(sin datos)': ['No hay registros']})
                                return hacer_xlsx_nativo(clean)

                            gt1, gt2, gt3 = st.tabs([
                                f"📋 GANA COMPLETO ({len(df_merged)})",
                                f"❌ GANA SIN CRM ({n_no_crm})",
                                f"⚠️ NUESTROS NO EN GANA ({n_no_gana})"
                            ])

                            with gt1:
                                df_show1 = df_merged[cols_result].reset_index(drop=True)
                                _hdr1, _btn1 = st.columns([4,1])
                                with _hdr1: st.markdown('<p style="color:#8b949e;font-size:0.83rem;margin:0;">Todos los contratos de Gana + datos CRM donde hay match.</p>', unsafe_allow_html=True)
                                with _btn1: st.download_button("⬇️ Descargar",
                                    _safe_xlsx({'Gana Completo': df_show1,
                                        'Gana sin CRM': df_merged[df_merged['ESTADO CRUCE']=='❌ No en Gana'][cols_result].reset_index(drop=True),
                                        'Nuestros no Gana': df_nuestros_no_gana[cols_nuestros].reset_index(drop=True)}),
                                    file_name="gana_cruce_completo.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True, key="dl_gt1")
                                st.dataframe(df_show1, use_container_width=True, height=420)

                            with gt2:
                                df_show2 = df_merged[df_merged['ESTADO CRUCE']=='❌ No en Gana'][cols_result].reset_index(drop=True)
                                _hdr2, _btn2 = st.columns([4,1])
                                with _hdr2: st.markdown('<p style="color:#ff4b4b;font-size:0.83rem;margin:0;">En Gana pero <b>no en nuestro CRM</b> — verificar si son nuestros.</p>', unsafe_allow_html=True)
                                with _btn2: st.download_button("⬇️ Descargar",
                                    _safe_xlsx({'Gana sin CRM': df_show2}),
                                    file_name="gana_sin_crm.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True, key="dl_gt2")
                                st.dataframe(df_show2, use_container_width=True, height=420)

                            with gt3:
                                df_show3 = df_nuestros_no_gana[cols_nuestros].reset_index(drop=True)
                                _hdr3, _btn3 = st.columns([4,1])
                                with _hdr3: st.markdown('<p style="color:#a78bfa;font-size:0.83rem;margin:0;">Nuestros contratos Gana que <b>no aparecen en el archivo</b> — reclamar.</p>', unsafe_allow_html=True)
                                with _btn3: st.download_button("⬇️ Descargar",
                                    _safe_xlsx({'Nuestros no en Gana': df_show3}),
                                    file_name="gana_nuestros_no_encontrados.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True, key="dl_gt3")
                                st.dataframe(df_show3, use_container_width=True, height=420)

                        except Exception as _eg:
                            import traceback
                            st.error(f"❌ Error en cruce Gana: {_eg}")
                            st.code(traceback.format_exc())
                    st.markdown("""
                        <div style="background:#f0f0f0; border:2px dashed #30363d; border-radius:12px; padding:30px; text-align:center; margin-top:10px;">
                            <p style="color:#8b949e; margin:0;">👆 Sube los dos archivos para iniciar el cruce con Gana Energía</p>
                        </div>
                    """, unsafe_allow_html=True)

            # ─────────────────────────────────────────────────────
            # ── NATURGY — PRÓXIMAMENTE ──
            # ─────────────────────────────────────────────────────
            with cia_tab_naturgy:
                st.markdown('<div class="block-header" style="font-size:1rem;">🔥 CRUCE NATURGY</div>', unsafe_allow_html=True)
                st.markdown("""
                    <div style="background:#f0f0f0; border-left:4px solid #FFD700; padding:12px; border-radius:8px; margin-bottom:16px;">
                        <p style="color:#c9d1d9; margin:0; font-size:0.82rem;">
                            Sube <b style="color:#FFD700;">nuestras ventas</b> (export CRM) y la
                            <b style="color:#FFD700;">extracción de Naturgy</b> (exportedDataorders).
                            Cruce por CUP (20 chars). Genera: Cruce Completo · Faltan en CRM · Faltan en Naturgy.
                        </p>
                    </div>
                """, unsafe_allow_html=True)

                cn1, cn2 = st.columns(2)
                with cn1:
                    st.markdown('<p style="color:#FFD700;font-weight:bold;font-size:0.95rem;margin-bottom:4px;">📋 Nuestras Ventas (CRM)</p>', unsafe_allow_html=True)
                    f_nat_crm = st.file_uploader("Nuestras ventas Naturgy", type=['xlsx'], key="naturgy_nuestras", label_visibility="collapsed")
                with cn2:
                    st.markdown('<p style="color:#FFD700;font-weight:bold;font-size:0.95rem;margin-bottom:4px;">🔥 Extracción Naturgy (exportedDataorders)</p>', unsafe_allow_html=True)
                    f_nat_ext = st.file_uploader("Extracción Naturgy", type=['xlsx'], key="naturgy_cia", label_visibility="collapsed")

                if f_nat_crm and f_nat_ext:
                    with st.spinner("⏳ Cruzando datos con Naturgy..."):
                        try:
                            # ── Utilidades ──
                            def n20(cup):
                                """Normaliza CUP/DNI: strip espacios + upper + trunca a 20."""
                                if cup is None or str(cup).strip() in ['','nan','None']: return None
                                s = str(cup).strip().upper()
                                return s[:20] if len(s) >= 20 else s

                            def strip_dni(val):
                                """Limpia DNI/NIF quitando espacios al inicio y final."""
                                if val is None or str(val).strip() in ['','nan','None']: return ''
                                return str(val).strip().upper()

                            def ffn(val):
                                if val is None or str(val).strip() in ['','nan','None','NaT']: return ''
                                s = str(val).strip()
                                if len(s) >= 10 and s[2] == '/': return s[:10]
                                if len(s) >= 10 and s[4] == '-':
                                    try:
                                        from datetime import datetime as _dt
                                        return _dt.strptime(s[:10], '%Y-%m-%d').strftime('%d/%m/%Y')
                                    except: return s[:10]
                                try:
                                    from datetime import date as _d, timedelta as _td
                                    return (_d(1899,12,30)+_td(days=int(float(s)))).strftime('%d/%m/%Y')
                                except: return s

                            def mes_anio_n(s):
                                try: return s[3:5]+'/'+s[6:10]
                                except: return ''

                            def _safe(sheets):
                                return hacer_xlsx_nativo({
                                    k: v if (isinstance(v, pd.DataFrame) and not v.empty)
                                       else pd.DataFrame({'(sin datos)': ['No hay registros']})
                                    for k, v in sheets.items()
                                })

                            # ── Leer CRM ──
                            df_nc_all = leer_excel_safe(f_nat_crm, header=0)
                            df_nc_all.columns = [str(c).strip() for c in df_nc_all.columns]
                            for fc in ['Fecha Creación','Fecha Activación']:
                                if fc in df_nc_all.columns:
                                    df_nc_all[fc] = df_nc_all[fc].apply(ffn)

                            # Filtrar sólo contratos Naturgy (df_nc = BASE COMPLETA para lookup)
                            if 'Comercializadora' in df_nc_all.columns:
                                df_nc = df_nc_all[df_nc_all['Comercializadora'].str.contains('Naturgy', case=False, na=False)].copy()
                            else:
                                df_nc = df_nc_all.copy()

                            # Limpiar DNI y CUPs CRM (strip espacios inicio/final/intermedios)
                            def clean_str_crm(x):
                                if x is None or str(x).strip() in ['nan','None','']: return None
                                return ' '.join(str(x).strip().split())

                            if 'DNI Cliente' in df_nc.columns:
                                df_nc['DNI Cliente'] = df_nc['DNI Cliente'].apply(clean_str_crm)
                            if 'CUPS Luz' in df_nc.columns:
                                df_nc['CUPS Luz'] = df_nc['CUPS Luz'].apply(clean_str_crm)
                            if 'CUPS Gas' in df_nc.columns:
                                df_nc['CUPS Gas'] = df_nc['CUPS Gas'].apply(clean_str_crm)
                            # Normalizar CUPs en la BASE COMPLETA (antes de cualquier filtro)
                            df_nc['luz_20'] = df_nc['CUPS Luz'].apply(n20) if 'CUPS Luz' in df_nc.columns else None
                            df_nc['gas_20'] = df_nc['CUPS Gas'].apply(n20) if 'CUPS Gas' in df_nc.columns else None
                            if 'Fecha Creación' in df_nc.columns:
                                df_nc['_mes'] = df_nc['Fecha Creación'].apply(mes_anio_n)

                            # Filtro por mes/año — solo afecta a lo mostrado en resultados
                            fechas_n = sorted([f for f in df_nc['_mes'].unique() if f], reverse=True) if '_mes' in df_nc.columns else []
                            sel_fn = st.multiselect(
                                "🗓️ Filtrar por mes/año de creación (puedes elegir varios):",
                                options=fechas_n,
                                default=[],
                                key="nat_fecha_sel",
                                placeholder="Sin filtro — mostrando todos los meses"
                            )
                            # df_nc_filtrado = vista filtrada para mostrar en KPIs/tabla
                            # df_nc = BASE COMPLETA para calcular cups_crm_all y el cruce
                            df_nc_vista = df_nc[df_nc['_mes'].isin(sel_fn)].copy() if (sel_fn and '_mes' in df_nc.columns) else df_nc.copy()

                            # ── Leer Naturgy ──
                            df_ne = leer_excel_safe(f_nat_ext, header=0)
                            df_ne.columns = [str(c).strip() for c in df_ne.columns]
                            for fc in ['responseDtm','fechaFirma','fechaUltimoCambioEstado']:
                                if fc in df_ne.columns: df_ne[fc] = df_ne[fc].apply(ffn)
                            if 'responseDtm' in df_ne.columns:
                                df_ne['Mes'] = df_ne['responseDtm'].apply(mes_anio_n)
                            # Excluir estados no válidos de Naturgy
                            ESTADOS_EXCLUIR_NAT = {'Pedidos incompletos', 'Por firmar', 'Scoring rechazado'}
                            if 'estado' in df_ne.columns:
                                df_ne = df_ne[~df_ne['estado'].isin(ESTADOS_EXCLUIR_NAT)].copy()

                            # Limpiar NIF y CUPs Naturgy (strip espacios inicio/final/intermedios)
                            def clean_str(x):
                                if x is None or str(x).strip() in ['nan','None','']: return None
                                # Eliminar espacios al inicio, final y espacios múltiples intermedios
                                return ' '.join(str(x).strip().split())

                            if 'nif' in df_ne.columns:
                                df_ne['nif'] = df_ne['nif'].apply(lambda x: clean_str(x) or '')
                            if 'idCupsEle' in df_ne.columns:
                                df_ne['idCupsEle'] = df_ne['idCupsEle'].apply(clean_str)
                            if 'idCupsGas' in df_ne.columns:
                                df_ne['idCupsGas'] = df_ne['idCupsGas'].apply(clean_str)
                            df_ne['cup_ele_20'] = df_ne['idCupsEle'].apply(n20) if 'idCupsEle' in df_ne.columns else None
                            df_ne['cup_gas_20'] = df_ne['idCupsGas'].apply(n20) if 'idCupsGas' in df_ne.columns else None

                            # cups_crm_all usa df_nc COMPLETO (todos los meses)
                            cups_crm_luz = set(df_nc['luz_20'].dropna()) if 'luz_20' in df_nc.columns else set()
                            cups_crm_gas = set(df_nc['gas_20'].dropna()) if 'gas_20' in df_nc.columns else set()
                            cups_crm_all = cups_crm_luz | cups_crm_gas

                            # ── Columnas CRM a incluir en el cruce ──
                            # Usar df_nc_vista (filtrado por fecha) para el merge de resultados
                            if 'Estado' in df_nc_vista.columns:
                                df_nc_vista = df_nc_vista.rename(columns={'Estado': 'Estado CRM'})
                            if 'Estado' in df_nc.columns:
                                df_nc = df_nc.rename(columns={'Estado': 'Estado CRM'})
                            cols_crm = [c for c in ['ID','Comercial','DNI Cliente','CUPS Luz','CUPS Gas','Estado CRM','Tarifa','Fecha Creación'] if c in df_nc_vista.columns]
                            cols_nat = [c for c in ['idCupsEle','idCupsGas','codigoVendedor','eleContratar','gasContratar','tarifaGas','tarifaEle','sveContratar','responseDtm','Mes','estado'] if c in df_ne.columns]

                            # ── CRUCE COMPLETO: usa df_nc_vista (filtrado por fecha) para mostrar ──
                            # pero cups_crm_all sigue siendo del df_nc completo (para Faltan en CRM)
                            df_crm_luz = df_nc_vista[df_nc_vista['luz_20'].notna()][cols_crm + ['luz_20']] if 'luz_20' in df_nc_vista.columns else pd.DataFrame()
                            df_ne_ele  = df_ne[df_ne['cup_ele_20'].notna()][cols_nat + ['cup_ele_20']]
                            df_m_luz = pd.merge(df_crm_luz, df_ne_ele,
                                                left_on='luz_20', right_on='cup_ele_20', how='inner') if not df_crm_luz.empty else pd.DataFrame()

                            ids_matched = set(df_m_luz['ID'].dropna()) if 'ID' in df_m_luz.columns and not df_m_luz.empty else set()
                            df_crm_gas_v = df_nc_vista[df_nc_vista['gas_20'].notna() & ~df_nc_vista['ID'].isin(ids_matched)][cols_crm + ['gas_20']] if 'gas_20' in df_nc_vista.columns else pd.DataFrame()
                            df_ne_gas  = df_ne[df_ne['cup_gas_20'].notna()][cols_nat + ['cup_gas_20']]
                            df_m_gas = pd.merge(df_crm_gas_v, df_ne_gas,
                                                left_on='gas_20', right_on='cup_gas_20', how='inner') if not df_crm_gas_v.empty else pd.DataFrame()

                            df_cruce = pd.concat([df_m_luz, df_m_gas], ignore_index=True)

                            # Filtrar df_cruce por Mes de Naturgy para que coincida con el filtro CRM
                            if sel_fn and 'Mes' in df_cruce.columns:
                                df_cruce = df_cruce[df_cruce['Mes'].isin(sel_fn)].copy()

                            # Renombrar a columnas de la plantilla
                            df_cruce_out = df_cruce.rename(columns={
                                'Comercial':        'Comercial (CONTRATOS CRM BASETTE)',
                                'idCupsEle':        'idCupsEle (EXPORTADO NATURGY)',
                                'idCupsGas':        'idCupsGas (EXPORTADO NATURGY)',
                                'codigoVendedor':   'Código Vendedor (EXPORTADO NATURGY)',
                                'eleContratar':     'Tarifa Ele (eleContratar)',
                                'gasContratar':     'Tarifa Gas (gasContratar)',
                                'tarifaGas':        'Detalle Tarifa Gas (tarifaGas)',
                                'tarifaEle':        'Detalle Tarifa Ele (tarifaEle)',
                                'sveContratar':     'Mantenimiento Ele (sveContratar)',
                                'responseDtm':      'Fecha (responseDtm)',
                                'estado':           'Estado Naturgy',
                                'Estado CRM':       'Estado CRM',
                            })
                            ord_out = [c for c in [
                                'Comercial (CONTRATOS CRM BASETTE)','idCupsEle (EXPORTADO NATURGY)',
                                'idCupsGas (EXPORTADO NATURGY)','Código Vendedor (EXPORTADO NATURGY)',
                                'Tarifa Ele (eleContratar)','Tarifa Gas (gasContratar)',
                                'Detalle Tarifa Gas (tarifaGas)','Detalle Tarifa Ele (tarifaEle)',
                                'Mantenimiento Ele (sveContratar)','Fecha (responseDtm)','Mes',
                                'Estado Naturgy','Estado CRM','DNI Cliente','CUPS Luz','CUPS Gas','Tarifa'
                            ] if c in df_cruce_out.columns]
                            # Eliminar duplicados de columna si los hubiera
                            seen = set()
                            ord_out = [c for c in ord_out if not (c in seen or seen.add(c))]
                            df_cruce_out = df_cruce_out[ord_out].reset_index(drop=True)

                            # ── FALTAN EN CONTRATOS CRM ──
                            # Naturgy rows cuyo CUP no está en nuestro CRM Naturgy
                            df_falta_crm = df_ne[
                                (~df_ne['cup_ele_20'].isin(cups_crm_all)) &
                                (~df_ne['cup_gas_20'].isin(cups_crm_all))
                            ].copy()
                            # Aplicar filtro de fecha también a "Faltan en CRM"
                            if sel_fn and 'Mes' in df_falta_crm.columns:
                                df_falta_crm = df_falta_crm[df_falta_crm['Mes'].isin(sel_fn)].copy()
                            # Posible Vendedor: codigoVendedor → Comercial mapeado desde el cruce
                            vendor_map = {}
                            for _, r in df_cruce.iterrows():
                                cv = str(r.get('codigoVendedor',''))
                                cm = str(r.get('Comercial',''))
                                if cv and cv not in ['nan','']: vendor_map[cv] = cm
                            if 'codigoVendedor' in df_falta_crm.columns:
                                df_falta_crm['Posible Vendedor'] = df_falta_crm['codigoVendedor'].apply(
                                    lambda x: vendor_map.get(str(x), 'No Encontrado'))
                            else:
                                df_falta_crm['Posible Vendedor'] = 'No Encontrado'
                            cols_fcrm = [c for c in ['Posible Vendedor','nif','nombre','idCupsEle','idCupsGas','codigoVendedor','eleContratar','gasContratar','estado','responseDtm','Mes'] if c in df_falta_crm.columns]
                            df_falta_crm_out = df_falta_crm[cols_fcrm].rename(columns={
                                'nif':            'DNI/NIF',
                                'nombre':         'Nombre Naturgy',
                                'codigoVendedor': 'Código Vendedor',
                                'eleContratar':   'Tarifa Ele',
                                'gasContratar':   'Tarifa Gas',
                                'estado':         'Estado Naturgy',
                                'responseDtm':    'Fecha (responseDtm)'
                            }).reset_index(drop=True)
                            df_falta_crm_out.insert(0, 'Comercial', 'No Encontrado')
                            # ── FALTAN EN EXPORTADO NATURGY ──
                            # CRM Naturgy contracts (del conjunto filtrado) cuyo CUP no está en Naturgy
                            cups_matched_luz = set(df_m_luz['luz_20'].dropna()) if not df_m_luz.empty else set()
                            cups_matched_gas = set(df_m_gas['gas_20'].dropna()) if not df_m_gas.empty else set()
                            _has_luz = 'luz_20' in df_nc_vista.columns
                            _has_gas = 'gas_20' in df_nc_vista.columns
                            df_falta_nat = df_nc_vista[
                                (~df_nc_vista['luz_20'].isin(cups_matched_luz) if _has_luz else True) &
                                (~df_nc_vista['gas_20'].isin(cups_matched_gas) if _has_gas else True)
                            ].copy()
                            # Código Vendedor Luz/Gas: buscar en Naturgy por CUP
                            cup_vendor = {}
                            for _, r in df_ne.iterrows():
                                if r.get('cup_ele_20'): cup_vendor[r['cup_ele_20']] = str(r.get('codigoVendedor','No Encontrado'))
                                if r.get('cup_gas_20'): cup_vendor[r['cup_gas_20']] = str(r.get('codigoVendedor','No Encontrado'))
                            df_falta_nat['Código Vendedor Luz'] = df_falta_nat['luz_20'].apply(
                                lambda c: cup_vendor.get(c, 'No Encontrado') if c else '-')
                            df_falta_nat['Código Vendedor Gas'] = df_falta_nat['gas_20'].apply(
                                lambda c: cup_vendor.get(c, 'No Encontrado') if c else '-')
                            df_falta_nat['Mes'] = df_falta_nat.get('Fecha Creación', pd.Series(dtype=str)).apply(mes_anio_n)
                            cols_fnat = [c for c in ['Comercial','DNI Cliente','CUPS Luz','CUPS Gas','Código Vendedor Luz','Código Vendedor Gas','Tarifa','Estado','Fecha Creación','Mes'] if c in df_falta_nat.columns]
                            df_falta_nat_out = df_falta_nat[cols_fnat].rename(
                                columns={'Fecha Creación': 'Fecha Creación (CRM)'}).reset_index(drop=True)

                            # ── KPIs ──
                            n_c = len(df_cruce_out); n_fc = len(df_falta_crm_out); n_fn = len(df_falta_nat_out)
                            n_vista = len(df_nc_vista)
                            n_total = len(df_nc)
                            st.markdown("---")
                            if sel_fn:
                                st.info(f"🗓️ Mostrando contratos de: {', '.join(sel_fn)} ({n_vista} de {n_total} contratos Naturgy)")
                            kn1, kn2, kn3, kn4 = st.columns(4)
                            bg = "border-radius:10px;padding:14px 8px;text-align:center;margin-bottom:10px;"
                            kn1.markdown(f'<div style="background:#f0fff4;border:2px solid #FFD700;{bg}"><p style="color:#FFD700;font-size:0.7rem;font-weight:bold;margin:0;">🔥 CRUCE COMPLETO</p><h2 style="color:#111111;margin:4px 0;">{n_c}</h2></div>', unsafe_allow_html=True)
                            kn2.markdown(f'<div style="background:#fff0f0;border:2px solid #ff4b4b;{bg}"><p style="color:#ff4b4b;font-size:0.7rem;font-weight:bold;margin:0;">❌ FALTAN EN CRM</p><h2 style="color:#111111;margin:4px 0;">{n_fc}</h2></div>', unsafe_allow_html=True)
                            kn3.markdown(f'<div style="background:#f8f0ff;border:2px solid #a78bfa;{bg}"><p style="color:#a78bfa;font-size:0.7rem;font-weight:bold;margin:0;">⚠️ FALTAN EN NATURGY</p><h2 style="color:#111111;margin:4px 0;">{n_fn}</h2></div>', unsafe_allow_html=True)
                            kn4.markdown(f'<div style="background:#ffffff;border:2px solid #8b949e;{bg}"><p style="color:#8b949e;font-size:0.7rem;font-weight:bold;margin:0;">📋 CRM {"(filtrado)" if sel_fn else "TOTAL"}</p><h2 style="color:#111111;margin:4px 0;">{n_vista}</h2></div>', unsafe_allow_html=True)

                            nt1, nt2, nt3 = st.tabs([
                                f"🔗 CRUCE COMPLETO ({n_c})",
                                f"❌ FALTAN EN CONTRATOS CRM ({n_fc})",
                                f"⚠️ FALTAN EN EXPORTADO NATURGY ({n_fn})"
                            ])

                            with nt1:
                                _nh1, _nb1 = st.columns([4,1])
                                with _nh1: st.markdown('<p style="color:#FFD700;font-size:0.83rem;margin:0;">CRM Naturgy cruzados con la extracción por CUP de luz o gas.</p>', unsafe_allow_html=True)
                                with _nb1: st.download_button("⬇️ Descargar",
                                    _safe({'Cruce Completo': df_cruce_out,
                                           'Faltan en CONTRATOS CRM': df_falta_crm_out,
                                           'Faltan en EXPORTADO NATURGY': df_falta_nat_out}),
                                    file_name="naturgy_cruce_completo.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True, key="dl_nt1")
                                st.dataframe(df_cruce_out, use_container_width=True, height=420)

                            with nt2:
                                _nh2, _nb2 = st.columns([4,1])
                                with _nh2: st.markdown('<p style="color:#ff4b4b;font-size:0.83rem;margin:0;">En Naturgy pero <b>ningún CUP en nuestro CRM</b>. Posible Vendedor estimado.</p>', unsafe_allow_html=True)
                                with _nb2: st.download_button("⬇️ Descargar",
                                    _safe({'Faltan en CONTRATOS CRM': df_falta_crm_out}),
                                    file_name="naturgy_faltan_en_crm.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True, key="dl_nt2")
                                st.dataframe(df_falta_crm_out, use_container_width=True, height=420)

                            with nt3:
                                _nh3, _nb3 = st.columns([4,1])
                                with _nh3: st.markdown('<p style="color:#a78bfa;font-size:0.83rem;margin:0;">Nuestros contratos Naturgy cuyo CUP <b>no aparece en la extracción</b>.</p>', unsafe_allow_html=True)
                                with _nb3: st.download_button("⬇️ Descargar",
                                    _safe({'Faltan en EXPORTADO NATURGY': df_falta_nat_out}),
                                    file_name="naturgy_faltan_en_extraccion.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True, key="dl_nt3")
                                st.dataframe(df_falta_nat_out, use_container_width=True, height=420)

                        except Exception as _en:
                            import traceback
                            st.error(f"❌ Error en cruce Naturgy: {_en}")
                            st.code(traceback.format_exc())
                else:
                    st.markdown('<div style="background:#f0f0f0;border:2px dashed #30363d;border-radius:12px;padding:30px;text-align:center;margin-top:10px;"><p style="color:#8b949e;margin:0;">👆 Sube el export CRM y la extracción de Naturgy para iniciar el cruce</p></div>', unsafe_allow_html=True)

        if _sel == "📁 DOCS EMPRESA":
            st.markdown('<div class="block-header">📁 DOCUMENTACIÓN DE EMPRESA</div>', unsafe_allow_html=True)
            st.markdown("""
                <div style="background:#ffffff; border-left:4px solid #FFD700; padding:15px; border-radius:8px; margin-bottom:20px;">
                    <p style="color:#8b949e; margin:0; font-size:0.85rem;">Escrituras, certificados, seguros, licencias y documentación oficial. Los archivos se leen desde Google Drive · Carpeta <b style="color:#FFD700;">EMPRESA</b></p>
                </div>
            """, unsafe_allow_html=True)
            col_doc1, col_doc2 = st.columns(2)
            with col_doc1:
                with st.expander("📬 Firmas Email Tecomparotodo"):
                    mostrar_carpeta_drive(["EMPRESA", "FIRMAS EMAIL TECOMPAROTODO"], "📬")
                with st.expander("🎓 Formación Inicial"):
                    mostrar_carpeta_drive(["EMPRESA", "FORMACION INICIAL"], "🎓")
                with st.expander("⚖️ CIF / CCC / Tarjetas Empresas"):
                    mostrar_carpeta_drive(["EMPRESA", "CIF CCC TARJETAS EMPRESAS"], "⚖️")
                with st.expander("🖼️ Logos"):
                    mostrar_carpeta_drive(["EMPRESA", "LOGOS"], "🖼️")
            with col_doc2:
                with st.expander("🛡️ Seguros (DNI CEO / BO)"):
                    mostrar_carpeta_drive(["EMPRESA", "DNI CEO BO"], "🛡️")
                with st.expander("🤝 Contrato de Colaboración Mercantil"):
                    # Es un Word suelto en la raíz de EMPRESA (no subcarpeta)
                    _emp_id = drive_folder_id_by_path(("EMPRESA",))
                    if _emp_id:
                        _emp_items = drive_list_folder(_emp_id)
                        _contratos = [f for f in _emp_items
                                      if f.get("mimeType") != "application/vnd.google-apps.folder"
                                      and "CONTRATO" in f.get("name","").upper()]
                        if _contratos:
                            for _cf in _contratos:
                                _mime = _cf.get("mimeType","")
                                if "document" in _mime:
                                    _curl = f"https://docs.google.com/document/d/{_cf['id']}/edit"
                                else:
                                    _curl = f"https://drive.google.com/file/d/{_cf['id']}/view"
                                _cc1, _cc2 = st.columns([5,1])
                                with _cc1:
                                    _sz = int(_cf.get("size",0))//1024
                                    st.markdown(f'<div style="background:#eef4fb;border:1px solid #c0d8ee;border-radius:8px;padding:8px 12px;">🤝 {_cf["name"]}{f" · {_sz} KB" if _sz else ""}</div>', unsafe_allow_html=True)
                                with _cc2:
                                    st.link_button("⬇️ Abrir", _curl, use_container_width=True)
                        else:
                            st.info("No se encontró el contrato. Comprueba el nombre en Drive.")
                    else:
                        st.warning("Carpeta EMPRESA no encontrada.")

        # ── TAB SOPORTE ──
        if _sel == "🛠️ SOPORTE":
            st.markdown('<div class="block-header">🛠️ SOPORTE Y HERRAMIENTAS</div>', unsafe_allow_html=True)

            def render_links_dir(lista, ncols=3):
                cols = st.columns(ncols)
                for i, p in enumerate(lista):
                    with cols[i % ncols]:
                        st.markdown(
                            f'<div style="background:#ffffff; padding:14px; border-radius:10px; '
                            f'border:1px solid #30363d; text-align:center; margin-bottom:10px;">'
                            f'<p style="color:#FFD700; font-size:1.1rem; margin:0;">{p.get("ico","🔗")}</p>'
                            f'<h4 style="color:#111111; margin:4px 0 0 0; font-size:0.9rem;">{p["n"]}</h4></div>',
                            unsafe_allow_html=True
                        )
                        st.link_button("ENTRAR", p["u"], use_container_width=True)

            st.markdown("##### 🖥️ Gestión y soporte")
            render_links_dir([
                {"n": "NODO",                    "u": "https://optimum.nodogestion.com/",                                                                                                             "ico": "🖥️"},
                {"n": "SUBIR DOCU TOTAL ENERGY", "u": "https://contrato.totalenergies.es/",                                                                                                          "ico": "📤"},
                {"n": "INFOJOBS",                "u": "https://www.infojobs.net/employer-login.xhtml",                                                                                               "ico": "💼"},
                {"n": "SAUC NATURGY",            "u": "https://sauc.gestdocout360.es/ServiceTonic/xhtml/portal/portal_home.jsf",                                                                    "ico": "🔧"},
                {"n": "LIQUIDACION TOTAL ENERGY","u": "https://ipbuestotalenergies-ipbuestotalenergiesprod.eu.cloud.varicent.com/payeewebv2/login?nextPathname=%2FPresenterAdaptive%2F67",           "ico": "💰"},
            ], ncols=3)

            st.markdown("---")
            st.markdown("##### 💡 Energía")
            render_links_dir([
                {"n": "CRM BASETTE",   "u": "https://crm.grupobasette.eu/login",                                                                                                                     "ico": "🏢"},
                {"n": "GANA ENERGÍA",  "u": "https://colaboradores.ganaenergia.com/",                                                                                                                "ico": "⚡"},
                {"n": "NATURGY",       "u": "https://checkout.naturgy.es/backoffice",                                                                                                                "ico": "🔥"},
                {"n": "TOTAL ENERGY",  "u": "https://totalenergiesespana.my.site.com/portalcolaboradores/s/login/?ec=302&startURL=%2Fportalcolaboradores%2Fs%2F",                                    "ico": "🌍"},
                {"n": "IBERDROLA",     "u": "https://crm.gesventas.eu/login.php",                                                                                                                    "ico": "💛"},
                {"n": "NIBA",          "u": "https://clientes.niba.es/",                                                                                                                             "ico": "🔵"},
                {"n": "ENDESA",        "u": "https://inergia.app",                                                                                                                                   "ico": "🔴"},
                {"n": "REPSOL",        "u": "https://inergia.app/login.php",                                                                                                                         "ico": "🛢️"},
            ], ncols=4)

            st.markdown("---")
            st.markdown("##### 🚨 Alarmas")
            render_links_dir([
                {"n": "SEGURMA", "u": "https://crm.segurma.com/web#action=619&cids=1&menu_id=200&model=sale.order&view_type=list", "ico": "🛡️"},
                {"n": "3D",      "u": "https://www.3dseguridad.es/reportes/menu.php",                                              "ico": "🔒"},
            ], ncols=3)

            st.markdown("---")
            st.markdown("##### 📶 Telecomunicaciones")
            render_links_dir([
                {"n": "O2",   "u": "https://o2online.es/auth/login/?next=%2Fventas%2F&type=retail", "ico": "📱"},
                {"n": "LOWI", "u": "https://vodafone.topgestion.es/login",                          "ico": "📡"},
            ], ncols=3)

            st.markdown("---")
            st.markdown("##### 📞 B2COM · Centralita")
            render_links_dir([
                {"n": "B2COM AGENTE",     "u": "https://grupobasette.vozipcenter.com/l/0/#/",                                                  "ico": "🎧"},
                {"n": "B2COM SUPERVISOR", "u": "https://grupobasette-super.vozipcenter.com/supervisor.html#/agentes",                          "ico": "👁️"},
                {"n": "B2COM ADMIN",      "u": "https://grupobasette-admin.vozipcenter.com/(X(9edb6d37-9516-4e3d-a150-1182e9197070))/",       "ico": "⚙️"},
                {"n": "B2COM PANEL",      "u": "https://pac.b2com.com/login",                                                                  "ico": "📊"},
            ], ncols=4)

            st.markdown("---")
            st.markdown("##### 🌐 RRSS y BBDD")
            render_links_dir([
                {"n": "IONOS", "u": "https://login.ionos.es/oauth-mandatorlogin?language=es_ES&redirect_url=https%3A%2F%2Fauth.ionos.es%2F1.0%2Foauth%2Fauth%2Fotk&oauthclient=Control+Panel+Webhosting&oauthinternal=true", "ico": "🌐"},
            ], ncols=3)

    # ══════════════════════════════════════════════════════
