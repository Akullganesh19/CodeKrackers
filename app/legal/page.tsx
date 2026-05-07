'use client'

import Sidebar from '@/components/Sidebar'
import Topbar from '@/components/Topbar'
import { motion } from 'framer-motion'
import { 
  Scale, 
  FileText, 
  Database, 
  Hash, 
  ShieldCheck, 
  ExternalLink,
  ChevronRight,
  Download,
  AlertCircle
} from 'lucide-react'

export default function Legal() {
  const ledgerEntries = [
    { id: 'E-4281', timestamp: '2025-05-07 14:32:11', type: 'Vishing Call', source: '+91-98XXX-XXXXX', hash: '0x8f2d...4e1a' },
    { id: 'E-4280', timestamp: '2025-05-07 14:18:04', type: 'Smishing SMS', source: 'SBI-ALRT', hash: '0x3a9b...7c2f' },
    { id: 'E-4279', timestamp: '2025-05-07 13:55:42', type: 'AI Voice Clone', source: '+91-72XXX-XXXXX', hash: '0x1c5e...9b8d' },
    { id: 'E-4278', timestamp: '2025-05-07 13:40:19', type: 'KYC Fraud', source: 'BK-AUTH', hash: '0x6d4f...2a3c' },
    { id: 'E-4277', timestamp: '2025-05-07 13:12:55', type: 'Bank Smishing', source: 'HDFC-KYC', hash: '0x9e1a...5d4e' },
  ]

  return (
    <div className="flex min-h-screen bg-bg text-[#e8edf5]">
      <Sidebar />
      <main className="flex-1 ml-[240px]">
        <Topbar title="Legal & Compliance Center" />

        <div className="p-12 space-y-12 max-w-[1400px] mx-auto">
          {/* COMPLIANCE STATUS */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <ComplianceCard 
              title="IT Act 2000" 
              desc="Section 66C & 66D Compliance Status" 
              status="VERIFIED" 
              color="success" 
            />
            <ComplianceCard 
              title="DPDP Act 2023" 
              desc="Data Privacy & Protection Protocols" 
              status="COMPLIANT" 
              color="accent" 
            />
            <ComplianceCard 
              title="TRAI DLT" 
              desc="Blockchain Smishing Header Verification" 
              status="ACTIVE" 
              color="success" 
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
            {/* EVIDENCE LEDGER */}
            <div className="lg:col-span-8 vsdp-card p-0 overflow-hidden">
               <div className="p-10 border-b border-white/[0.03] flex justify-between items-center bg-white/[0.01]">
                 <div className="space-y-1">
                   <h3 className="font-space text-xl tracking-tight uppercase">Tamper-Proof Evidence Ledger</h3>
                   <div className="font-mono text-[0.55rem] text-muted uppercase tracking-widest">Blockchain-hashed incident records for courtroom admissibility</div>
                 </div>
                 <div className="flex items-center gap-3 px-4 py-2 rounded border border-accent/20 bg-accent/5">
                   <Database size={14} className="text-accent" />
                   <span className="font-mono text-[0.55rem] text-accent uppercase tracking-widest">Mainnet Active</span>
                 </div>
               </div>
               
               <div className="overflow-x-auto">
                 <table className="w-full">
                   <thead>
                     <tr className="border-b border-white/[0.03] bg-white/[0.005]">
                       <th className="px-10 py-6 text-left font-mono text-[0.55rem] text-muted uppercase tracking-widest">ID / Timestamp</th>
                       <th className="px-10 py-6 text-left font-mono text-[0.55rem] text-muted uppercase tracking-widest">Threat Vector</th>
                       <th className="px-10 py-6 text-left font-mono text-[0.55rem] text-muted uppercase tracking-widest">Source Entity</th>
                       <th className="px-10 py-6 text-left font-mono text-[0.55rem] text-muted uppercase tracking-widest">Proof Hash</th>
                       <th className="px-10 py-6 text-right font-mono text-[0.55rem] text-muted uppercase tracking-widest">Verify</th>
                     </tr>
                   </thead>
                   <tbody className="divide-y divide-white/[0.03]">
                     {ledgerEntries.map((entry, i) => (
                       <tr key={i} className="group hover:bg-white/[0.01] transition-colors">
                         <td className="px-10 py-6">
                            <div className="font-mono text-[0.7rem] text-white">{entry.id}</div>
                            <div className="font-mono text-[0.5rem] text-muted">{entry.timestamp}</div>
                         </td>
                         <td className="px-10 py-6 font-mono text-[0.65rem] text-[#e8edf5]">{entry.type}</td>
                         <td className="px-10 py-6 font-mono text-[0.65rem] text-muted">{entry.source}</td>
                         <td className="px-10 py-6">
                            <div className="flex items-center gap-2 font-mono text-[0.55rem] text-accent bg-accent/5 border border-accent/10 px-2 py-1 rounded w-fit">
                              <Hash size={10} /> {entry.hash}
                            </div>
                         </td>
                         <td className="px-10 py-6 text-right">
                           <button className="text-muted hover:text-accent transition-colors">
                             <ExternalLink size={16} />
                           </button>
                         </td>
                       </tr>
                     ))}
                   </tbody>
                 </table>
               </div>
               <div className="p-8 border-t border-white/[0.03] bg-white/[0.005] flex justify-center">
                  <button className="font-mono text-[0.6rem] text-muted uppercase tracking-[0.4em] hover:text-white transition-colors">Load Archive Entries (4,276 Remaining)</button>
               </div>
            </div>

            {/* FIR DRAFTING MODULE */}
            <div className="lg:col-span-4 vsdp-card p-10 space-y-10 border-t-4 border-t-danger">
               <div className="space-y-4">
                 <h3 className="font-space text-xl tracking-tight uppercase flex items-center gap-3">
                   <FileText size={20} className="text-danger" />
                   FIR Auto-Draft
                 </h3>
                 <p className="font-mono text-[0.6rem] text-muted uppercase tracking-widest leading-loose">
                   Automatically generate a legal FIR draft for the selected incident.
                 </p>
               </div>

               <div className="space-y-8">
                  <div className="p-6 bg-surface2 border border-white/5 space-y-6">
                     <div className="space-y-2">
                       <label className="font-mono text-[0.5rem] text-muted uppercase tracking-[0.2em]">Select Jurisdiction</label>
                       <select className="w-full bg-bg border border-white/10 px-4 py-2 font-mono text-[0.65rem] text-[#e8edf5] uppercase tracking-widest focus:outline-none">
                         <option>Bengaluru Cyber Cell</option>
                         <option>Delhi North Special Unit</option>
                         <option>Mumbai EOW</option>
                       </select>
                     </div>

                     <div className="space-y-2">
                       <label className="font-mono text-[0.5rem] text-muted uppercase tracking-[0.2em]">Offense Mapping</label>
                       <div className="flex flex-wrap gap-2 pt-2">
                         <div className="node-chip-red text-[0.45rem]">§66C Identity Theft</div>
                         <div className="node-chip-red text-[0.45rem]">§66D Cheating by Personation</div>
                       </div>
                     </div>
                  </div>

                  <div className="space-y-4">
                    <button className="btn-primary w-full py-4 text-[0.65rem] uppercase tracking-widest flex items-center justify-center gap-3">
                      Generate PDF Draft <Download size={14} />
                    </button>
                    <button className="btn-ghost w-full py-4 text-[0.65rem] uppercase tracking-widest flex items-center justify-center gap-3">
                      Direct Submit to Portal <ExternalLink size={14} />
                    </button>
                  </div>

                  <div className="p-6 bg-warning/5 border border-warning/20 flex gap-4">
                     <AlertCircle size={20} className="text-warning shrink-0" />
                     <p className="font-mono text-[0.55rem] text-muted italic leading-relaxed">
                       Drafting engine uses fine-tuned LLM (Llama-3-Legal) to ensure proper terminology for Indian judicial systems.
                     </p>
                  </div>
               </div>
            </div>
          </div>

          {/* BLOCKCHAIN STATS */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
             <div className="vsdp-card p-8 flex items-center gap-6">
               <div className="w-12 h-12 rounded bg-accent/5 border border-accent/10 flex items-center justify-center text-accent">
                 <ShieldCheck size={24} />
               </div>
               <div>
                 <div className="font-mono text-[0.5rem] text-muted uppercase tracking-widest">Network_Status</div>
                 <div className="font-space font-bold uppercase">Mainnet_Active</div>
               </div>
             </div>
             <div className="vsdp-card p-8 flex items-center gap-6">
               <div className="w-12 h-12 rounded bg-success/5 border border-success/10 flex items-center justify-center text-success">
                 <Database size={24} />
               </div>
               <div>
                 <div className="font-mono text-[0.5rem] text-muted uppercase tracking-widest">Chain_Length</div>
                 <div className="font-space font-bold uppercase">842,109_Blocks</div>
               </div>
             </div>
             <div className="vsdp-card p-8 flex items-center gap-6">
               <div className="w-12 h-12 rounded bg-warning/5 border border-warning/10 flex items-center justify-center text-warning">
                 <Hash size={24} />
               </div>
               <div>
                 <div className="font-mono text-[0.5rem] text-muted uppercase tracking-widest">Hashing_Algo</div>
                 <div className="font-space font-bold uppercase">SHA-256_Enc</div>
               </div>
             </div>
             <div className="vsdp-card p-8 flex items-center gap-6">
               <div className="w-12 h-12 rounded bg-accent/5 border border-accent/10 flex items-center justify-center text-accent">
                 <Scale size={24} />
               </div>
               <div>
                 <div className="font-mono text-[0.5rem] text-muted uppercase tracking-widest">Admissibility</div>
                 <div className="font-space font-bold uppercase">Level_1_Certified</div>
               </div>
             </div>
          </div>
        </div>
      </main>
    </div>
  )
}

function ComplianceCard({ title, desc, status, color }: any) {
  return (
    <div className={`vsdp-card p-8 space-y-3 border-l-4 ${color === 'success' ? 'border-l-success' : 'border-l-accent'}`}>
       <div className="flex justify-between items-start">
         <h3 className="font-space text-lg tracking-tight uppercase">{title}</h3>
         <div className={`px-2 py-0.5 rounded font-mono text-[0.5rem] font-bold ${color === 'success' ? 'bg-success/10 text-success border border-success/20' : 'bg-accent/10 text-accent border border-accent/20'}`}>
           {status}
         </div>
       </div>
       <p className="font-mono text-[0.55rem] text-muted uppercase tracking-widest leading-loose">{desc}</p>
    </div>
  )
}
