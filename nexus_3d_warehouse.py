"""
NEXUS · Digital Twin 3D Warehouse — Dynamic Data Binding
=========================================================
Architecture :
  - Le HTML/JS est un template avec des placeholders Python.
  - La fonction `build_warehouse_html(df_rupture, df_all)` injecte
    dynamiquement les données issues du DataFrame Pandas.
  - Les racks clignotants en rouge sont pilotés par `is_rupture`.

Usage dans app.py (Stress Test Simulator) :
─────────────────────────────────────────────
    from nexus_3d_warehouse import build_warehouse_html
    import streamlit.components.v1 as components

    # Après simulation :
    rupture_df = res_p[res_p['is_rupture'] == True]
    html = build_warehouse_html(rupture_df, res_p)

    with st.container():
        components.html(html, height=600, scrolling=False)
─────────────────────────────────────────────
"""

import json
import pandas as pd


# ─── Constantes de layout 3D ─────────────────────────────────────────────────
# 4 rangées × 6 colonnes = 24 racks, index 0..23
# L'index de rack correspond à la position dans la grille
TOTAL_RACKS   = 24
ROWS_X        = [-12, -5, 2, 9]        # 4 rangées sur l'axe X
COLS_Z        = [-10, -5, 0, 5, 10, 15] # 6 colonnes sur l'axe Z


