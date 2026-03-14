# CHANGELOG

---

## [2026-03-14] Infrastructure pipeline auto-codant v1.0
> 2026-03-14 23:28:53
> https://github.com/Duperopope/wakfu-optimizer/commits/main

### Fait
- Extension Chrome v4.1 avec SENTINEL classification
- Memory Manager v1.0 (5 memoires: episodique, procedurale, working, session, semantic)
- DocBot llama3.2:3b pour tags automatiques
- Reviewer deepseek-coder-v2 branche sur write-file
- Routes /ext-log /memory-status /classify ajoutees au dev_server
- Hook memoire sur /execute et /write-file
- Consolidation memoire en fin de session
- SENTINEL qwen2.5-coder:7b a 84-143 tok/s valide
- ResourceGovernor NORMAL/ECO/TURBO fonctionnel

### Fichiers
- scripts/memory_manager.py (476 lignes - NOUVEAU)
- scripts/dev_server.py (hooks memoire + routes)
- scripts/local_agent.py (SENTINEL + ResourceGovernor)
- scripts/gen_ext.py (generateur extension)
- wakfu-dev-extension/content.js v4.1

### Non resolus
- Extension auto-send ne trouve pas le bouton envoi Genspark (SVG path connu: clip0_739_13340)
- Extension ajoute Copy devant les commandes lors de injection
- Reviewer deepseek-coder-v2 cause timeout sur write-file (trop lent en single request)
- Debounce extension OK mais logs chat pas envoyes au Memory Manager
- Pas encore code sur le projet Wakfu lui-meme
