import { contextBridge, ipcRenderer, webUtils } from 'electron';

const invoke = (ch: string) => (...a: unknown[]) => ipcRenderer.invoke(ch, ...a);
const channels = [
  'state:get', 'settings:get', 'settings:save', 'settings:pickRepo', 'doctor:run',
  'key:status', 'key:save', 'key:clear', 'workspace:info', 'workspace:pickLocation', 'workspace:create',
  'file:read', 'file:open', 'file:reveal', 'git:diff',
  'page:plan', 'page:imageItem', 'page:render', 'page:saveInline',
  'upload:pick', 'upload:chapter', 'chapter:prep', 'review:decide',
  'agent:list', 'agent:get', 'agent:create', 'agent:send', 'agent:desk', 'agent:interrupt', 'agent:stopTask',
  'agent:close', 'agent:permission', 'agent:gateText', 'run:start', 'run:control', 'shell:external',
] as const;

const api: Record<string, unknown> = Object.fromEntries(channels.map((c) => [c, invoke(c)]));
api.on = (channel: 'state' | 'agent', fn: (payload: unknown) => void) => {
  const l = (_e: unknown, p: unknown) => fn(p);
  ipcRenderer.on(channel, l);
  return () => ipcRenderer.removeListener(channel, l);
};
api.pathForFile = (f: File) => webUtils.getPathForFile(f);

contextBridge.exposeInMainWorld('studio', api);
