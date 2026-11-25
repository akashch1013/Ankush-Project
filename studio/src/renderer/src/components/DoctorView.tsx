import { useEffect, useState } from 'react';
import type { DoctorCheck } from '@shared/types';
import { api } from '../api';

export function DoctorView() {
  const [checks, setChecks] = useState<DoctorCheck[] | null>(null);
  const run = async () => {
    setChecks(null);
    setChecks(await api['doctor:run']());
  };
  useEffect(() => {
    run();
  }, []);
  return (
    <div className="doctor">
      <div className="row gap">
        <h2 className="grow">Doctor</h2>
        <button onClick={run}>Re-check</button>
      </div>
      {!checks && <div className="muted">Checking…</div>}
      {checks?.map((c) => (
        <div key={c.name} className={`check ${c.ok ? 'ok' : 'bad'}`}>
          <span className="mark">{c.ok ? '✓' : '✕'}</span>
          <div className="grow">
            <b>{c.name}</b>
            <div className="small muted">{c.detail}</div>
            {!c.ok && c.fix && <div className="small warn">{c.fix}</div>}
          </div>
        </div>
      ))}
    </div>
  );
}
