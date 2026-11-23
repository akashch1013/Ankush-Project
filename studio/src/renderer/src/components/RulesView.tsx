import { useEffect, useState } from 'react';
import { api } from '../api';

export function RulesView({ openSession }: { openSession: (id: string) => void }) {
  const [lessons, setLessons] = useState('');
  const [feedback, setFeedback] = useState('');
  const [diff, setDiff] = useState('');
  const [rule, setRule] = useState('');
  const [msg, setMsg] = useState<string | null>(null);

  const load = async () => {
    setLessons((await api['file:read']('LESSONS.md')) ?? '(LESSONS.md not found)');
    const fb = (await api['file:read']('FEEDBACK.md')) ?? '';
    setFeedback(fb.trim().split('\n').slice(-15).join('\n'));
    setDiff(await api['git:diff'](['LESSONS.md', 'FEEDBACK.md']));
  };
  useEffect(() => {
    load();
    return api.on('state', () => load());
  }, []);

  const add = async () => {
    const t = rule.trim();
    if (!t) return;
    const s = await api['agent:desk'](undefined, `/comic-master feedback "${t.replace(/"/g, "'")}"`);
    setRule('');
    setMsg(`Sent to ${s.title}. The master appends it to FEEDBACK.md, distils a rule into LESSONS.md and updates the skill if needed. The diff appears below when it's done.`);
    openSession(s.id);
  };

  return (
    <div className="rules">
      <section className="box">
        <h3>Add a permanent rule</h3>
        <p className="small muted">For “from now on…”, “always…”, “never…” feedback that should change every future page. One-off fixes belong on the page itself.</p>
        <textarea rows={3} value={rule} onChange={(e) => setRule(e.target.value)} placeholder="e.g. From now on, answer cards are always sealed until the next page; never use pastel pink." />
        <button className="primary" onClick={add} disabled={!rule.trim()}>
          Send to the master as feedback
        </button>
        {msg && <div className="small">{msg}</div>}
      </section>
      {diff && (
        <section className="box">
          <h3>Uncommitted changes to the rules</h3>
          <pre className="code diff">
            {diff.split('\n').map((l, i) => (
              <div key={i} className={l.startsWith('+') && !l.startsWith('+++') ? 'add' : l.startsWith('-') && !l.startsWith('---') ? 'del' : ''}>
                {l}
              </div>
            ))}
          </pre>
        </section>
      )}
      <div className="cols">
        <section className="box grow">
          <h3>LESSONS.md</h3>
          <pre className="code wrap">{lessons}</pre>
        </section>
        <section className="box grow">
          <h3>FEEDBACK.md (latest)</h3>
          <pre className="code wrap">{feedback}</pre>
        </section>
      </div>
    </div>
  );
}
