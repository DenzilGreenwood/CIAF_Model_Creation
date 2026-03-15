import React, { useEffect } from 'react';
import { Line, Doughnut, Radar, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  RadarController,
  BarController,
  Tooltip,
  Legend,
  Filler,
  RadialLinearScale,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  RadarController,
  BarController,
  Tooltip,
  Legend,
  Filler,
  RadialLinearScale
);

export const Home: React.FC = () => {
  useEffect(() => {
    // Scroll to section if hash is present
    const hash = window.location.hash;
    if (hash) {
      setTimeout(() => {
        const element = document.querySelector(hash);
        element?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  }, []);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#f8fafc',
          font: { family: 'Inter', size: 13 },
        },
      },
    },
  };

  const readinessData = {
    labels: ['High-Stakes AI Deployments', 'Cryptographic Proof Capability'],
    datasets: [
      {
        data: [85, 15],
        backgroundColor: ['#1e293b', '#FF6D00'],
        borderColor: '#0f172a',
        borderWidth: 4,
        hoverOffset: 4,
      },
    ],
  };

  const comparisonData = {
    labels: [
      'Tamper-Evident Security',
      'Independent Custody Model',
      'Auditor Verification Trust',
      'Incident Reconstruction Speed',
      'Lifecycle Event Coverage',
    ],
    datasets: [
      {
        label: 'AI Evidence Vault',
        data: [100, 100, 95, 90, 100],
        backgroundColor: 'rgba(0, 229, 255, 0.2)',
        borderColor: '#00E5FF',
        pointBackgroundColor: '#00E5FF',
        pointBorderColor: '#fff',
        borderWidth: 2,
      },
      {
        label: 'Internal Logging',
        data: [30, 0, 40, 50, 60],
        backgroundColor: 'rgba(255, 109, 0, 0.2)',
        borderColor: '#FF6D00',
        pointBackgroundColor: '#FF6D00',
        pointBorderColor: '#fff',
        borderWidth: 2,
      },
    ],
  };

  const lifecycleData = {
    labels: [
      'Data Ingest & Curation',
      'Model Training Phase',
      'Validation & Policy Gates',
      'Production Inference',
      'Autonomous Agent Actions',
      'Human Approval Checkpoints',
    ],
    datasets: [
      {
        label: 'Evidence Cryptographically Retained',
        data: [75, 85, 100, 90, 100, 95],
        backgroundColor: '#2962FF',
        borderRadius: 6,
      },
    ],
  };

  return (
    <div className="bg-slate-950 text-slate-50">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur-md border-b border-slate-800 p-4">
        <div className="container mx-auto flex justify-between items-center">
          <div className="text-2xl font-black tracking-tighter text-white">
            CIAF <span className="text-cyan-400">VAULT</span>
          </div>
          <div className="hidden md:flex space-x-6 text-sm font-medium text-slate-300">
            <a href="#problem" className="hover:text-cyan-400 transition">
              The Problem
            </a>
            <a href="#architecture" className="hover:text-cyan-400 transition">
              Architecture
            </a>
            <a href="#evidence" className="hover:text-cyan-400 transition">
              Evidence vs Logs
            </a>
            <a href="#lifecycle" className="hover:text-cyan-400 transition">
              Lifecycle
            </a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="container mx-auto px-6 py-20 md:py-32 text-center">
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6">
          From AI Logging to{' '}
          <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
            AI Proof
          </span>
        </h1>
        <p className="text-xl md:text-2xl text-slate-400 max-w-3xl mx-auto mb-10 leading-relaxed">
          The trusted third-party evidence vault for AI lifecycle, agent, and decision records in regulated
          environments. We help organizations move beyond fragmented logs to cryptographically verifiable proof.
        </p>
        <button className="inline-block bg-blue-600 hover:bg-cyan-400 text-white hover:text-slate-900 font-bold py-3 px-8 rounded-full transition duration-300 shadow-[0_0_20px_rgba(41,98,255,0.4)] text-lg">
          Request Briefing
        </button>
      </header>

      <main className="container mx-auto px-6 space-y-24 pb-24">
        {/* Problem Section */}
        <section id="problem" className="scroll-mt-24">
          <div className="max-w-4xl mx-auto text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">The AI Accountability Crisis</h2>
            <p className="text-lg text-slate-300">
              AI systems are increasingly deployed in high-stakes contexts, yet most organizations rely on scattered,
              editable logs. When asked to prove what happened during an incident, internal dashboards and standard
              monitoring fall short. High-stakes AI requires verifiable proof, not just internal recordkeeping.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-xl hover:border-blue-500 transition">
              <h3 className="text-xl font-bold mb-6 text-center text-slate-200">
                Enterprise Readiness for High-Stakes Audit
              </h3>
              <div className="h-80">
                <Doughnut
                  data={readinessData}
                  options={{
                    ...chartOptions,
                    cutout: '75%',
                  }}
                />
              </div>
            </div>
            <div className="space-y-6">
              <div className="p-6 bg-slate-800/50 rounded-xl border border-slate-700 border-l-4 border-l-orange-500">
                <h4 className="text-lg font-bold text-white mb-2">Fragmented</h4>
                <p className="text-slate-400">
                  Logs exist in silos across data pipelines, model registries, and application code.
                </p>
              </div>
              <div className="p-6 bg-slate-800/50 rounded-xl border border-slate-700 border-l-4 border-l-orange-500">
                <h4 className="text-lg font-bold text-white mb-2">Editable</h4>
                <p className="text-slate-400">
                  Internal records are organization-controlled and susceptible to post-incident alteration.
                </p>
              </div>
              <div className="p-6 bg-slate-800/50 rounded-xl border border-slate-700 border-l-4 border-l-orange-500">
                <h4 className="text-lg font-bold text-white mb-2">Hard to Trust</h4>
                <p className="text-slate-400">
                  Third-party auditors and regulators struggle to verify internally reconstructed narratives.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Architecture Section */}
        <section id="architecture" className="scroll-mt-24">
          <div className="max-w-4xl mx-auto text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 text-cyan-400">Independent Custody Architecture</h2>
            <p className="text-lg text-slate-300">
              The Artificial Intelligence Evidence Vault acts as a neutral evidence custody layer. Instead of simply monitoring activity, we
              cryptographically capture, canonicalize, and securely retain lifecycle and runtime evidence. This
              independent custody model fundamentally changes the trust dynamic for external oversight.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-8 md:p-12 rounded-3xl shadow-2xl">
            <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
              <div className="bg-slate-800 border-2 border-cyan-400 rounded-lg p-4 text-center">
                <span className="text-cyan-400 text-3xl mb-2 block">*</span>
                <span className="text-xs uppercase tracking-wider text-slate-400">Phase 1</span>
                <span className="text-sm font-bold">Capture</span>
              </div>
              <div className="flex items-center justify-center text-orange-500 text-2xl">→</div>
              <div className="bg-slate-800 border-2 border-cyan-400 rounded-lg p-4 text-center">
                <span className="text-cyan-400 text-3xl mb-2 block">⊙</span>
                <span className="text-xs uppercase tracking-wider text-slate-400">Phase 2</span>
                <span className="text-sm font-bold">Canonicalize</span>
              </div>
              <div className="flex items-center justify-center text-orange-500 text-2xl">→</div>
              <div className="bg-slate-800 border-2 border-cyan-400 rounded-lg p-4 text-center">
                <span className="text-cyan-400 text-3xl mb-2 block">✎</span>
                <span className="text-xs uppercase tracking-wider text-slate-400">Phase 3</span>
                <span className="text-sm font-bold">Sign</span>
              </div>
              <div className="flex items-center justify-center text-orange-500 text-2xl">→</div>
              <div className="bg-slate-800 border-2 border-blue-500 rounded-lg p-4 text-center">
                <span className="text-blue-500 text-3xl mb-2 block">🔒</span>
                <span className="text-xs uppercase tracking-wider text-slate-400">Phase 4</span>
                <span className="text-sm font-bold">Retain (WORM)</span>
              </div>
            </div>

            <div className="mt-8 text-center text-slate-400 bg-slate-950 p-6 rounded-xl border border-slate-800">
              <p className="mb-2">
                <strong className="text-white">The Outcome:</strong> Generating cryptographic receipts, signed
                records, and multi-tenant evidence isolation to support full incident reconstruction via an immutable
                Audit Pack.
              </p>
            </div>
          </div>
        </section>

        {/* Evidence vs Logs Section */}
        <section id="evidence" className="scroll-mt-24">
          <div className="max-w-4xl mx-auto text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Logging vs. Cryptographic Proof</h2>
            <p className="text-lg text-slate-300">
              Dashboards provide operational visibility, but they do not provide legal defensibility. To satisfy
              regulators and audit firms, evidence must be tamper-evident, independently held, and capable of
              reproducing the exact state of a high-risk AI decision.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-6 md:p-10 rounded-2xl shadow-xl grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            <div className="space-y-8">
              <div>
                <h4 className="text-xl font-bold text-orange-500 flex items-center gap-2">
                  <span>✕</span> Standard AI Logging
                </h4>
                <p className="text-slate-400 mt-2">
                  Activity is recorded, but relies entirely on internal security models. Vulnerable to deletion,
                  fragmentation, and post-incident manipulation.
                </p>
              </div>
              <div>
                <h4 className="text-xl font-bold text-cyan-400 flex items-center gap-2">
                  <span>✓</span> AI-EV Proof
                </h4>
                <p className="text-slate-400 mt-2">
                  Cryptographic receipts guarantee the chain of custody. Independent retention ensures the timeline
                  is absolute and auditor-ready.
                </p>
              </div>
            </div>
            <div className="h-80">
              <Radar data={comparisonData} options={chartOptions} />
            </div>
          </div>
        </section>

        {/* Lifecycle Section */}
        <section id="lifecycle" className="scroll-mt-24">
          <div className="max-w-4xl mx-auto text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Lifecycle-Wide Accountability</h2>
            <p className="text-lg text-slate-300">
              True AI governance requires unbroken evidence chains. The AI Evidence Vault spans the entire lifecycle, ensuring
              that data curation, model training, policy gates, and autonomous agent actions are all bound by
              verifiable proof.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-xl">
            <h3 className="text-xl font-bold mb-6 text-center text-slate-200">
              Evidence Density Across AI System Stages
            </h3>
            <div className="h-96">
              <Bar
                data={lifecycleData}
                options={{
                  ...chartOptions,
                  indexAxis: 'y',
                  scales: {
                    x: {
                      grid: { color: 'rgba(255,255,255,0.05)' },
                      ticks: { color: '#8892B0' },
                    },
                    y: {
                      grid: { display: false },
                      ticks: { color: '#f8fafc' },
                    },
                  },
                }}
              />
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="mt-24 border-t border-slate-800 pt-20">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold mb-6">Designed for the Ecosystem</h2>
              <p className="text-lg text-slate-300 mb-8">
                The Artificial Intelligence Evidence Vault serves as the foundational trust infrastructure for regulated AI. We are building the
                category of AI evidence custody to empower the entire ecosystem.
              </p>
              <ul className="space-y-4 text-slate-300">
                <li className="flex items-center gap-3">
                  <span className="text-blue-500 text-2xl">■</span>
                  <div>
                    <strong>Regulators & Auditors:</strong> Independent verification and reliable incident
                    reconstruction.
                  </div>
                </li>
                <li className="flex items-center gap-3">
                  <span className="text-cyan-400 text-2xl">■</span>
                  <div>
                    <strong>Enterprises:</strong> Legal defensibility, accelerated audits, and reduced operational
                    risk.
                  </div>
                </li>
                <li className="flex items-center gap-3">
                  <span className="text-orange-500 text-2xl">■</span>
                  <div>
                    <strong>Strategic Partners:</strong> Integration into GRC workflows and AI observability platforms.
                  </div>
                </li>
              </ul>
            </div>
            <div className="bg-slate-900 p-8 rounded-2xl border border-slate-700 text-center shadow-[0_10px_40px_rgba(41,98,255,0.1)]">
              <h3 className="text-2xl font-bold text-white mb-4">Become a Design Partner</h3>
              <p className="text-slate-400 mb-8">
                We are actively seeking strategic validators who understand AI risk, audit, and infrastructure to
                pressure-test category-defining trust infrastructure.
              </p>
              <button className="w-full bg-gradient-to-r from-blue-600 to-cyan-400 hover:from-cyan-400 hover:to-blue-600 text-white font-bold py-4 rounded-xl transition duration-300 shadow-lg text-lg">
                Initiate Conversation
              </button>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-slate-950 py-8 border-t border-slate-900 mt-12 text-center text-slate-500">
        <div className="container mx-auto px-6">
          <p>&copy; 2026 Artificial Intelligence Evidence Vault. The independent evidence vault for AI systems.</p>
        </div>
      </footer>
    </div>
  );
};

export default Home;
