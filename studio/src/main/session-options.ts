// Pure builder for the Agent SDK query() options of a Studio session. Kept free of electron imports so it is unit-tested.
import type { Options } from '@anthropic-ai/claude-agent-sdk';
import type { SessionKind } from '../shared/types.ts';

/** The only skills a Studio session lists. Everything else on the machine (user and plugin skills) stays hidden. */
export const COMIC_SKILLS = [
  'comic-master',
  'comic-page-builder',
  'comic-panel-art',
  'comic-math-check',
  'comic-backgrounds',
  'comic-setup',
  'chandrush-backgrounds',
];

/**
 * Built-in tools the comic pipeline never uses. Each tool definition is re-sent on every turn, so dropping them
 * shrinks the fixed start block. Agent, Skill, Read/Write/Edit/Bash/Grep/Glob, Monitor and mcp__studio__* stay.
 */
export const DISALLOWED_TOOLS = [
  'ScheduleWakeup',
  'CronCreate',
  'CronDelete',
  'CronList',
  'RemoteTrigger',
  'WebSearch',
  'WebFetch',
  'NotebookEdit',
  'Artifact',
  'ArtifactComments',
  'ArtifactData',
  'ArtifactCheck',
  'ListAgents',
  'ReportFindings',
  'PushNotification',
  'EnterWorktree',
  'ExitWorktree',
  'EnterPlanMode',
  'ExitPlanMode',
  'AskUserQuestion',
  'DesignSync',
];

export type SessionOptionsInput = {
  cwd: string;
  kind: SessionKind;
  /** Model for run/desk sessions (Settings.model). Quick sessions always use sonnet. */
  model: string;
  executable?: string;
  env: NodeJS.ProcessEnv;
  append: string;
  resume?: string;
  mcpServers: NonNullable<Options['mcpServers']>;
  hooks?: Options['hooks'];
  canUseTool?: Options['canUseTool'];
};

export function buildSessionOptions(i: SessionOptionsInput): Options {
  return {
    cwd: i.cwd,
    pathToClaudeCodeExecutable: i.executable,
    // claude.ai connectors (Gmail, Drive, Canva...) otherwise load from the login and add their tools to every turn.
    env: { ...i.env, ENABLE_CLAUDEAI_MCP_SERVERS: 'false' },
    // No 'user': the author's ~/.claude settings (default model/effort, plugins, personal skills) must not leak in.
    // Login is not a setting source, so auth still works.
    settingSources: ['project', 'local'],
    systemPrompt: { type: 'preset', preset: 'claude_code', append: i.append },
    permissionMode: 'default',
    model: i.kind === 'quick' ? 'sonnet' : i.model || 'sonnet',
    effort: 'medium',
    skills: [...COMIC_SKILLS],
    disallowedTools: [...DISALLOWED_TOOLS],
    strictMcpConfig: true,
    resume: i.resume,
    mcpServers: i.mcpServers,
    includePartialMessages: false,
    hooks: i.hooks,
    canUseTool: i.canUseTool,
  };
}
