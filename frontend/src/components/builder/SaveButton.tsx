'use client';
import { useState } from 'react';

interface SaveButtonProps {
  buildName: string;
  onSave?: () => void;
}

export function SaveButton({ buildName, onSave }: SaveButtonProps) {
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    const key = 'wakfu-build-' + buildName.replace(/\s+/g, '_');
    const data = JSON.stringify({ name: buildName, date: new Date().toISOString() });
    localStorage.setItem(key, data);
    setSaved(true);
    if (onSave) onSave();
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <button
      onClick={handleSave}
      className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
        saved
          ? 'bg-green-600 text-white cursor-default'
          : 'bg-blue-600 hover:bg-blue-700 text-white cursor-pointer'
      }`}
    >
      {saved ? '\u2705 Sauvegarde !' : 'Sauvegarder'}
    </button>
  );
}