// Runs the free, deterministic pipeline scripts directly (no agent).
import { spawn } from 'node:child_process';
import { getSettings, requireTasks, childEnv } from './settings';
import type { ToolRunResult } from '@shared/types';

const locks = new Map<string, Promise<unknown>>();

/** Run `python3 pipeline/<script> ...args` from Tasks/. Calls sharing a lock key run one at a time. */
export function runPipeline(script: string, args: string[], lockKey?: string, timeoutMs = 300_000): Promise<ToolRunResult> {
  const job = () => runCmd(getSettings().python, [`pipeline/${script}`, ...args], requireTasks(), timeoutMs);
  if (!lockKey) return job();
  const prev = locks.get(lockKey) ?? Promise.resolve();
  const next = prev.catch(() => undefined).then(job);
  locks.set(lockKey, next);
  return next;
}

export function runCmd(cmd: string, args: string[], cwd?: string, timeoutMs = 60_000): Promise<ToolRunResult> {
  return new Promise((resolve) => {
    let out = '';
    let done = false;
    const finish = (code: number) => {
      if (done) return;
      done = true;
      clearTimeout(timer);
      resolve({ code, out: out.length > 20000 ? out.slice(-20000) : out });
    };
    let child;
    try {
      child = spawn(cmd, args, { cwd, env: childEnv() });
    } catch (e) {
      return resolve({ code: -1, out: String(e) });
    }
    const timer = setTimeout(() => {
      out += `\n[timed out after ${timeoutMs / 1000}s]`;
      child.kill();
      finish(-1);
    }, timeoutMs);
    child.stdout.on('data', (d) => (out += d));
    child.stderr.on('data', (d) => (out += d));
    child.on('error', (e) => {
      out += String(e);
      finish(-1);
    });
    child.on('close', (code) => finish(code ?? -1));
  });
}
