import { useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, useInView } from 'framer-motion';
import { useAuth, SignInButton, SignUpButton } from '@clerk/react';
import Navbar from '../components/Navbar';

const C = {
  bg:'#F5F5F5',surface:'#FFFFFF',dark:'#1A1626',darkest:'#0A0A0F',
  accent:'#6C63FF',accentSoft:'#EEEDFF',border:'#E0E0E8',
  text:'#0A0A0F',muted:'#6B6B80',textInv:'#F0F0FF',
  mutedInv:'rgba(240,240,255,0.55)',
};
const fontD="'Sora', sans-serif";
const fontM="'DM Mono', monospace";

function Arrow({size=15,color='#0A0A0F'}){
  return <svg width={size} height={size} viewBox="0 0 16 16" fill="none"><path d="M3.33 8H12.67M12.67 8L8.67 4M12.67 8L8.67 12" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;
}

function Label({children}){
  return <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:14}} className="eyebrow-row">
    <span style={{width:6,height:6,borderRadius:'50%',background:C.accent,flexShrink:0}}/>
    <span style={{fontFamily:fontM,fontSize:11,color:C.accent,letterSpacing:'0.1em'}}>{children}</span>
  </div>;
}

function Pill({onClick,children,accent=false,large=false}){
  const bg=accent?C.accent:C.darkest;
  return <button onClick={onClick} style={{
    display:'inline-flex',alignItems:'center',gap:large?14:12,
    background:bg,color:'#FFF',fontFamily:fontD,fontWeight:600,
    fontSize:large?16:15,paddingLeft:large?30:22,paddingRight:large?10:8,
    paddingTop:large?12:10,paddingBottom:large?12:10,
    borderRadius:999,border:'none',cursor:'pointer',whiteSpace:'nowrap',
    transition:'opacity 0.2s,transform 0.15s',
  }}
  onMouseEnter={e=>{e.currentTarget.style.opacity='0.88';e.currentTarget.style.transform='translateY(-1px)';}}
  onMouseLeave={e=>{e.currentTarget.style.opacity='1';e.currentTarget.style.transform='translateY(0)';}}
  >{children}<span style={{background:'#FFF',borderRadius:'50%',padding:large?9:7,display:'flex',alignItems:'center',justifyContent:'center',flexShrink:0}}><Arrow size={large?16:14} color={accent?C.accent:C.darkest}/></span></button>;
}

function FadeIn({children,delay=0,y=28}){
  const ref=useRef(null);
  const v=useInView(ref,{once:true,margin:'-50px'});
  return <motion.div ref={ref} initial={{opacity:0,y}} animate={v?{opacity:1,y:0}:{}} transition={{duration:0.55,delay,ease:'easeOut'}}>{children}</motion.div>;
}

