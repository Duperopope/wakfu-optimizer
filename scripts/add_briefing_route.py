import pathlib, json

srv = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-optimizer\scripts\dev_server.py')
s = srv.read_text('utf-8')

route = """
        elif path == '/briefing':
            try:
                project = Path(__file__).resolve().parent.parent
                parts = []
                bf = project / 'BRIEFING.md'
                if bf.exists():
                    parts.append('# CONTEXTE PROJET (auto-injecte par Conductor)')
                    parts.append(bf.read_text('utf-8', errors='replace')[:2000])
                sh = project / 'SESSION_HANDOFF.md'
                if sh.exists():
                    parts.append('\\n# SESSION PRECEDENTE')
                    parts.append(sh.read_text('utf-8', errors='replace')[:1500])
                ep_file = project / 'memory' / 'episodes.jsonl'
                if ep_file.exists():
                    import json as bjson
                    episodes = [bjson.loads(l) for l in ep_file.read_text('utf-8').strip().split('\\n') if l.strip()]
                    last5 = episodes[-5:]
                    parts.append('\\n# 5 DERNIERS EPISODES')
                    for ep in last5:
                        ctx = ep.get('context', '')[:80]
                        act = ep.get('action', '')[:80]
                        ok = 'OK' if ep.get('success') else 'FAIL'
                        parts.append(f'- [{ok}] {ctx} -> {act}')
                pm = project / 'PROJECT_MEMORY.md'
                if pm.exists():
                    pmc = pm.read_text('utf-8', errors='replace')
                    idx = pmc.find('TODO')
                    if idx > 0:
                        parts.append('\\n# TODO ACTUEL')
                        parts.append(pmc[idx:idx+800])
                parts.append('\\n---\\nLe contexte a ete compacte par Genspark. Voici le briefing complet. Continue le travail.')
                briefing = '\\n'.join(parts)
                self._json({'briefing': briefing, 'length': len(briefing)})
                self.server.log(f'[BRIEFING] Genere: {len(briefing)} chars')
            except Exception as e:
                self._json({'error': str(e)}, 500)
"""

target = "        elif path == '/ollama':"
s = s.replace(target, route + "\n" + target)
srv.write_text(s, 'utf-8')
print('OK dev_server.py:', srv.stat().st_size, 'octets')