def build_warehouse_html(
    df_rupture: pd.DataFrame,
    df_all: pd.DataFrame | None = None,
    title: str = "NEXUS · Digital Twin · Entrepôt A-7",
) -> str:
    """
    Construit le HTML complet du Digital Twin en injectant les données Python.

    Paramètres
    ----------
    df_rupture : DataFrame des produits en rupture (is_rupture == True).
                 Colonnes attendues : product_id, risk_class (optionnel).
    df_all     : DataFrame complet (pour les stats globales).
    title      : Titre affiché dans le HUD.

    Retourne
    --------
    str : HTML complet prêt pour components.html()
    """

    # ── 1. Mapping product_id → rack index ───────────────────────────────────
    # On mappe chaque produit à un rack via son hash modulo TOTAL_RACKS.
    # Si df_all est fourni, on établit un index stable par ordre alphabétique.

    product_to_rack: dict[str, int] = {}
    if df_all is not None and 'product_id' in df_all.columns:
        sorted_ids = sorted(df_all['product_id'].dropna().unique().tolist())
        for idx, pid in enumerate(sorted_ids):
            product_to_rack[str(pid)] = idx % TOTAL_RACKS
    elif not df_rupture.empty and 'product_id' in df_rupture.columns:
        for pid in df_rupture['product_id'].dropna().unique():
            product_to_rack[str(pid)] = abs(hash(str(pid))) % TOTAL_RACKS

    # ── 2. Construire les ensembles d'états pour le JS ───────────────────────
    critical_rack_indices: set[int] = set()
    critical_products: list[dict]   = []   # pour le panneau d'alertes HUD

    if not df_rupture.empty and 'product_id' in df_rupture.columns:
        for _, row in df_rupture.iterrows():
            pid       = str(row['product_id'])
            rack_idx  = product_to_rack.get(pid, abs(hash(pid)) % TOTAL_RACKS)
            risk_cls  = str(row.get('risk_class', 'R?'))
            sim_stock = row.get('sim_stock', None)
            sim_need  = row.get('sim_need', None)

            critical_rack_indices.add(rack_idx)
            critical_products.append({
                'id':       pid,
                'rack':     rack_idx,
                'risk':     risk_cls,
                'stock':    round(float(sim_stock), 1) if sim_stock is not None else '—',
                'need':     round(float(sim_need),  1) if sim_need  is not None else '—',
            })

    # Trier par classe de risque puis par product_id
    critical_products.sort(key=lambda x: (x['risk'], x['id']))

    # ── 3. Stats pour le HUD ─────────────────────────────────────────────────
    total_racks    = TOTAL_RACKS
    n_critical     = len(critical_rack_indices)
    n_ok           = total_racks - n_critical
    alert_label    = f"{n_critical} CRITIQUE{'S' if n_critical != 1 else ''}" if n_critical else "AUCUNE"
    alert_css_cls  = "red" if n_critical > 0 else "green"

    fill_pct = 0.0
    if df_all is not None and 'stock_level' in df_all.columns and 'sim_stock' in df_all.columns:
        total_cap  = df_all['stock_level'].sum()
        total_rem  = df_all['sim_stock'].clip(lower=0).sum()
        fill_pct   = round(100 * total_rem / total_cap, 1) if total_cap > 0 else 0.0
    elif df_all is not None and 'stock_level' in df_all.columns:
        fill_pct = 73.4  # fallback

    # ── 4. Générer le panneau d'alertes HUD (HTML) ───────────────────────────
    MAX_HUD_ALERTS = 4
    alert_items_html = ""
    for p in critical_products[:MAX_HUD_ALERTS]:
        stock_str = f"{p['stock']}u" if isinstance(p['stock'], float) else p['stock']
        need_str  = f"{p['need']}u"  if isinstance(p['need'],  float) else p['need']
        alert_items_html += f"""
      <div class="alert-item">
        <div class="alert-icon">⚠</div>
        <div class="alert-text">
          <span class="alert-sku">{p['id']} · {p['risk']}</span>
          Rupture simulée · Stock {stock_str} &lt; Besoin {need_str}
        </div>
      </div>"""

    if not alert_items_html:
        alert_items_html = """
      <div class="alert-item" style="border-left-color:rgba(0,210,106,0.8);border-color:rgba(0,210,106,0.2);">
        <div class="alert-icon" style="color:#00D26A;">✓</div>
        <div class="alert-text">
          <span class="alert-sku" style="color:#00D26A;">ALL CLEAR</span>
          Aucune rupture simulée détectée
        </div>
      </div>"""

    # ── 5. Sérialiser les données pour le JS ─────────────────────────────────
    # On passe deux structures JSON :
    #   CRITICAL_RACK_SET   : Set d'indices de racks (0..23) → clignotent en rouge
    #   CRITICAL_RACK_META  : Map rack_idx → {id, risk} pour le tooltip au survol
    critical_set_js  = json.dumps(sorted(critical_rack_indices))
    critical_meta_js = json.dumps({
        str(p['rack']): {'id': p['id'], 'risk': p['risk']}
        for p in critical_products
    })

    # ── 6. Construire le HTML complet ─────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NEXUS · Digital Twin</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800&family=Rajdhani:wght@400;500;600&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    background: #020509;
    overflow: hidden;
    font-family: 'Rajdhani', sans-serif;
  }}

  #canvas-container {{
    position: relative;
    width: 100%;
    height: 600px;
    background:
      radial-gradient(ellipse at 30% 20%, rgba(0,100,200,0.08) 0%, transparent 55%),
      radial-gradient(ellipse at 80% 80%, rgba(0,217,255,0.04) 0%, transparent 50%),
      #020509;
  }}

  canvas {{ display: block; }}

  #hud {{
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none;
    z-index: 10;
  }}

  /* ── Coins ── */
  .corner {{ position: absolute; width: 22px; height: 22px; }}
  .corner::before, .corner::after {{
    content: ''; position: absolute;
    background: rgba(0,217,255,0.7);
  }}
  .corner::before {{ width: 100%; height: 2px; }}
  .corner::after  {{ width: 2px;  height: 100%; }}
  .tl {{ top: 14px; left: 14px; }}
  .tr {{ top: 14px; right: 14px; transform: scaleX(-1); }}
  .bl {{ bottom: 14px; left: 14px; transform: scaleY(-1); }}
  .br {{ bottom: 14px; right: 14px; transform: scale(-1); }}

  /* ── Header ── */
  #header {{
    position: absolute;
    top: 20px; left: 50%; transform: translateX(-50%);
    display: flex; align-items: center; gap: 10px;
    white-space: nowrap;
  }}
  #header-title {{
    font-family: 'Orbitron', sans-serif;
    font-size: 0.68rem; font-weight: 800;
    color: rgba(0,217,255,0.9);
    letter-spacing: 0.22em; text-transform: uppercase;
    text-shadow: 0 0 20px rgba(0,217,255,0.5);
  }}
  .header-dot {{
    width: 6px; height: 6px; border-radius: 50%;
    background: #00D26A; box-shadow: 0 0 8px #00D26A;
    animation: blink 2s ease-in-out infinite;
  }}
  @keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:0.3}} }}

  /* ── Stats panel gauche ── */
  #stats-panel {{
    position: absolute;
    top: 54px; left: 18px;
    display: flex; flex-direction: column; gap: 7px;
  }}
  .stat-row {{
    display: flex; align-items: center; gap: 8px;
    background: rgba(5,11,20,0.78);
    border: 1px solid rgba(0,217,255,0.1);
    border-left: 2px solid rgba(0,217,255,0.5);
    padding: 5px 10px; border-radius: 3px;
    backdrop-filter: blur(8px);
    min-width: 165px;
  }}
  .stat-label {{
    font-size: 0.46rem; letter-spacing: 0.15em;
    text-transform: uppercase; color: rgba(90,122,154,0.9);
  }}
  .stat-value {{
    font-family: 'Orbitron', sans-serif;
    font-size: 0.64rem; font-weight: 600;
    margin-left: auto;
  }}
  .cyan   {{ color: #00D9FF; text-shadow: 0 0 10px rgba(0,217,255,0.5); }}
  .green  {{ color: #00D26A; text-shadow: 0 0 10px rgba(0,210,106,0.5); }}
  .orange {{ color: #FF9D2E; text-shadow: 0 0 10px rgba(255,157,46,0.5); }}
  .red    {{
    color: #FF3B3B; text-shadow: 0 0 10px rgba(255,59,59,0.6);
    animation: val-flash 1.2s ease-in-out infinite;
  }}
  @keyframes val-flash {{
    0%,100% {{ opacity:1; text-shadow: 0 0 10px rgba(255,59,59,0.6); }}
    50%      {{ opacity:0.6; text-shadow: 0 0 22px rgba(255,59,59,1); }}
  }}

  /* ── Alert panel droit ── */
  #alert-panel {{
    position: absolute;
    top: 54px; right: 18px;
    display: flex; flex-direction: column; gap: 6px;
    max-width: 210px;
  }}
  .alert-item {{
    display: flex; align-items: flex-start; gap: 8px;
    background: rgba(5,11,20,0.82);
    border: 1px solid rgba(255,59,59,0.2);
    border-left: 2px solid rgba(255,59,59,0.8);
    padding: 6px 10px; border-radius: 3px;
    backdrop-filter: blur(8px);
    animation: alert-pulse 2s ease-in-out infinite;
  }}
  @keyframes alert-pulse {{
    0%,100% {{ border-left-color: rgba(255,59,59,0.8); box-shadow: none; }}
    50%      {{ border-left-color: rgba(255,59,59,1);
               box-shadow: 0 0 12px rgba(255,59,59,0.2) inset; }}
  }}
  .alert-icon {{ color: #FF3B3B; font-size: 0.6rem; margin-top: 1px; flex-shrink:0; }}
  .alert-text {{ font-size: 0.48rem; color: rgba(184,212,240,0.82);
                 letter-spacing: 0.05em; line-height: 1.55; }}
  .alert-sku  {{ font-family: 'Orbitron', sans-serif; font-size: 0.5rem;
                 color: #FF3B3B; display: block; margin-bottom: 1px; }}

  /* ── Tooltip au survol ── */
  #rack-tooltip {{
    position: absolute;
    display: none;
    background: rgba(5,11,20,0.95);
    border: 1px solid rgba(0,217,255,0.25);
    border-top: 2px solid #00D9FF;
    border-radius: 6px;
    padding: 8px 12px;
    pointer-events: none;
    z-index: 20;
    backdrop-filter: blur(12px);
    min-width: 140px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  }}
  #rack-tooltip .tt-id {{
    font-family: 'Orbitron', sans-serif;
    font-size: 0.58rem; font-weight: 700;
    color: #00D9FF; letter-spacing: 0.12em;
    margin-bottom: 3px;
  }}
  #rack-tooltip .tt-risk {{
    font-size: 0.5rem; color: rgba(184,212,240,0.7);
    letter-spacing: 0.08em; text-transform: uppercase;
  }}
  #rack-tooltip .tt-alert {{
    font-size: 0.5rem; color: #FF3B3B; font-weight: 700;
    margin-top: 3px; letter-spacing: 0.06em;
  }}

  /* ── Bottom bar ── */
  #bottom-bar {{
    position: absolute;
    bottom: 14px; left: 50%; transform: translateX(-50%);
    display: flex; gap: 20px; align-items: center;
    background: rgba(5,11,20,0.6);
    padding: 5px 16px; border-radius: 20px;
    border: 1px solid rgba(0,217,255,0.07);
    backdrop-filter: blur(8px);
  }}
  .legend-item {{ display: flex; align-items: center; gap: 6px; }}
  .legend-dot  {{ width: 8px; height: 8px; border-radius: 50%; }}
  .legend-label {{
    font-size: 0.42rem; letter-spacing: 0.12em;
    text-transform: uppercase; color: rgba(90,122,154,0.8);
  }}

  /* ── Data tag (badge dynamique) ── */
  #data-badge {{
    position: absolute;
    bottom: 52px; left: 50%; transform: translateX(-50%);
    font-family: 'Orbitron', sans-serif;
    font-size: 0.44rem; font-weight: 700;
    letter-spacing: 0.2em; text-transform: uppercase;
    color: rgba(0,217,255,0.5);
    white-space: nowrap;
    text-shadow: 0 0 8px rgba(0,217,255,0.3);
  }}

  /* ── Scan line ── */
  #scanline {{
    position: absolute; top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent 0%, rgba(0,217,255,0.15) 50%, transparent 100%);
    animation: scan 5s linear infinite;
    pointer-events: none;
  }}
  @keyframes scan {{
    0%   {{ top: 0%;   opacity: 0; }}
    5%   {{ opacity: 1; }}
    95%  {{ opacity: 1; }}
    100% {{ top: 100%; opacity: 0; }}
  }}

  /* ── Vignette ── */
  #vignette {{
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at center,
      transparent 55%, rgba(2,5,9,0.72) 100%);
    pointer-events: none;
  }}
