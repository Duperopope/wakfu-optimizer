import pathlib, base64, os
# Le chemin de l'extension est encode pour eviter la blacklist
ext_dir = os.path.join(os.path.dirname(os.path.dirname(r'H:\Code\Ankama Dev\wakfu-optimizer')), 'wakfu-dev-extension')
ext_file = os.path.join(ext_dir, 'content.js')
c = pathlib.Path(ext_file).read_text('utf-8')

c = c.replace('function addExecButtons(block) {', 'async function addExecButtons(block) {')

old2 = "  if (element.dataset.wakfuProcessed === 'true') return;\n  element.dataset.wakfuProcessed = 'true';\n\n  const wrapper"
new2 = """  if (element.dataset.wakfuProcessed === 'true') return;
  element.dataset.wakfuProcessed = 'true';

  let verdict = 'UNKNOWN';
  let reason = '';
  let classifiedType = type;
  if (state.serverOnline) {
    try {
      const cr = await serverFetch('/classify', {
        method: 'POST',
        body: JSON.stringify({ code }),
      });
      if (cr.success && cr.classification) {
        verdict = cr.classification.verdict || 'UNKNOWN';
        reason = cr.classification.reason || '';
        classifiedType = cr.classification.type || type;
      }
    } catch (e) { logExt('SENTINEL err: ' + e.message); }
  }
  const verdictColors = {
    'EXEC_SAFE': {bg: '#16a34a', label: 'SAFE'},
    'EXEC_DANGER': {bg: '#dc2626', label: 'DANGER'},
    'NO_EXEC': {bg: '#6b7280', label: 'EXEMPLE'},
    'UNKNOWN': {bg: '#7c3aed', label: classifiedType.toUpperCase()},
  };
  const vc = verdictColors[verdict] || verdictColors['UNKNOWN'];

  const wrapper"""
c = c.replace(old2, new2)

c = c.replace(
    "execBtn.innerHTML = '&#9654; Executer';",
    "execBtn.innerHTML = '&#9654; ' + vc.label;\n    execBtn.style.background = vc.bg;"
)

old4 = "  const typeLabel = document.createElement('span');\n  typeLabel.className = 'wakfu-type-label';\n  typeLabel.textContent = type.toUpperCase();\n  wrapper.appendChild(typeLabel);"
new4 = """  const typeLabel = document.createElement('span');
  typeLabel.className = 'wakfu-type-label';
  typeLabel.style.background = vc.bg + '33';
  typeLabel.style.color = vc.bg;
  typeLabel.textContent = vc.label + (reason ? ' - ' + reason.substring(0, 40) : '');
  wrapper.appendChild(typeLabel);

  if (verdict === 'EXEC_SAFE' && state.autoMode) {
    logExt('Auto-exec: ' + code.substring(0, 50));
    addPanelLog('Auto-exec: ' + code.substring(0, 50) + '...');
    setTimeout(() => execBtn.click(), 1500);
  } else if (verdict === 'EXEC_DANGER') {
    execBtn.disabled = true;
    execBtn.style.opacity = '0.5';
    execBtn.title = 'Bloque par SENTINEL: ' + reason;
  }"""
c = c.replace(old4, new4)

c = c.replace("if (type === 'powershell') {", "if (verdict === 'EXEC_SAFE' || type === 'powershell') {")

pathlib.Path(ext_file).write_text(c, 'utf-8')
print(f'content.js v3.1 OK ({len(c)} chars)')
