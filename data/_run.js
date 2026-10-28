const mk = () => new Proxy(function(){}, { get: (t, k) => k === Symbol.toPrimitive ? () => "" : (k === "length" ? 0 : (k==="slice"? ()=>"" : mk())), set: () => true, apply: () => mk() });
const store = {};
global.document = { getElementById: id => store[id] ||= { innerHTML: "", textContent: "", appendChild(){}, querySelectorAll: () => [], set length(v){}, get length(){return 0}, onchange:null, oninput:null },
  createElement: () => ({ style: {}, setAttribute(){}, appendChild(){} }),
  createElementNS: () => ({ setAttribute(){}, addEventListener(){}, appendChild(){}, getBoundingClientRect: () => ({}) }) };
global.location = { hash: "" }; global.innerWidth = 1000;
eval(require("fs").readFileSync("_b.js", "utf8") + "\nconsole.log(DOSS.map(d=>[d.id,d.n,d.c,d.flags,d.p0[1],d.p12,d.pMax[1],d.pMin,d.pAvg,d.pEnd]));");
console.log(store.cmp.innerHTML.length, store.ledger.innerHTML.length, store["themes-t"].innerHTML.length);