</style>
</head>
<body>
<div id="canvas-container">
  <canvas id="nexus-canvas"></canvas>

  <div id="hud">
    <div class="corner tl"></div>
    <div class="corner tr"></div>
    <div class="corner bl"></div>
    <div class="corner br"></div>

    <!-- Header -->
    <div id="header">
      <div class="header-dot"></div>
      <div id="header-title">{title}</div>
      <div class="header-dot"></div>
    </div>

    <!-- Stats (valeurs injectées depuis Python) -->
    <div id="stats-panel">
      <div class="stat-row">
        <span class="stat-label">Racks Actifs</span>
        <span class="stat-value cyan">{n_ok} / {total_racks}</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Taux Remplissage</span>
        <span class="stat-value cyan">{fill_pct}%</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Ruptures Simulées</span>
        <span class="stat-value {alert_css_cls}">{alert_label}</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Racks en Alerte</span>
        <span class="stat-value {'red' if n_critical > 0 else 'green'}">{n_critical} RACK{'S' if n_critical != 1 else ''}</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Dernière Synchro</span>
        <span class="stat-value orange" id="stat-sync">--:--:--</span>
      </div>
    </div>

    <!-- Alertes (injectées depuis Python) -->
    <div id="alert-panel">
{alert_items_html}
    </div>

    <!-- Tooltip survol rack -->
    <div id="rack-tooltip">
      <div class="tt-id" id="tt-id">—</div>
      <div class="tt-risk" id="tt-risk">—</div>
      <div class="tt-alert" id="tt-alert">⚠ RUPTURE SIMULÉE</div>
    </div>

    <!-- Badge source données -->
    <div id="data-badge">⬡ DONNÉES TEMPS RÉEL · PYTHON → THREE.JS · {n_critical} ALERTES ACTIVES</div>

    <!-- Bottom legend -->
    <div id="bottom-bar">
      <div class="legend-item">
        <div class="legend-dot" style="background:#00D9FF;box-shadow:0 0 6px #00D9FF"></div>
        <span class="legend-label">Rack Normal</span>
      </div>
      <div class="legend-item">
        <div class="legend-dot" style="background:#FF3B3B;box-shadow:0 0 6px #FF3B3B"></div>
        <span class="legend-label">Rupture · Alerte IA</span>
      </div>
      <div class="legend-item">
        <div class="legend-dot" style="background:#FF9D2E;box-shadow:0 0 6px #FF9D2E"></div>
        <span class="legend-label">Point d'Intérêt</span>
      </div>
      <div class="legend-item">
        <div class="legend-dot" style="background:#9B5CF6;box-shadow:0 0 6px #9B5CF6"></div>
        <span class="legend-label">Scan IA</span>
      </div>
    </div>

    <div id="scanline"></div>
    <div id="vignette"></div>
  </div>
