import './discrete-action-learning.css';

const tracks = [
  {
    id: '01',
    eyebrow: '末端运动',
    token: 'EEF',
    values: ['18', '42', '07', '31', '56'],
    className: 'dal-track-eef',
  },
  {
    id: '02',
    eyebrow: '末端执行器',
    token: 'HAND',
    values: ['04', '29', '51', '16', '38'],
    className: 'dal-track-hand',
  },
  {
    id: '03',
    eyebrow: '下肢动作',
    token: 'LOWER',
    values: ['27', '11', '44', '03', '22'],
    className: 'dal-track-lower',
  },
] as const;

const defaultDescription =
  '统一动作空间按 EEF 运动、末端执行器和 Lower Body 划分为三个部分，并分别训练 RVQ 模型完成动作离散化。离散动作 token 与视觉、语言表征在同一 VLM 中对齐和联合训练。';

export interface DiscreteActionLearningProps {
  title?: string;
  description?: string;
  className?: string;
}

function FlowArrow({ delay = 0 }: { delay?: number }) {
  return (
    <svg className="dal-flow-arrow" viewBox="0 0 92 24" aria-hidden="true">
      <path
        className="dal-flow-line"
        d="M2 12h78"
        pathLength="1"
        style={{ animationDelay: `${delay}s` }}
      />
      <path className="dal-flow-head" d="m72 4 10 8-10 8" />
      <circle
        className="dal-flow-dot"
        cx="2"
        cy="12"
        r="3"
        style={{ animationDelay: `${delay}s` }}
      />
    </svg>
  );
}

function MotionGlyph({ index }: { index: number }) {
  if (index === 0) {
    return (
      <svg viewBox="0 0 78 54" aria-hidden="true">
        <path d="M9 36c11-2 19-9 25-20 5 9 14 16 28 20" />
        <circle cx="34" cy="16" r="4" />
      </svg>
    );
  }

  if (index === 1) {
    return (
      <svg viewBox="0 0 78 54" aria-hidden="true">
        <path d="M8 34c13 0 23-5 31-15 8 10 18 15 31 15" />
        <path d="M24 38h30" />
      </svg>
    );
  }

  return (
    <svg viewBox="0 0 78 54" aria-hidden="true">
      <path d="M19 16h40l-5 24H24z" />
      <path d="M28 40v7m22-7v7" />
    </svg>
  );
}

export function DiscreteActionLearning({
  title = 'Discrete action learning',
  description = defaultDescription,
  className = '',
}: DiscreteActionLearningProps) {
  return (
    <section className={`dal-root ${className}`.trim()}>
      <article className="dal-card">
        <header className="dal-intro">
          <div className="dal-kicker"><span /> ACTION TOKENIZER</div>
          <h2>{title}</h2>
          <p>{description}</p>
        </header>

        <section className="dal-pipeline" aria-label="离散动作学习流程图">
          <div className="dal-live" aria-label="动画正在循环播放">
            <i /> LIVE ENCODING
          </div>
          <div className="dal-column-labels" aria-hidden="true">
            <span>CONTINUOUS MOTION</span>
            <span>VECTOR QUANTIZATION</span>
            <span>DISCRETE TOKENS</span>
          </div>

          <div className="dal-tracks">
            {tracks.map((track, index) => (
              <div className={`dal-track ${track.className}`} key={track.id}>
                <div className="dal-source">
                  <div className="dal-motion-glyph"><MotionGlyph index={index} /></div>
                  <div><small>{track.eyebrow}</small></div>
                </div>

                <FlowArrow delay={index * 0.45} />

                <div className="dal-rvq-card">
                  <span>RVQ</span>
                  <div className="dal-codebook" aria-hidden="true"><i /><i /><i /></div>
                </div>

                <FlowArrow delay={0.25 + index * 0.45} />

                <div className="dal-token-sequence">
                  <span className="dal-boundary">&lt;{track.token}_START&gt;</span>
                  {track.values.map((value) => <i key={value}>{value}</i>)}
                  <span className="dal-boundary">&lt;{track.token}_END&gt;</span>
                </div>
              </div>
            ))}
          </div>

          <div className="dal-timeline">
            <div className="dal-timeline-rule"><span /></div>
            <p><b>时间维度对齐</b><span>共享时间步 · 同步注入 VLM</span></p>
          </div>
        </section>

      </article>
    </section>
  );
}

export default DiscreteActionLearning;