function HeroIllustration(){
  return (
    <svg viewBox="0 0 480 420" fill="none" xmlns="http://www.w3.org/2000/svg" style={{width:'100%',maxWidth:480,height:'auto'}}>
      <rect x="40" y="60" width="320" height="300" rx="24" fill="#FFFFFF" stroke="#E0E0E8" strokeWidth="1.5"/>
      <rect x="40" y="60" width="320" height="56" rx="24" fill="#6C63FF"/>
      <rect x="40" y="88" width="320" height="28" fill="#6C63FF"/>
      <rect x="68" y="78" width="120" height="10" rx="5" fill="rgba(255,255,255,0.9)"/>
      <rect x="68" y="94" width="80" height="8" rx="4" fill="rgba(255,255,255,0.5)"/>
      <rect x="288" y="74" width="56" height="22" rx="11" fill="rgba(255,255,255,0.2)"/>
      <text x="316" y="89" fontFamily="monospace" fontSize="9" fill="white" textAnchor="middle" fontWeight="700">SURVIVAL</text>
      {[0,1,2,3].map(i=>(
        <g key={i} transform={`translate(0, ${i*52})`}>
          <rect x="60" y="140" width="280" height="40" rx="10" fill="#F8F8FF" stroke="#E0E0E8" strokeWidth="1"/>
          <circle cx="80" cy="160" r="6" fill={i===0?'#E8341C':i===1?'#E8341C':i===2?'#D4910A':'#6B6B80'}/>
          <rect x="96" y="154" width={i===0?160:i===1?140:i===2?150:120} height="8" rx="4" fill="#0A0A0F" opacity="0.7"/>
          <rect x="96" y="167" width="60" height="6" rx="3" fill="#6B6B80" opacity="0.5"/>
          <rect x="268" y="154" width="52" height="6" rx="3" fill="#E0E0E8"/>
          <rect x="268" y="154" width={i===0?44:i===1?40:i===2?34:26} height="6" rx="3" fill="#6C63FF"/>
          <text x="323" y="170" fontFamily="monospace" fontSize="8" fill="#6C63FF" textAnchor="end" fontWeight="500">{i===0?'85%':i===1?'77%':i===2?'64%':'49%'}</text>
        </g>
      ))}
      <rect x="310" y="30" width="130" height="44" rx="14" fill="#0A0A0F"/>
      <text x="375" y="49" fontFamily="monospace" fontSize="9" fill="rgba(240,240,255,0.6)" textAnchor="middle">EXAM DATE</text>
      <text x="375" y="64" fontFamily="sans-serif" fontSize="12" fill="white" textAnchor="middle" fontWeight="700">3 days left</text>
      <circle cx="320" cy="52" r="4" fill="#E8341C"/>
      <rect x="0" y="310" width="140" height="52" rx="14" fill="#FFFFFF" stroke="#E0E0E8" strokeWidth="1.5"/>
      <text x="20" y="330" fontFamily="monospace" fontSize="8" fill="#6B6B80">STUDY MODE</text>
      <text x="20" y="350" fontFamily="sans-serif" fontSize="14" fill="#6C63FF" fontWeight="700">{'Survival 🔥'}</text>
      <rect x="340" y="340" width="130" height="52" rx="14" fill="#6C63FF"/>
      <text x="360" y="360" fontFamily="monospace" fontSize="8" fill="rgba(255,255,255,0.7)">PLAN READY</text>
      <text x="360" y="378" fontFamily="sans-serif" fontSize="13" fill="white" fontWeight="700">{'5 questions →'}</text>
      {[0,1,2,3].map(row=>[0,1,2,3].map(col=>(
        <circle key={`${row}-${col}`} cx={col*14+8} cy={row*14+8} r="2" fill="#6C63FF" opacity={0.12+(row+col)*0.02}/>
      )))}
    </svg>
  );
}

const marqueeItems=['Observer Pattern','SOLID Principles','Factory Pattern','Strategy Pattern','MVC','SESD','NST','Design Patterns','UML Diagrams','Singleton','Decorator','Repository'];

