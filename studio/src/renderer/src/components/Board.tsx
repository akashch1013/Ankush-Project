import { useMemo, useState } from 'react';
import type { ChapterState, PageStage } from '@shared/types';
import { api, fileUrl } from '../api';
import { fmtUsd } from '../store';

export const STAGE_LABEL: Record<PageStage, string> = {
  source: 'in manuscript',
  planned: 'planned',
  built: 'built',
  rendered: 'rendered',
  math_pass: 'maths PASS',
  pending: 'awaiting review',
  approved: 'approved',
  changes: 'changes asked',
};
const ORDER: PageStage[] = ['pending', 'changes', 'math_pass', 'rendered', 'built', 'planned', 'approved', 'source'];

export function StageChip({ stage }: { stage: PageStage }) {
  return <span className={`chip st-${stage}`}>{STAGE_LABEL[stage]}</span>;
}

export function Board({ chapter, openPage, onPrep }: { chapter: ChapterState; openPage: (p: string) => void; onPrep: () => void }) {
  const [filter, setFilter] = useState<PageStage | 'all' | 'built'>('all');
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [busy, setBusy] = useState<string | null>(null);

  const pages = useMemo(() => {
    if (filter === 'all') return chapter.pages;
    if (filter === 'built') return chapter.pages.filter((p) => p.preview);
    return chapter.pages.filter((p) => p.stage === filter);
  }, [chapter, filter]);

  const toggle = (p: string) =>
    setSelected((s) => {
      const n = new Set(s);
      n.has(p) ? n.delete(p) : n.add(p);
      return n;
    });

  const approveSelected = async () => {
    setBusy('approve');
    await api['review:decide'](chapter.id, [...selected].map((page) => ({ page, status: 'approved' as const })));
    setSelected(new Set());
    setBusy(null);
  };

  const prep = async () => {
    setBusy('prep');
    const r = await api['chapter:prep'](chapter.id);
    setBusy(r.every((x) => x.code === 0) ? null : `prep failed: ${r.map((x) => x.out).join('\n').slice(-400)}`);
    onPrep();
  };

  return (
    <div className="board">
      <div className="boardbar">
        <div className="filters">
          <button className={filter === 'all' ? 'on' : ''} onClick={() => setFilter('all')}>
            All <span className="muted">{chapter.pages.length}</span>
          </button>
          <button className={filter === 'built' ? 'on' : ''} onClick={() => setFilter('built')}>
            With preview <span className="muted">{chapter.pages.filter((p) => p.preview).length}</span>
          </button>
          {ORDER.filter((s) => chapter.counts[s]).map((s) => (
            <button key={s} className={filter === s ? 'on' : ''} onClick={() => setFilter(s)}>
              <span className={`dot st-${s}`} /> {STAGE_LABEL[s]} <span className="muted">{chapter.counts[s]}</span>
            </button>
          ))}
        </div>
        <div className="row gap">
          <span className="muted small">
            {chapter.referenceDir ?? 'no Reference folder'} · images {fmtUsd(chapter.imageCostUsd)}
          </span>
          {!chapter.hasSrc && chapter.manuscript && (
            <button onClick={prep} disabled={!!busy}>
              {busy === 'prep' ? 'Preparing…' : 'Prepare sources (free)'}
            </button>
          )}
          {selected.size > 0 && (
            <>
              <button className="primary" onClick={approveSelected} disabled={!!busy}>
                Approve {selected.size}
              </button>
              <button onClick={() => setSelected(new Set())}>Clear</button>
            </>
          )}
        </div>
      </div>
      {busy && busy.startsWith('prep failed') && <pre className="errorbox">{busy}</pre>}
      {!chapter.pages.length && <div className="empty">No pages yet. {chapter.manuscript ? 'Prepare the sources to split the manuscript into pages.' : ''}</div>}
      <div className="grid">
        {pages.map((p) => (
          <div key={p.page} className={`card ${selected.has(p.page) ? 'sel' : ''}`} onClick={() => openPage(p.page)}>
            <div className="thumb">
              {p.preview ? (
                <img src={fileUrl(p.preview, p.previewMtime)} loading="lazy" alt={p.page} />
              ) : (
                <div className="ph">
                  <div className="big">{p.page}</div>
                  {p.survey && (
                    <div className="muted small">
                      {p.survey.kind} · {p.survey.panels} panels · {p.survey.equations} eq · ~{p.survey.words} words
                    </div>
                  )}
                </div>
              )}
              {p.preview && (
                <input
                  type="checkbox"
                  className="pick"
                  checked={selected.has(p.page)}
                  onClick={(e) => e.stopPropagation()}
                  onChange={() => toggle(p.page)}
                  title="Select for bulk approve"
                />
              )}
            </div>
            <div className="cardfoot">
              <b>{p.page}</b>
              <span className="ellipsis grow muted small">{p.title ?? p.survey?.kind ?? ''}</span>
              <StageChip stage={p.stage} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