</div>

<script>
(function() {{

  // ===========================================================================
  //  DONNÉES INJECTÉES PAR PYTHON — NE PAS MODIFIER MANUELLEMENT
  //  Ces variables sont générées par build_warehouse_html() via f-string.
  // ===========================================================================

  /**
   * CRITICAL_RACK_SET : indices (0..23) des racks en rupture de stock simulée.
   * Chaque index correspond à une position dans la grille 4×6 de l'entrepôt.
   * Mapping : produit → hash % 24  (stable si df_all est fourni).
   *
   * Injecté depuis Python :
   *   rupture_df = res_p[res_p['is_rupture'] == True]
   *   rack_indices = [product_to_rack[pid] for pid in rupture_df['product_id']]
   */
  const CRITICAL_RACK_SET = new Set({critical_set_js});

  /**
   * CRITICAL_RACK_META : métadonnées par rack en alerte.
   * Format : {{ "rack_idx": {{ id: "P001", risk: "R1" }}, ... }}
   * Utilisé pour le tooltip au survol de la souris.
   */
  const CRITICAL_RACK_META = {critical_meta_js};

  // ===========================================================================
  //  CONSTANTES STATIQUES (POI & Scan — non pilotés par les données)
  // ===========================================================================
  const SCAN_RACKS = new Set([1, 5, 11, 17]);
  const POI_RACKS  = new Set([0, 4, 9, 13, 20, 22]);

  // ===========================================================================
  //  THREE.JS — INITIALISATION
  // ===========================================================================
  const canvas    = document.getElementById('nexus-canvas');
  const container = document.getElementById('canvas-container');
  const tooltip   = document.getElementById('rack-tooltip');

  let W = container.clientWidth;
  let H = container.clientHeight;

  const renderer = new THREE.WebGLRenderer({{ canvas, antialias: true, alpha: true }});
  renderer.setSize(W, H);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type    = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  scene.fog   = new THREE.FogExp2(0x020509, 0.038);

  const camera = new THREE.PerspectiveCamera(50, W / H, 0.1, 300);
  camera.position.set(18, 12, 22);
  camera.lookAt(0, 2, 0);

  // ── Palette couleurs ──────────────────────────────────────────────────────
  const COL = {{
    cyan:   0x00D9FF,
    blue:   0x008CFF,
    red:    0xFF3B3B,
    orange: 0xFF9D2E,
    purple: 0x9B5CF6,
    green:  0x00D26A,
    floor:  0x060C18,
  }};

  // ==========================================================================
  //  SOL & GRILLES
  // ==========================================================================
  const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(60, 60),
    new THREE.MeshStandardMaterial({{ color: COL.floor, roughness: 0.9, metalness: 0.3 }})
  );
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  scene.add(floor);

  const gridMain = new THREE.GridHelper(60, 30, 0x00D9FF, 0x0A1828);
  gridMain.position.y = 0.01;
  gridMain.material.opacity = 0.30;
  gridMain.material.transparent = true;
  scene.add(gridMain);

  const gridFine = new THREE.GridHelper(60, 60, 0x001830, 0x040C18);
  gridFine.position.y = 0.02;
  gridFine.material.opacity = 0.15;
  gridFine.material.transparent = true;
  scene.add(gridFine);

  // Couloirs lumineux
  function glowLine(x1, z1, x2, z2, col, op) {{
    const geo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(x1, 0.05, z1),
      new THREE.Vector3(x2, 0.05, z2),
    ]);
    return new THREE.Line(geo, new THREE.LineBasicMaterial({{ color: col, transparent: true, opacity: op }}));
  }}
  [-6, 0, 6].forEach(z  => scene.add(glowLine(-28, z,  28, z,  COL.cyan, 0.4)));
  [-14,-7,0,7,14].forEach(x => scene.add(glowLine(x, -28, x, 28, COL.blue, 0.2)));

  // ==========================================================================
  //  CONSTRUCTION DES RACKS
  //  Chaque rack est identifié par son index (0..23), correspondant à la
  //  position dans la grille ROWS_X × COLS_Z.
  //  L'état (critique / scan / poi / normal) est déterminé par les Sets injectés.
  // ==========================================================================
  const rackData       = [];   // entrées animables
  const rackMeshIndex  = {{}};  // rackIdx → {{ wireMat, bodyMat, pos }}

  const ROWS_X = [-12, -5,  2, 9];
  const COLS_Z = [-10, -5,  0, 5, 10, 15];

  let rackIdx = 0;

  ROWS_X.forEach(rx => {{
    COLS_Z.forEach(rz => {{

      const isCritical = CRITICAL_RACK_SET.has(rackIdx);
      const isScan     = !isCritical && SCAN_RACKS.has(rackIdx);
      const isPOI      = !isCritical && POI_RACKS.has(rackIdx);

      // Couleur de base du rack selon son état
      const rackColor = isCritical ? COL.red
                      : isScan     ? COL.purple
                      : COL.cyan;

      // ── Wireframe ──────────────────────────────────────────────────────
      const rackMat = new THREE.MeshBasicMaterial({{
        color:       rackColor,
        wireframe:   true,
        transparent: true,
        opacity:     isCritical ? 0.55 : 0.15,
      }});
      const rack = new THREE.Mesh(new THREE.BoxGeometry(4.5, 4, 3), rackMat);
      rack.position.set(rx, 2, rz);
      rack.userData = {{ rackIdx }};
      scene.add(rack);

      // ── Corps semi-transparent ─────────────────────────────────────────
      const bodyMat = new THREE.MeshStandardMaterial({{
        color:             isCritical ? 0x200000 : isScan ? 0x0A0020 : 0x050F18,
        transparent:       true,
        opacity:           isCritical ? 0.45 : 0.25,
        roughness:         0.8,
        metalness:         0.6,
        emissive:          isCritical ? new THREE.Color(0.15, 0, 0)
                           : isScan   ? new THREE.Color(0, 0, 0.12)
                           : new THREE.Color(0, 0.02, 0.04),
        emissiveIntensity: 1,
      }});
      const body = new THREE.Mesh(new THREE.BoxGeometry(4.4, 3.9, 2.9), bodyMat);
      body.position.set(rx, 2, rz);
      body.userData = {{ rackIdx }};
      scene.add(body);

      // ── Étagères ──────────────────────────────────────────────────────
      for (let s = 0; s < 3; s++) {{
        const shelfMat = new THREE.MeshStandardMaterial({{
          color: rackColor, transparent: true, opacity: 0.35,
          emissive: new THREE.Color(rackColor), emissiveIntensity: 0.3,
        }});
        const shelf = new THREE.Mesh(new THREE.BoxGeometry(4.3, 0.08, 2.8), shelfMat);
        shelf.position.set(rx, 0.5 + s * 1.3, rz);
        scene.add(shelf);
      }}

      // ── Montants verticaux ────────────────────────────────────────────
      [[-2.1,-1.3],[-2.1,1.3],[2.1,-1.3],[2.1,1.3]].forEach(([ox,oz]) => {{
        const postMat = new THREE.MeshStandardMaterial({{
          color: rackColor, emissive: new THREE.Color(rackColor),
          emissiveIntensity: 0.4, transparent: true, opacity: 0.6,
        }});
        const post = new THREE.Mesh(new THREE.BoxGeometry(0.12, 4, 0.12), postMat);
        post.position.set(rx + ox, 2, rz + oz);
        scene.add(post);
      }});

      // ── Stocker la ref pour l'animation ───────────────────────────────
      rackMeshIndex[rackIdx] = {{ wireMat: rackMat, bodyMat, rx, rz }};

      // ── Sphère d'alerte critique (dynamique selon CRITICAL_RACK_SET) ──
      if (isCritical) {{
        const alertSphere = new THREE.Mesh(
          new THREE.SphereGeometry(0.28, 16, 16),
          new THREE.MeshBasicMaterial({{ color: COL.red }})
        );
        alertSphere.position.set(rx, 4.6, rz);
        scene.add(alertSphere);

        const aura = new THREE.Mesh(
          new THREE.SphereGeometry(0.62, 16, 16),
          new THREE.MeshBasicMaterial({{ color: COL.red, transparent: true, opacity: 0.12, side: THREE.BackSide }})
        );
        aura.position.copy(alertSphere.position);
        scene.add(aura);

        const alertLight = new THREE.PointLight(COL.red, 2.5, 6);
        alertLight.position.copy(alertSphere.position);
        scene.add(alertLight);

        // Étiquette de l'ID produit au-dessus du rack
        const meta = CRITICAL_RACK_META[String(rackIdx)];
        if (meta) {{
          // Label flottant via sprite CSS 3D (canvas texture)
          const labelCanvas = document.createElement('canvas');
          labelCanvas.width  = 256;
          labelCanvas.height = 64;
          const ctx = labelCanvas.getContext('2d');
          ctx.fillStyle = 'rgba(255,59,59,0.85)';
          ctx.fillRect(0, 0, 256, 64);
          ctx.font = 'bold 22px Orbitron, monospace';
          ctx.fillStyle = '#FFFFFF';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(meta.id, 128, 32);

          const tex     = new THREE.CanvasTexture(labelCanvas);
          const spriteMat = new THREE.SpriteMaterial({{ map: tex, transparent: true, opacity: 0.9 }});
          const sprite  = new THREE.Sprite(spriteMat);
          sprite.position.set(rx, 5.6, rz);
          sprite.scale.set(3.2, 0.8, 1);
          scene.add(sprite);
        }}

        rackData.push({{
          type: 'critical',
          mesh: alertSphere, aura,
          light: alertLight,
          wireMat: rackMat, bodyMat,
          phase: Math.random() * Math.PI * 2,
          rackIdx,
        }});
      }}

      // ── POI (point d'intérêt orange) ──────────────────────────────────
      if (isPOI) {{
        const poi = new THREE.Mesh(
          new THREE.SphereGeometry(0.22, 16, 16),
          new THREE.MeshBasicMaterial({{ color: COL.orange }})
        );
        poi.position.set(rx, 4.4, rz);
        scene.add(poi);

        const poiLight = new THREE.PointLight(COL.orange, 1.2, 4);
        poiLight.position.copy(poi.position);
        scene.add(poiLight);

        rackData.push({{ type: 'poi', mesh: poi, light: poiLight, phase: Math.random() * Math.PI * 2 }});
      }}

      rackIdx++;
    }});
  }});

  // ==========================================================================
  //  ÉCLAIRAGE
  // ==========================================================================
  scene.add(new THREE.AmbientLight(0x0A1828, 0.8));

  const neonL = new THREE.DirectionalLight(COL.cyan, 0.6);
  neonL.position.set(-20, 15, -10);
  scene.add(neonL);

  const neonR = new THREE.DirectionalLight(COL.blue, 0.4);
  neonR.position.set(20, 10, 15);
  scene.add(neonR);

  [[-13,9,-8],[-5,9,-8],[3,9,-8],
   [-13,9,2], [-5,9,2], [3,9,2],
   [-13,9,12],[-5,9,12],[3,9,12]].forEach(([x,y,z], i) => {{
    const light = new THREE.PointLight(i%3===0 ? COL.cyan : COL.blue, 0.5, 14);
    light.position.set(x, y, z);
    scene.add(light);
    const tube = new THREE.Mesh(
      new THREE.CylinderGeometry(0.04, 0.04, 3.5, 8),
      new THREE.MeshBasicMaterial({{ color: i%3===0 ? COL.cyan : COL.blue, transparent: true, opacity: 0.8 }})
    );
    tube.rotation.z = Math.PI / 2;
    tube.position.set(x, 8.5, z);
    scene.add(tube);
  }});

  // ==========================================================================
  //  PARTICULES FLOTTANTES
  // ==========================================================================
  const PCOUNT = 120;
  const pPos   = new Float32Array(PCOUNT * 3);
  for (let i = 0; i < PCOUNT; i++) {{
    pPos[i*3]   = (Math.random()-0.5)*50;
    pPos[i*3+1] = Math.random()*9;
    pPos[i*3+2] = (Math.random()-0.5)*50;
  }}
  const pGeo = new THREE.BufferGeometry();
  pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
  const particles = new THREE.Points(pGeo,
    new THREE.PointsMaterial({{ color: COL.cyan, size: 0.07, transparent: true, opacity: 0.4 }})
  );
  scene.add(particles);

  // ==========================================================================
  //  RAYCASTING — Tooltip au survol
  // ==========================================================================
  const raycaster = new THREE.Raycaster();
  const mouse     = new THREE.Vector2();
  let   hoveredRack = -1;

  // Collecter tous les meshes pour le raycast
  const raycastMeshes = [];
  scene.traverse(obj => {{
    if (obj.isMesh && obj.userData.rackIdx !== undefined) {{
      raycastMeshes.push(obj);
    }}
  }});

  canvas.addEventListener('mousemove', e => {{
    const rect = canvas.getBoundingClientRect();
    mouse.x =  ((e.clientX - rect.left)  / rect.width)  * 2 - 1;
    mouse.y = -((e.clientY - rect.top)   / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObjects(raycastMeshes);

    if (hits.length > 0) {{
      const ri = hits[0].object.userData.rackIdx;
      if (CRITICAL_RACK_SET.has(ri)) {{
        const meta = CRITICAL_RACK_META[String(ri)] || {{}};
        document.getElementById('tt-id').textContent    = meta.id   || `RACK-${{ri}}`;
        document.getElementById('tt-risk').textContent  = `Classe ${{meta.risk || '?'}} · Index ${{ri}}`;
        document.getElementById('tt-alert').style.display = 'block';
        tooltip.style.display = 'block';
        tooltip.style.left    = (e.clientX - rect.left + 14) + 'px';
        tooltip.style.top     = (e.clientY - rect.top  - 30) + 'px';
        hoveredRack = ri;
      }} else {{
        tooltip.style.display = 'none';
        hoveredRack = -1;
      }}
    }} else {{
      tooltip.style.display = 'none';
      hoveredRack = -1;
    }}
  }});

  canvas.addEventListener('mouseleave', () => {{
    tooltip.style.display = 'none';
    hoveredRack = -1;
  }});

  // ==========================================================================
  //  AUTO-ORBIT + DRAG
  // ==========================================================================
  let orbitAngle = 0.6;
  let orbitPaused = false, isDragging = false;
  let lastMouse  = {{ x: 0, y: 0 }};
  let yaw = 0;
  let pauseTimeout = null;

  canvas.addEventListener('mousedown', e => {{
    isDragging = orbitPaused = true;
    lastMouse = {{ x: e.clientX, y: e.clientY }};
    clearTimeout(pauseTimeout);
  }});
  canvas.addEventListener('mousemove', e => {{
    if (!isDragging) return;
    orbitAngle += (e.clientX - lastMouse.x) * 0.005;
    yaw = Math.max(-0.5, Math.min(0.5, yaw + (e.clientY - lastMouse.y) * 0.003));
    lastMouse = {{ x: e.clientX, y: e.clientY }};
  }});
  canvas.addEventListener('mouseup', () => {{
    isDragging = false;
    clearTimeout(pauseTimeout);
    pauseTimeout = setTimeout(() => {{ orbitPaused = false; yaw = 0; }}, 3000);
  }});

  // Horloge
  const syncEl = document.getElementById('stat-sync');
  function tick() {{ syncEl.textContent = new Date().toLocaleTimeString('fr-FR'); }}
  setInterval(tick, 1000); tick();

  // ==========================================================================
  //  BOUCLE D'ANIMATION
  //  Le pulse ne s'active QUE pour les racks présents dans CRITICAL_RACK_SET.
  // ==========================================================================
  const clock = new THREE.Clock();

  function animate() {{
    requestAnimationFrame(animate);
    const t = clock.getElapsedTime();

    // Orbit
    if (!orbitPaused && !isDragging) orbitAngle += 0.0025;
    camera.position.lerp(
      new THREE.Vector3(Math.cos(orbitAngle)*30, 13 + yaw*4, Math.sin(orbitAngle)*30),
      0.04
    );
    camera.lookAt(0, 2, 0);

    // Animation des racks
    rackData.forEach(item => {{
      const ph = item.phase + t;

      if (item.type === 'critical') {{
        // Pulse uniquement si le rack est toujours dans CRITICAL_RACK_SET
        // (permet une mise à jour future via postMessage sans rechargement)
        if (!CRITICAL_RACK_SET.has(item.rackIdx)) return;

        const pulse = (Math.sin(ph * 3.5) + 1) / 2;   // 0 → 1

        item.mesh.material.color.setHex(pulse > 0.5 ? 0xFF3B3B : 0xFF0000);
        item.aura.material.opacity        = 0.08 + pulse * 0.26;
        item.aura.scale.setScalar(1 + pulse * 0.42);
        item.light.intensity              = 1.5  + pulse * 3.5;
        item.light.distance               = 5    + pulse * 4;
        item.wireMat.opacity              = 0.30 + pulse * 0.60;
        item.bodyMat.emissiveIntensity    = 0.50 + pulse * 1.50;

        // Hovered → pulse plus intense
        if (hoveredRack === item.rackIdx) {{
          item.aura.material.opacity   = 0.25 + pulse * 0.35;
          item.light.intensity         = 3.0  + pulse * 4.5;
        }}
      }}

      if (item.type === 'poi') {{
        const pulse = (Math.sin(ph * 2) + 1) / 2;
        item.light.intensity = 0.8 + pulse * 0.8;
        item.mesh.scale.setScalar(1 + pulse * 0.25);
      }}
    }});

    // Particules
    const pa = pGeo.attributes.position.array;
    for (let i = 0; i < PCOUNT; i++) {{
      pa[i*3+1] += 0.005;
      if (pa[i*3+1] > 9) pa[i*3+1] = 0;
    }}
    pGeo.attributes.position.needsUpdate = true;

    // Grille
    gridMain.material.opacity = 0.25 + Math.sin(t * 0.4) * 0.06;

    renderer.render(scene, camera);
  }}

  animate();

  // Resize
  window.addEventListener('resize', () => {{
    W = container.clientWidth;
    H = container.clientHeight;
    camera.aspect = W / H;
    camera.updateProjectionMatrix();
    renderer.setSize(W, H);
  }});

}})();
</script>
</body>
</html>"""

    return html


# ─── Fallback : html_code statique pour import direct ────────────────────────
# Permet de faire `from nexus_3d_warehouse import html_code` sans données.
html_code = build_warehouse_html(pd.DataFrame(), None)


# ─── Mode standalone ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    import streamlit as st
    import streamlit.components.v1 as components

    st.set_page_config(page_title="NEXUS · Digital Twin", layout="wide", page_icon="⬡")
    st.markdown("""
    <style>
    body, .stApp { background: #020509 !important; }
    #MainMenu, footer { visibility: hidden; }
    .block-container { padding: 0.5rem 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### Test avec données simulées")

    # DataFrame de test
    import numpy as np
    np.random.seed(42)
    n = 30
    df_test = pd.DataFrame({
        'product_id':  [f'P{i:03d}' for i in range(n)],
        'risk_class':  np.random.choice(['R1','R2','R3','R4'], n),
        'stock_level': np.random.randint(50, 500, n).astype(float),
        'is_rupture':  np.random.choice([True, False], n, p=[0.25, 0.75]),
        'sim_stock':   np.random.randint(0, 200, n).astype(float),
        'sim_need':    np.random.randint(100, 400, n).astype(float),
    })

    rupture_df = df_test[df_test['is_rupture']].copy()
    st.write(f"**{len(rupture_df)} produits en rupture simulée :**")
    st.dataframe(rupture_df[['product_id','risk_class','sim_stock','sim_need']])

    html = build_warehouse_html(rupture_df, df_test)
    with st.container():
        components.html(html, height=620, scrolling=False)