export default function HomePage(){
  const navigate=useNavigate();
  const {isSignedIn}=useAuth();

  function CTAButton({large=false,label='Start Preparing',accent=false}){
    if(isSignedIn) return <Pill onClick={()=>navigate('/input')} large={large} accent={accent}>{label}</Pill>;
    return <SignUpButton mode="modal"><Pill large={large} accent={accent}>{label}</Pill></SignUpButton>;
  }

  return (
    <div style={{background:C.bg,overflowX:'hidden'}}>
      <style>{`
        @keyframes marquee{from{transform:translateX(0)}to{transform:translateX(-50%)}}
        .mtrack{display:flex;width:max-content;animation:marquee 22s linear infinite}
        .hero-grid{display:grid;grid-template-columns:1fr 1fr;align-items:center;gap:80px}
        .hero-visual{display:flex}
        .section-grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
        .section-grid-6{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
        .stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:0}
        .modes-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
        .section-pad{padding:100px 80px}
        .hero-pad{padding:0 80px}
        .footer-row{flex-direction:row;padding:28px 80px}
        .stat-divider{border-right:1px solid rgba(255,255,255,0.08)}
        @media(max-width:1024px){
          .hero-grid{grid-template-columns:1fr;gap:48px;text-align:center}
          .hero-visual{justify-content:center}
          .section-grid-3{grid-template-columns:repeat(2,1fr)}
          .section-grid-6{grid-template-columns:repeat(2,1fr)}
          .stats-grid{grid-template-columns:repeat(2,1fr);gap:32px}
          .modes-grid{grid-template-columns:1fr;max-width:480px;margin:0 auto}
          .section-pad{padding:80px 40px}
          .hero-pad{padding:0 40px}
          .hero-cta{justify-content:center!important}
          .hero-marquee{margin:48px auto 0!important}
          .eyebrow-row{justify-content:center}
          .stat-divider{border-right:none}
          .footer-row{padding:24px 40px}
        }
        @media(max-width:640px){
          .hero-grid{gap:32px}
          .hero-visual{display:none}
          .section-grid-3{grid-template-columns:1fr}
          .section-grid-6{grid-template-columns:1fr}
          .stats-grid{grid-template-columns:repeat(2,1fr);gap:24px}
          .modes-grid{grid-template-columns:1fr}
          .section-pad{padding:64px 20px}
          .hero-pad{padding:0 20px}
          .footer-row{flex-direction:column;gap:16px;text-align:center;padding:24px 20px}
          .stat-divider{border-right:none}
        }
      `}</style>

      <Navbar/>

      {/* HERO */}
      <section style={{minHeight:'100vh',background:'linear-gradient(160deg,#EEEAFF 0%,#F5F5F5 45%,#F0EEFF 100%)',display:'flex',alignItems:'center',paddingTop:56}}>
        <div style={{maxWidth:1200,margin:'0 auto',width:'100%'}} className="hero-pad">
          <div className="hero-grid">
            <motion.div initial={{opacity:0,y:24}} animate={{opacity:1,y:0}} transition={{duration:0.6}}>
              <div style={{display:'inline-flex',alignItems:'center',gap:8,background:C.accentSoft,border:'1px solid #C8C4FF',borderRadius:999,padding:'6px 16px',marginBottom:28}}>
                <span style={{width:6,height:6,borderRadius:'50%',background:C.accent}}/>
                <span style={{fontFamily:fontM,fontSize:11,color:'#4A44AA',letterSpacing:'0.07em'}}>AI-POWERED EXAM INTELLIGENCE</span>
              </div>
              <h1 style={{fontFamily:fontD,fontWeight:700,fontSize:'clamp(38px,5vw,68px)',color:C.text,letterSpacing:'-0.04em',lineHeight:1.06,marginBottom:24,maxWidth:650}}>
                Less time. More marks.{' '}<span style={{color:C.accent}}>AI knows</span>{' '}what to study.
              </h1>
              <p style={{fontFamily:fontD,fontSize:'clamp(15px,1.8vw,18px)',color:C.muted,lineHeight:1.65,maxWidth:420,marginBottom:40}}>
                Tell Prepzo your subject and exam date. Get a precision study plan ranked by what's <em>actually</em> likely to appear.
              </p>
              <div className="hero-cta" style={{display:'flex',gap:12,flexWrap:'wrap',alignItems:'center',marginBottom:16}}>
                <CTAButton/>
                <button onClick={()=>document.getElementById('how-it-works')?.scrollIntoView({behavior:'smooth'})} style={{display:'inline-flex',alignItems:'center',background:'transparent',color:C.muted,fontFamily:fontD,fontSize:15,border:`1px solid ${C.border}`,borderRadius:999,padding:'10px 22px',cursor:'pointer',whiteSpace:'nowrap',transition:'border-color 0.2s,color 0.2s'}}
                  onMouseEnter={e=>{e.currentTarget.style.borderColor=C.accent;e.currentTarget.style.color=C.accent}}
                  onMouseLeave={e=>{e.currentTarget.style.borderColor=C.border;e.currentTarget.style.color=C.muted}}>
                  See how it works ↓
                </button>
              </div>
              {!isSignedIn&&<SignInButton mode="modal"><button style={{background:'none',border:'none',cursor:'pointer',fontFamily:fontD,fontSize:13,color:C.muted,textDecoration:'underline',textUnderlineOffset:3,padding:0}}>Already have an account? Sign in</button></SignInButton>}
              <div className="hero-marquee" style={{marginTop:52,overflow:'hidden',maxWidth:460}}>
                <div className="mtrack">
                  {[...marqueeItems,...marqueeItems].map((t,i)=><span key={i} style={{fontFamily:fontM,fontSize:11,color:'rgba(10,10,15,0.28)',letterSpacing:'0.07em',marginRight:36,whiteSpace:'nowrap',textTransform:'uppercase'}}>{t}</span>)}
                </div>
              </div>
            </motion.div>
            <motion.div className="hero-visual" initial={{opacity:0,x:32}} animate={{opacity:1,x:0}} transition={{duration:0.7,delay:0.15}}>
              <HeroIllustration/>
            </motion.div>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section id="how-it-works" style={{background:C.bg}} className="section-pad">
        <div style={{maxWidth:1100,margin:'0 auto'}}>
          <FadeIn><div style={{textAlign:'center',marginBottom:60}}>
            <Label>HOW IT WORKS</Label>
            <h2 style={{fontFamily:fontD,fontWeight:700,fontSize:'clamp(28px,4vw,48px)',color:C.text,letterSpacing:'-0.04em',marginBottom:14}}>Three steps to exam clarity.</h2>
            <p style={{fontFamily:fontD,fontSize:16,color:C.muted,maxWidth:420,margin:'0 auto'}}>No guesswork. Just the topics that matter, ranked by probability.</p>
          </div></FadeIn>
          <div className="section-grid-3">
            {[
              {num:'01',icon:'📚',title:'Enter your details',body:'Subject, exam date, topics — or upload your syllabus PDF. Done in 30 seconds.'},
              {num:'02',icon:'🧠',title:'AI ranks what matters',body:'Prepzo scores every topic by exam probability and picks your mode — Survival, Balanced, or Full.'},
              {num:'03',icon:'🎯',title:'Study with precision',body:'A ranked question list with difficulty tags, priority badges, and an AI chatbot on standby.'},
            ].map((s,i)=>(
              <FadeIn key={i} delay={i*0.13}><div style={{background:C.surface,border:`1.5px solid ${C.border}`,borderRadius:20,padding:'32px 28px',height:'100%',boxSizing:'border-box',transition:'box-shadow 0.2s,border-color 0.2s'}}
                onMouseEnter={e=>{e.currentTarget.style.boxShadow='0 8px 32px rgba(108,99,255,0.10)';e.currentTarget.style.borderColor='#C8C4FF'}}
                onMouseLeave={e=>{e.currentTarget.style.boxShadow='none';e.currentTarget.style.borderColor=C.border}}>
                <span style={{display:'inline-block',background:C.accentSoft,borderRadius:999,padding:'3px 11px',marginBottom:20,fontFamily:fontM,fontSize:11,color:C.accent,letterSpacing:'0.06em'}}>{s.num}</span>
                <div style={{fontSize:32,marginBottom:14}}>{s.icon}</div>
                <h3 style={{fontFamily:fontD,fontWeight:600,fontSize:19,color:C.text,letterSpacing:'-0.02em',marginBottom:10}}>{s.title}</h3>
                <p style={{fontFamily:fontD,fontSize:14,color:C.muted,lineHeight:1.65}}>{s.body}</p>
              </div></FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* MODES */}
      <section style={{background:C.bg}} className="section-pad" id="modes">
        <div style={{maxWidth:1100,margin:'0 auto'}}>
          <FadeIn><div style={{marginBottom:44}}>
            <Label>STUDY MODES</Label>
            <h2 style={{fontFamily:fontD,fontWeight:700,fontSize:'clamp(28px,4vw,48px)',color:C.text,letterSpacing:'-0.04em'}}>Pick your battle.</h2>
          </div></FadeIn>
          <div className="modes-grid">
            {[
              {badge:'🔥 3 DAYS OR LESS',color:'#E8341C',title:'Survival',body:'Only the highest-probability questions. Pure Pareto — 20% of topics, 80% of marks.',features:['Top 5 must-do topics','Only Must questions','Fastest possible prep']},
              {badge:'⚡ 4–7 DAYS',color:'#D4910A',title:'Balanced',body:'Smart coverage across priority topics. Hit what matters without burning out.',features:['Priority + Should topics','Medium question set','Covers exam pattern gaps']},
              {badge:'🎯 7+ DAYS',color:'#0D9E6E',title:'Full Prep',body:'Comprehensive. Every topic weighted, every question type covered.',features:['All topics, all types','Theory + Coding + MCQ','AI chatbot for every Q']},
            ].map((m,i)=>(
              <FadeIn key={i} delay={i*0.11}><div style={{background:C.dark,border:'1px solid #2A2240',borderRadius:20,padding:'32px 28px',transition:'transform 0.2s'}}
                onMouseEnter={e=>e.currentTarget.style.transform='translateY(-4px)'}
                onMouseLeave={e=>e.currentTarget.style.transform='translateY(0)'}>
                <span style={{display:'inline-block',background:`${m.color}22`,border:`1px solid ${m.color}`,borderRadius:999,padding:'4px 12px',marginBottom:20,fontFamily:fontM,fontSize:10,color:m.color,letterSpacing:'0.06em'}}>{m.badge}</span>
                <h3 style={{fontFamily:fontD,fontWeight:700,fontSize:26,color:C.textInv,letterSpacing:'-0.03em',marginBottom:10}}>{m.title}</h3>
                <p style={{fontFamily:fontD,fontSize:14,color:C.mutedInv,lineHeight:1.7,marginBottom:24}}>{m.body}</p>
                <ul style={{listStyle:'none',padding:0,margin:0,display:'flex',flexDirection:'column',gap:8}}>
                  {m.features.map(f=><li key={f} style={{fontFamily:fontD,fontSize:13,color:'rgba(240,240,255,0.7)',display:'flex',alignItems:'center',gap:10}}><span style={{color:m.color,fontWeight:700}}>✓</span>{f}</li>)}
                </ul>
              </div></FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section style={{background:C.surface,borderTop:`1px solid ${C.border}`}} className="section-pad">
        <div style={{maxWidth:1100,margin:'0 auto'}}>
          <FadeIn><div style={{textAlign:'center',marginBottom:56}}>
            <Label>WHAT YOU GET</Label>
            <h2 style={{fontFamily:fontD,fontWeight:700,fontSize:'clamp(26px,3.5vw,44px)',color:C.text,letterSpacing:'-0.04em'}}>Everything you need.<br/>Nothing you don't.</h2>
          </div></FadeIn>
          <div className="section-grid-6">
            {[
              {icon:'📊',title:'Probability scores',body:'Every question ranked by exam likelihood based on topic weight and frequency.'},
              {icon:'🏷️',title:'Priority badges',body:'Must / Should / Optional — so you know exactly where to start studying.'},
              {icon:'💬',title:'AI chatbot',body:'Ask Prepzo to explain any question, simplify a concept, or go deeper.'},
              {icon:'📄',title:'PDF syllabus parse',body:'Upload your syllabus and Prepzo auto-detects all topics instantly.'},
              {icon:'🔍',title:'Smart filters',body:'Filter by difficulty, type, or priority. See only what matters right now.'},
              {icon:'📅',title:'Deadline-aware',body:'The closer your exam, the more aggressive Prepzo gets on focusing what counts.'},
            ].map((f,i)=>(
              <FadeIn key={i} delay={i*0.07}><div style={{background:C.bg,border:`1.5px solid ${C.border}`,borderRadius:16,padding:'26px 22px',transition:'border-color 0.2s'}}
                onMouseEnter={e=>e.currentTarget.style.borderColor='#C8C4FF'}
                onMouseLeave={e=>e.currentTarget.style.borderColor=C.border}>
                <div style={{fontSize:26,marginBottom:12}}>{f.icon}</div>
                <h4 style={{fontFamily:fontD,fontWeight:600,fontSize:15,color:C.text,letterSpacing:'-0.02em',marginBottom:8}}>{f.title}</h4>
                <p style={{fontFamily:fontD,fontSize:13,color:C.muted,lineHeight:1.6}}>{f.body}</p>
              </div></FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* STATS */}
      <section style={{background:C.dark}} className="section-pad">
        <div style={{maxWidth:900,margin:'0 auto'}}>
          <div className="stats-grid">
            {[
              {v:'25+',l:'Students in beta'},
              {v:'3',l:'Study modes'},
              {v:'85%',l:'Question accuracy'},
              {v:'30s',l:'Plan generation time'},
            ].map((s,i)=>(
              <FadeIn key={i} delay={i*0.1}><div className={i<3?'stat-divider':''} style={{textAlign:'center',padding:'0 24px'}}>
                <div style={{fontFamily:fontM,fontWeight:700,fontSize:'clamp(32px,4vw,52px)',color:C.textInv,letterSpacing:'-0.04em',marginBottom:8}}>{s.v}</div>
                <div style={{fontFamily:fontD,fontSize:13,color:C.mutedInv}}>{s.l}</div>
              </div></FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* QUOTE */}
      <section style={{background:C.bg}} className="section-pad">
        <div style={{maxWidth:780,margin:'0 auto',textAlign:'center'}}>
          <FadeIn>
            <div style={{fontSize:40,marginBottom:24,opacity:0.15,fontFamily:'Georgia,serif',color:C.accent}}>"</div>
            <p style={{fontFamily:fontD,fontWeight:700,fontSize:'clamp(20px,3vw,36px)',color:C.text,letterSpacing:'-0.03em',lineHeight:1.35,marginBottom:28}}>
              We are not another AI study tool — we are a{' '}<span style={{color:C.accent}}>decision engine</span>{' '}that tells students exactly what to study when time is limited.
            </p>
            <div style={{fontFamily:fontM,fontSize:12,color:C.muted,letterSpacing:'0.06em'}}>— PREPZO TEAM · NST 2026</div>
          </FadeIn>
        </div>
      </section>

      {/* FINAL CTA */}
      <section style={{background:C.darkest}} className="section-pad">
        <div style={{maxWidth:600,margin:'0 auto',textAlign:'center'}}>
          <FadeIn>
            <div style={{width:280,height:280,borderRadius:'50%',background:'radial-gradient(circle,rgba(108,99,255,0.22) 0%,transparent 70%)',margin:'0 auto',marginBottom:-140,pointerEvents:'none'}}/>
            <h2 style={{fontFamily:fontD,fontWeight:700,fontSize:'clamp(32px,5vw,60px)',color:C.textInv,letterSpacing:'-0.04em',lineHeight:1.05,marginBottom:18,position:'relative'}}>
              Your next exam.<br/><span style={{color:C.accent}}>Decoded.</span>
            </h2>
            <p style={{fontFamily:fontD,fontSize:16,color:C.mutedInv,lineHeight:1.6,maxWidth:380,margin:'0 auto 40px'}}>Join students who stopped guessing and started studying what actually matters.</p>
            <CTAButton large accent label="Get started free"/>
            <p style={{fontFamily:fontM,fontSize:11,color:'rgba(240,240,255,0.2)',marginTop:18,letterSpacing:'0.05em'}}>FREE DURING BETA · NO CREDIT CARD</p>
          </FadeIn>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="footer-row" style={{background:C.darkest,borderTop:'1px solid rgba(255,255,255,0.06)',display:'flex',justifyContent:'space-between',alignItems:'center'}}>
        <span style={{fontFamily:fontD,fontWeight:700,fontSize:16,color:C.textInv,letterSpacing:'-0.03em'}}>Prepzo<span style={{color:C.accent}}>.ai</span></span>
        <span style={{fontFamily:fontM,fontSize:11,color:'rgba(240,240,255,0.22)',letterSpacing:'0.05em'}}>2026 · NST TEAM · BUILT WITH ❤️</span>
      </footer>
    </div>
  );
}
