import { useEffect, useState } from 'react';
import type { Settings } from '@shared/types';
import { api } from '../api';
import { OpenAIKeyField, WorkspaceField } from './Setup';

export function SettingsView() {
  const [s, setS] = useState<Settings | null>(null);
  const [saved, setSaved] = useState(false);
  useEffect(() => {
    api['settings:get']().then(setS);
  }, []);
  if (!s) return null;
  const save = async (patch: Partial<Settings>) => {
    setS(await api['settings:save'](patch));
    setSaved(true);
    setTimeout(() => setSaved(false), 1200);
  };
  return (
    <div className="settings col gap">
      <h2>Settings {saved && <span className="small muted">saved</span>}</h2>
      <div className="col gap">
        <span className="muted">OpenAI API key (image generation)</span>
        <OpenAIKeyField />
      </div>
      <div className="col gap">
        <span className="muted">Workspace (the folder that contains Tasks/)</span>
        <WorkspaceField settings={s} onChange={setS} />
      </div>
      <label>
        Permissions for agent tool calls
        <select value={s.permissionMode} onChange={(e) => save({ permissionMode: e.target.value as Settings['permissionMode'] })}>
          <option value="safe">Pipeline-safe auto (recommended): pipeline scripts and page files run without asking; anything else asks</option>
          <option value="ask">Ask for everything the CLI would prompt for</option>
          <option value="auto">Allow everything (still blocked: Reference/Charactors edits, API key, immediate calls)</option>
        </select>
        <span className="small muted">Paid image batches always ask, in every mode.</span>
      </label>
      <label>
        Default pages per run session
        <input type="number" min={1} max={35} value={s.chunkSize} onChange={(e) => save({ chunkSize: +e.target.value || 20 })} />
      </label>
      <label>
        Python <input value={s.python} onChange={(e) => setS({ ...s, python: e.target.value })} onBlur={() => save({ python: s.python })} />
      </label>
      <label>
        Claude Code CLI <input value={s.claude} onChange={(e) => setS({ ...s, claude: e.target.value })} onBlur={() => save({ claude: s.claude })} />
        <span className="small muted">“claude” finds the CLI on PATH or in ~/.local/bin (your login and settings). Give a full path to use a specific install.</span>
      </label>
      <label>
        Firefox <input value={s.firefox} onChange={(e) => setS({ ...s, firefox: e.target.value })} onBlur={() => save({ firefox: s.firefox })} />
      </label>
    </div>
  );
}
