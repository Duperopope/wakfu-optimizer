import subprocess, time, os

SERVER_SCRIPT = r'H:\Code\Ankama Dev\wakfu-optimizer\scripts\dev_server.py'
PROJECT_DIR = r'H:\Code\Ankama Dev\wakfu-optimizer'
PYTHON = 'python'
MAX_RESTARTS = 50
RESTART_DELAY = 3

def main():
    restarts = 0
    while restarts < MAX_RESTARTS:
        restarts += 1
        print(f'\n=== LAUNCHER: Demarrage du serveur (tentative {restarts}) ===')
        try:
            proc = subprocess.run(
                [PYTHON, SERVER_SCRIPT],
                cwd=PROJECT_DIR
            )
            print(f'Serveur arrete (code {proc.returncode})')
            if proc.returncode == 0:
                # Verifier si c'est un restart demande (le serveur ecrit un fichier signal)
                signal_file = os.path.join(PROJECT_DIR, 'logs', '.restart_signal')
                if os.path.exists(signal_file):
                    os.remove(signal_file)
                    print('Restart demande - relance immediate...')
                    time.sleep(1)
                    continue
                else:
                    print('Arret propre (Ctrl+C). Fin du launcher.')
                    break
            else:
                print(f'Crash detecte - relance dans {RESTART_DELAY}s...')
                time.sleep(RESTART_DELAY)
        except KeyboardInterrupt:
            print('\nLauncher arrete par utilisateur.')
            break
        except Exception as e:
            print(f'Erreur launcher: {e}')
            time.sleep(RESTART_DELAY)
    if restarts >= MAX_RESTARTS:
        print(f'ERREUR: {MAX_RESTARTS} tentatives atteintes.')

if __name__ == '__main__':
    main()
