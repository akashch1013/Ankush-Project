// The author's OpenAI API key, kept in Studio's user-data folder (encrypted with the OS keychain
// when available) and handed to agent and pipeline processes as OPENAI_API_KEY. It never goes to
// the renderer: the UI only learns whether a key is saved and its last 4 characters.
import { app, net, safeStorage } from 'electron';
import { existsSync, readFileSync, rmSync, writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import type { KeyStatus } from '@shared/types';

const file = () => join(app.getPath('userData'), 'openai-key.json');
let cache: string | null | undefined;

export function getOpenAIKey(): string | null {
  if (cache !== undefined) return cache;
  cache = null;
  try {
    const j = JSON.parse(readFileSync(file(), 'utf8')) as { enc: boolean; data: string };
    const buf = Buffer.from(j.data, 'base64');
    cache = j.enc ? safeStorage.decryptString(buf) : buf.toString('utf8');
  } catch {
    /* no key saved */
  }
  return cache;
}

export function keyStatus(): KeyStatus {
  const k = getOpenAIKey();
  if (k) return { saved: true, source: 'studio', hint: `…${k.slice(-4)}` };
  const env = ['OPENAI_API_KEY', 'CHATGPT_API'].find((v) => !!process.env[v]);
  return { saved: false, source: env ? 'env' : null };
}

/** Check the key against OpenAI (GET /v1/models is free), then save it. */
export async function saveOpenAIKey(raw: string): Promise<{ ok: boolean; error?: string; warning?: string; status?: KeyStatus }> {
  const key = raw.trim().replace(/^["']|["']$/g, '');
  if (!/^sk-[\w-]{20,}$/.test(key)) return { ok: false, error: 'That does not look like an OpenAI API key (it starts with “sk-”).' };
  let warning: string | undefined;
  try {
    const res = await net.fetch('https://api.openai.com/v1/models', { headers: { authorization: `Bearer ${key}` } });
    if (res.status === 401) return { ok: false, error: 'OpenAI rejected this key (401). Copy it again from platform.openai.com/api-keys.' };
    if (!res.ok) warning = `Saved, but OpenAI answered ${res.status} when checking it.`;
  } catch {
    warning = 'Saved, but the key could not be checked (no connection to api.openai.com).';
  }
  const enc = safeStorage.isEncryptionAvailable();
  const data = (enc ? safeStorage.encryptString(key) : Buffer.from(key, 'utf8')).toString('base64');
  mkdirSync(app.getPath('userData'), { recursive: true });
  writeFileSync(file(), JSON.stringify({ enc, data }), { mode: 0o600 });
  cache = key;
  return { ok: true, warning, status: keyStatus() };
}

export function clearOpenAIKey(): KeyStatus {
  if (existsSync(file())) rmSync(file());
  cache = null;
  return keyStatus();
}
