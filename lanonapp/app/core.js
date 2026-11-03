/* LaNonApp SPSE v0.8.0. Domain logic without AI or network dependence.
   SPDX-License-Identifier: AGPL-3.0-or-later. Pre-alpha: NOT an emergency or medical service. */
(function (root, factory) {
  const core = factory();
  if (typeof module !== 'undefined' && module.exports) module.exports = core;
  if (root) root.LaNonCore = core;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const VERSION = 8;
  const EMPTY = () => ({ schema: VERSION,
    profile: {name:'', persona:'nona', proactivity:'equilibrada'},
    tasks:[], objects:[], medications:[], habits:[], transactions:[], positions:[],
    contacts:[], content:[], grants:[], events:[], incidents:[],
    preferences:{voice:false, screenReader:false}, createdAt:new Date().toISOString() });
  function uuid() { return typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : 'id-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2); }
  function plain(v) { return String(v == null ? '' : v).trim(); }
  function normalize(raw) {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw) || Number(raw.schema)>VERSION) throw Error('Formato no compatible');
    const init=EMPTY(), out={...init,...raw};
    for (const key of ['tasks','objects','medications','habits','transactions','positions','contacts','content','grants','events','incidents']) {
      if (!Array.isArray(out[key])) throw Error('Colección inválida: '+key);
      if (out[key].length>50000) throw Error('Colección excesiva');
    }
    out.profile={...init.profile,...(raw.profile||{})};
    out.preferences={...init.preferences,...(raw.preferences||{})};
    out.schema=VERSION;
    return out;
  }
  function addEvent(s, type, details, options={}) {
    const e={id:uuid(),type,at:new Date().toISOString(),provenance:options.provenance||'user_manual',
      certainty:options.certainty||'declared',subject:options.subject||'local_user',
      details:details||{}};
    s.events.push(e);
    return e;
  }
  function sameDayLocal(iso, day=new Date()) {
    const d=new Date(iso);return !Number.isNaN(d.valueOf()) && d.toDateString()===new Date(day).toDateString();
  }
  function parseDate(x) {const d=new Date(x);return !Number.isNaN(d.valueOf())?d:null;}
  function dueTasks(s, now=new Date()) {
    const today=new Date(now);today.setHours(23,59,59,999);
    return s.tasks.filter(x=>!x.done && x.due && parseDate(x.due) && parseDate(x.due)<=today)
      .sort((a,b)=>new Date(a.due)-new Date(b.due));
  }
  function medicationEpisode(medId, date=new Date()){
    // Date-only key for a user's LOCAL-clock daily reminders; not an interval dosing algorithm.
    const d=new Date(date);return medId+'@'+[d.getFullYear(),String(d.getMonth()+1).padStart(2,'0'),String(d.getDate()).padStart(2,'0')].join('-');
  }
  function medStatus(s, medId, date=new Date()){
    const episode=medicationEpisode(medId,date);
    const ev=s.events.filter(e=>e.details && e.details.episode===episode && e.type.startsWith('med.'));
    const taken=ev.some(e=>e.type==='med.taken_self_reported');
    const negative=new Set(ev.filter(e=>e.type==='med.refused'||e.type==='med.deferred').map(e=>e.details.interactionId));
    return {episode,taken, negatives:negative.size, status:taken?'taken_self_reported':negative.size?'refused_or_deferred':'unconfirmed'};
  }
  function recordMedication(s, medId, action, when=new Date(), interactionId) {
    const med=s.medications.find(x=>x.id===medId);
    if (!med)throw Error('Pauta no encontrada');
    if (!['taken_self_reported','refused','deferred','unconfirmed'].includes(action))throw Error('Acción no permitida');
    const ep=medicationEpisode(medId,when), status=medStatus(s,medId,when);
    if(status.taken && action!=='taken_self_reported') return {incident:null,status};
    const interaction=interactionId||uuid();
    if(s.events.some(e=>e.details && e.details.interactionId===interaction && e.details.episode===ep))return {incident:null,status};
    addEvent(s, 'med.'+action,{medId,episode:ep,interactionId:interaction,planVersion:med.planVersion||'user_entered'});
    const next=medStatus(s,medId,when);
    if(next.negatives>=2&&!next.taken) {
      const id='spse-med:'+ep;
      if (!s.incidents.some(i=>i.id===id)) {
        const recipient=s.contacts.find(c=>c.scopes && c.scopes.includes('medication'))||null;
        const incident={id,createdAt:new Date(when).toISOString(),kind:'medication_followup',medId,
          status:'local_intent_only',recipientId:recipient?recipient.id:null,
          note:'Dos negativas o aplazamientos explícitos; no se ha enviado ningún aviso.'};
        s.incidents.push(incident);
        addEvent(s,'spse.intent_created',{incidentId:id,recipientId:incident.recipientId},{certainty:'derived'});
        return {incident,status:next};
      }
    }
    return {incident:null,status:next};
  }
  function validateGrant(g,cap,at=new Date()) {
    if(!g || !Array.isArray(g.scopes)||!g.scopes.includes(cap)||g.revokedAt)return false;
    if(g.validFrom&&new Date(g.validFrom)>at)return false;
    if(g.validTo&&new Date(g.validTo)<at)return false;
    return g.verified===true;
  }
  function authorize(state, actor, scope, at=new Date()) {
    // No family root inferred from relation. All grants require an explicit verified record.
    return state.grants.some(g=>g.actor===actor && validateGrant(g,scope,at));
  }
  function projection(input) {
    const f=['cash','monthlyIncome','monthlyExpenses','exceptional','reserve','months'];
    for(const x of f)if(input[x]===''||input[x]===null||input[x]===undefined||!Number.isFinite(Number(input[x])))throw Error('Dato faltante o no numérico: '+x);
    const o=Object.fromEntries(f.map(k=>[k,Number(input[k])]));
    if(o.months<0||o.months>1200||!Number.isInteger(o.months)||o.monthlyExpenses<0||o.exceptional<0||o.reserve<0)throw Error('Parámetros fuera del dominio');
    const balance=o.cash+o.months*(o.monthlyIncome-o.monthlyExpenses)-o.exceptional;
    return {balance,aboveReserve:balance-o.reserve,netFlow:o.monthlyIncome-o.monthlyExpenses,assumptions:o,kind:'deterministic_conditional_not_forecast'};
  }
  function moneyTotals(s,currency) {
    const rows=s.transactions.filter(x=>x.currency===currency);
    return {income:rows.filter(x=>x.kind==='income').reduce((a,b)=>a+Number(b.amount),0),
      expenses:rows.filter(x=>x.kind==='expense').reduce((a,b)=>a+Number(b.amount),0),
      currency,complete:false}; // No claim of comprehensive coverage.
  }
  function healthFresh(entry, now=new Date(),maxAgeHours=24) {
    if(!entry||!entry.observedAt||!parseDate(entry.observedAt))return {status:'unknown'};
    const age=(new Date(now)-new Date(entry.observedAt))/3600000;
    return {status:age>=0&&age<=maxAgeHours?'recent':'stale',ageHours:age};
  }
  function capabilities(){return {
    findItems:{status:'manual_registry',realTagControl:false},speech:{status:'browser_opt_in',offlineGuaranteed:false},
    medication:{status:'foreground_self_report',backgroundAlarm:false,clinical:false},
    spse:{status:'local_intent',remoteAlert:false,fallDetection:false},
    finance:{status:'manual_local',bankRead:false,payment:false},
    media:{status:'user_initiated_external_links',feeds:false},
    sensors:{status:'not_connected'},sync:{status:'not_connected',cloud:false}
  };}
  function escapeHTML(s){return plain(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  function safeWebURL(text){try{let url=new URL(text);if(url.protocol!=='https:')return null;return url.href;}catch{return null;}}
  function platformSearch(provider,query){const q=encodeURIComponent(plain(query)); const sources={
    youtube:'https://www.youtube.com/results?search_query='+q,
    news:'https://news.google.com/search?q='+q,
    archive:'https://archive.org/search?query='+q,
    wikipedia:'https://es.wikipedia.org/w/index.php?search='+q,
    podcasts:'https://www.youtube.com/results?search_query='+encodeURIComponent('podcast '+query),
    instagram:'https://www.instagram.com/',facebook:'https://www.facebook.com/'
  };return sources[provider]||null;}
  function checkInSituational(s,now=new Date()) {
    const due=dueTasks(s,now);
    const outstanding=s.incidents.filter(i=>i.status==='local_intent_only').length;
    return {dueTasks:due.length,localIntents:outstanding,
      message:outstanding?'Hay incidencias locales pendientes. No se ha avisado a contactos externos.':
        due.length?'Hay '+due.length+' tareas vencidas o para hoy.':'No hay obligaciones con vencimiento registradas para hoy.'};
  }
  return {VERSION,EMPTY,uuid,normalize,addEvent,parseDate,dueTasks,medicationEpisode,medStatus,recordMedication,validateGrant,authorize,projection,moneyTotals,healthFresh,capabilities,escapeHTML,safeWebURL,platformSearch,checkInSituational};
});
