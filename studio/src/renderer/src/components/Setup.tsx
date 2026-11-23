import { useEffect, useState } from 'react';
import type { KeyStatus, Settings } from '@shared/types';
import { api } from '../api';

const KEYS_URL = 'https://platform.openai.com/api-keys';

/** Paste / replace / remove the OpenAI API key. The key itself never comes back from the main process. */
export function OpenAIKeyField({ onSaved, autoFocus }: { onSaved?: (s: KeyStatus) => void; autoFocus?: boolean }) {
  const [status, setStatus] = useState<KeyStatus | null>(null);
  const [key, setKey] = useState('');
  const [editing, setEditing] = useState(false);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ kind: 'ok' | 'bad' | 'warn'; text: string } | null>(null);
  useEffect(() => {
    api['key:status']().then(setStatus);
  }, []);
  if (!status) return null;

  const save = async () => {
    setBusy(true);
    setMsg(null);
    const r = await api['key:save'](key);
    setBusy(false);
    if (!r.ok) return setMsg({ kind: 'bad', text: r.error ?? 'Could not save the key.' });
    setKey('');
    setEditing(false);
    setStatus(r.status!);
    setMsg(r.warning ? { kind: 'warn', text: r.warning } : { kind: 'ok', text: 'Key checked with OpenAI and saved.' });
    onSaved?.(r.status!);
  };
  const remove = async () => {
    setStatus(await api['key:clear']());
    setMsg(null);
  };

  const showInput = !status.saved || editing;
  return (
    <div className="col gap keyfield">
      {status.saved && !editing && (
        <div className="row gap">
          <span className="chip st-approved">Saved</span>
          <code className="grow">sk-{'•'.repeat(12)}{status.hint?.replace('…', '')}</code>
          <button onClick={() => setEditing(true)}>Replace</button>
          <button className="bad" onClick={remove}>Remove</button>
        </div>
      )}
      {showInput && (
        <form
          className="row gap"
          onSubmit={(e) => {
            e.preventDefault();
            if (key.trim() && !busy) save();
          }}
        >
          <input
            className="grow"
            type="password"
            autoFocus={autoFocus}
            spellCheck={false}
            autoComplete="off"
            placeholder="sk-proj-…"
            value={key}
            onChange={(e) => setKey(e.target.value)}
          />
          <button type="submit" className="primary" disabled={!key.trim() || busy}>
            {busy ? 'Checking…' : 'Save key'}
          </button>
          {editing && (
            <button type="button" onClick={() => { setEditing(false); setKey(''); setMsg(null); }}>
              Cancel
            </button>
          )}
        </form>
      )}
      {msg && <span className={`small ${msg.kind === 'ok' ? 'okc' : msg.kind === 'bad' ? 'badc' : 'warn'}`}>{msg.text}</span>}
      {!status.saved && status.source === 'env' && !msg && <span className="small muted">OPENAI_API_KEY is set in the environment and will be used unless you save a key here.</span>}
      <span className="small muted">
        Used only for image batches (backgrounds and panel art), billed to your OpenAI account. Create a key at{' '}
        <button type="button" className="link" onClick={() => api['shell:external'](KEYS_URL)}>platform.openai.com/api-keys</button>. It is stored
        encrypted on this computer and never shown to the agents.
      </span>
    </div>
  );
}

/** Create a workspace from the starter kit bundled in the app, or point Studio at an existing one. */
export function WorkspaceField({ settings, onChange }: { settings: Settings; onChange: (s: Settings) => void }) {
  const [info, setInfo] = useState<{ available: boolean; version?: string; defaultPath: string } | null>(null);
  const [target, setTarget] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    api['workspace:info']().then((i) => {
      setInfo(i);
      setTarget(i.defaultPath);
    });
  }, []);
  if (!info) return null;
  const create = async () => {
    setBusy(true);
    setError(null);
    const r = await api['workspace:create'](target);
    setBusy(false);
    if (!r.ok) return setError(r.error ?? 'Could not create the workspace.');
    onChange(r.settings!);
  };
  return (
    <div className="col gap">
      {settings.repo && (
        <div className="row gap">
          <span className="chip st-approved">Current</span>
          <code className="grow ellipsis">{settings.repo}</code>
        </div>
      )}
      {info.available && (
        <div className="col gap choice">
          <b>{settings.repo ? 'Create a new workspace' : 'Create a workspace (recommended)'}</b>
          <span className="small muted">Copies the pipeline, skills, character sheets and chapter manuscripts that ship with Studio into a folder on this computer. No GitHub access needed.</span>
          <div className="row gap">
            <input className="grow" value={target} onChange={(e) => setTarget(e.target.value)} spellCheck={false} />
            <button onClick={async () => { const d = await api['workspace:pickLocation'](); if (d) setTarget(`${d}${d.includes('\\') ? '\\' : '/'}ChandRush Studio`); }}>Change…</button>
            <button className={settings.repo ? '' : 'primary'} disabled={!target.trim() || busy} onClick={create}>{busy ? 'Creating…' : 'Create'}</button>
          </div>
        </div>
      )}
      <div className="col gap choice">
        <b>Use an existing folder</b>
        <span className="small muted">A workspace made earlier, or a clone of the repo (the folder that contains Tasks/).</span>
        <div className="row">
          <button onClick={async () => { const r = await api['settings:pickRepo'](); if (r) onChange(r); }}>Choose folder…</button>
        </div>
      </div>
      {error && <span className="small badc">{error}</span>}
    </div>
  );
}

/** First-run setup: OpenAI key, then workspace. Shown until finished or skipped. */
export function Setup({ done }: { done: () => void }) {
  const [step, setStep] = useState<0 | 1>(0);
  const [s, setS] = useState<Settings | null>(null);
  const [hasKey, setHasKey] = useState(false);
  useEffect(() => {
    api['settings:get']().then(setS);
    api['key:status']().then((k) => setHasKey(k.saved));
  }, []);
  if (!s) return null;
  const finish = async () => {
    await api['settings:save']({ setupDone: true });
    done();
  };
  return (
    <div className="setup">
      <div className="setup-card col gap">
        <div className="brand-lg">
          <span className="moon">☾</span> <b>ChandRush</b> Studio
        </div>
        <div className="steps row gap">
          <span className={step === 0 ? 'on' : hasKey ? 'done' : ''}>1 · OpenAI API key</span>
          <span className={step === 1 ? 'on' : ''}>2 · Workspace</span>
        </div>
        {step === 0 && (
          <>
            <h2>Paste your OpenAI API key</h2>
            <OpenAIKeyField autoFocus onSaved={() => setHasKey(true)} />
            <div className="row gap end">
              <button className="link" onClick={() => setStep(1)}>Skip for now</button>
              <button className="primary" disabled={!hasKey} onClick={() => setStep(1)}>Next</button>
            </div>
          </>
        )}
        {step === 1 && (
          <>
            <h2>Where should Studio keep the comic?</h2>
            <WorkspaceField settings={s} onChange={setS} />
            <div className="row gap end">
              <button className="link" onClick={() => setStep(0)}>Back</button>
              <button className="primary" disabled={!s.repo} onClick={finish}>Open Studio</button>
            </div>
            <span className="small muted">Agents also need the Claude Code CLI, logged in, plus Python 3 with Pillow and Firefox. Doctor checks all of these.</span>
          </>
        )}
      </div>
    </div>
  );
}
