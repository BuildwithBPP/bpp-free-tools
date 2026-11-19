const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const htmlPath = path.join(__dirname, 'index.html');
const html = fs.existsSync(htmlPath) ? fs.readFileSync(htmlPath, 'utf8') : '';
const script = html.match(/<script id="bpp-money-allocator-core">([\s\S]*?)<\/script>/)?.[1] || '';
const context = {};
vm.createContext(context);
if (script) vm.runInContext(script, context);
function engine() {
  assert.equal(typeof context.BPPAllocator?.calculate, 'function', 'Calculator engine not implemented');
  return context.BPPAllocator;
}
const base = overrides => ({ revenue:'18000', expenses:'10000', cash:'17000', commitments:'0', taxRate:'28', businessType:'service', growthMode:'stable', ownerMethod:'draw', ownerBaseline:'1000', reserveMonths:'3', period:'Example month', ...overrides });

test('draw shortfall explains requested pay, available profit, gap and cash support', () => {
  const r=engine().calculate(base({ownerBaseline:'4790'}));
  const explanation=engine().drawExplanation(r);
  for(const amount of ['$4,790.00','$4,320.00','$470.00','$4,184.00']) assert.ok(explanation.includes(amount),amount);
  assert.ok(engine().summary(r).includes(explanation));
});
test('pay already in expenses is described as included rather than a missing draw', () => {
  const r=engine().calculate(base({ownerMethod:'expense'}));
  assert.match(engine().drawExplanation(r),/already included in business costs/);
  assert.doesNotMatch(engine().drawExplanation(r),/gap|You entered/);
});

test('approved profit waterfall reconciles every cent and limits extra draws by cash', () => {
  const r = engine().calculate(base());
  assert.equal(r.valid, true);
  assert.equal(r.profit, 800000);
  assert.equal(r.tax, 224000);
  assert.equal(r.afterTaxProfit, 576000);
  assert.equal(r.savings, 86400);
  assert.equal(r.growth, 57600);
  assert.equal(r.baselinePlan, 100000);
  assert.equal(r.extraPlan, 66400);
  assert.equal(r.ownerPlan, 166400);
  assert.equal(r.unassignedProfit, 265600);
  assert.equal(r.expenses + r.tax + r.savings + r.growth + r.ownerPlan + r.unassignedProfit, r.revenue);
  assert.equal(r.baselineCash, 100000);
  assert.equal(r.extraCash, 0);
  assert.equal(r.ownerCash, 100000);
  assert.equal(r.status, 'yellow');
});
test('earmarking savings never increases the cash balance', () => {
  const r = engine().calculate(base());
  assert.equal(r.currentRunway, 1.7);
  assert.equal(r.cashAfterPlan, 1542400);
  assert.equal(r.cashAfterPlan, r.cash-r.commitments-r.growthCash-r.ownerCash);
  assert.equal(r.operatingCashAfter, r.cashAfterPlan-r.tax);
  assert.ok(r.cashAfterPlan <= r.cash);
  assert.equal(r.reserveGapAfter, r.reserveTarget-r.operatingCashAfter);
});
test('salary included in expenses is not deducted as a second baseline', () => {
  const r = engine().calculate(base({ownerMethod:'expense',ownerBaseline:'4000',cash:'50000'}));
  assert.equal(r.profit, 800000);
  assert.equal(r.baselinePlan, 0);
  assert.equal(r.extraPlan, 97920);
  assert.equal(r.ownerCash, 97920);
});
test('extra payment respects the business-type cash threshold after growth and baseline', () => {
  for (const [businessType,threshold] of [['service',1.5],['mixed',1.8],['product',2]]) {
    const r = engine().calculate(base({businessType,cash:'60000',ownerBaseline:'0'}));
    assert.ok(r.extraCash > 0);
    assert.ok(r.afterRunway >= threshold);
    assert.equal(r.status,'green');
  }
});
test('red takes precedence over an otherwise positive margin', () => {
  const r = engine().calculate(base({cash:'9000'}));
  assert.equal(r.status,'red');
  assert.equal(r.ownerCash,0);
  assert.equal(r.growthCash,0);
});
test('low margin remains yellow even with plenty of cash; no extra payout', () => {
  const r = engine().calculate(base({revenue:'10800',expenses:'10000',cash:'50000',ownerBaseline:'0'}));
  assert.equal(r.status,'yellow');
  assert.equal(r.extraCash,0);
});
test('loss mode makes no new positive-profit allocation or owner draw', () => {
  const r = engine().calculate(base({revenue:'8000',cash:'50000'}));
  assert.equal(r.profit,-200000);
  assert.equal(r.operationsShortfall,200000);
  for (const key of ['tax','savings','growth','baselinePlan','extraPlan','ownerPlan','ownerCash']) assert.equal(r[key],0,key);
  assert.equal(r.status,'yellow');
});
test('explicit zero differs from a missing amount and zero costs cannot imply infinite runway', () => {
  const e=engine();
  assert.equal(e.calculate(base({revenue:''})).valid,false);
  const r=e.calculate(base({revenue:'0',expenses:'0',cash:'0'}));
  assert.equal(r.valid,true);
  assert.equal(r.margin,null);
  assert.equal(r.currentRunway,null);
  assert.equal(r.cashCheckAvailable,false);
  assert.equal(r.status,'yellow');
});
test('invalid numbers and out-of-range policy settings are rejected', () => {
  const e=engine();
  for (const overrides of [{revenue:'-1'},{cash:'1e8'},{expenses:'1.001'},{taxRate:'41'},{taxRate:'14.99'},{reserveMonths:'4'},{businessType:'unknown'},{commitments:'NaN'}]) {
    assert.equal(e.calculate(base(overrides)).valid,false,JSON.stringify(overrides));
  }
});
test('inherited object names cannot masquerade as supported settings', () => {
  for(const field of ['businessType','growthMode'])for(const value of ['toString','constructor','__proto__']) {
    assert.equal(engine().calculate(base({[field]:value})).valid,false);
  }
});
test('selected cushion target remains distinct from minimum payment threshold', () => {
  const r=engine().calculate(base({cash:'30000',reserveMonths:'6'}));
  assert.equal(r.status,'green');
  assert.ok(r.reserveGapAfter>0);
  assert.ok(r.afterRunway<6);
});
test('commitments equal to cash leave no supported payments or available operating cash', () => {
  const r=engine().calculate(base({cash:'17000',commitments:'17000'}));
  assert.equal(r.ownerCash,0); assert.equal(r.growthCash,0);
  assert.equal(r.operatingCashAfter,0); assert.equal(r.taxCashShortfall,r.tax);
});
test('currency parsing rejects malformed separators and out-of-range values', () => {
  const e=engine();
  assert.equal(e.money('$1,234.56'),123456);
  assert.equal(e.money('999999999.99'),99999999999);
  for(const value of ['12,34','1,2,3','1e6','Infinity','1000000000','-0.01'])assert.equal(e.money(value),null,value);
});
test('reserve rates follow business type, then change to 5% when the cash goal is met', () => {
  for (const [businessType,bps] of [['service',1500],['product',2000],['mixed',1800]]) {
    const r=engine().calculate(base({businessType}));
    assert.equal(r.reserveRateBps,bps);
  }
  const full=engine().calculate(base({cash:'100000'}));
  assert.equal(full.reserveRateBps,500);
});
test('unpaid commitments and new tax holds reduce the owner-pay check', () => {
  const r=engine().calculate(base({cash:'50000',commitments:'49000'}));
  assert.equal(r.status,'red');
  assert.equal(r.ownerCash,0);
  assert.ok(r.taxCashShortfall>0);
  const committed=engine().calculate(base({cash:'1000',commitments:'2000'}));
  assert.equal(committed.commitmentShortfall,100000);
});
test('small rounding-sensitive inputs preserve the revenue allocation identity', () => {
  for (const revenue of ['0.01','10.01','999.99','9999.99','123456.78']) {
    const r=engine().calculate(base({revenue,expenses:'0.01',cash:'50000',ownerBaseline:'0',taxRate:'28.17',growthMode:'aggressive'}));
    assert.equal(r.valid,true);
    assert.equal(r.expenses+r.tax+r.savings+r.growth+r.ownerPlan+r.unassignedProfit,r.revenue);
  }
});
test('CSV and copy summary identify assumptions and treat user text as text', () => {
  const e=engine();
  const r=e.calculate(base({period:'=HYPERLINK("https://example.invalid")'}));
  const csv=e.toCSV(r);
  assert.ok(csv.includes("'=HYPERLINK"));
  assert.ok(csv.includes('Owner pay supported by this cash check'));
  assert.ok(e.summary(r).includes('not tax calculations or industry standards'));
  assert.ok(e.summary(r).includes('Cash Already Held Today'));
  assert.ok(e.summary(r).includes('Profit is not added to this balance again'));
});

test('report keeps numeric values for Excel and separates planned pay from supported pay',()=>{
 const e=engine(),r=e.calculate(base()),rows=e.reportRows(r),get=label=>rows.find(row=>row.label===label);
 assert.equal(get('Monthly Profit').value,8000);
 assert.equal(get('Profit Margin').value,8000/18000);
 assert.equal(get('Owner Pay in the Profit Plan').value,1664);
 assert.equal(get('Owner Pay Supported by Cash').value,1000);
 assert.equal(get('Available After the Tax Hold').value,13184);
 assert.equal(e.reportValue(get('Profit Margin')),'44.44%');
 assert.ok(e.summary(r).includes('YOUR ALLOCATION PLAN'));
});

test('zero-cost report marks cash support unavailable and preserves zero profit',()=>{
 const e=engine(),r=e.calculate(base({revenue:'0',expenses:'0',cash:'0',ownerBaseline:'0'})),rows=e.reportRows(r),get=label=>rows.find(row=>row.label===label);
 assert.equal(get('Monthly Profit').value,0);
 for(const label of ['Owner Pay Supported by Cash','Baseline Draw Supported','Extra Distribution Supported','Growth Supported by Cash','Current Cash Runway'])assert.equal(get(label).value,'Not assessed');
 assert.equal(get('Profit Margin').value,'Not available');
 assert.deepEqual(Array.from(e.reportRows({valid:false})),[]);
});
test('all settings preserve cash limits and the revenue allocation identity', () => {
  const e=engine();
  for(const businessType of ['service','product','mixed'])for(const growthMode of ['stable','growth','aggressive'])for(const ownerMethod of ['draw','expense'])for(const revenue of ['0','999.99','1080','18000'])for(const cash of ['0','700','1100','50000']){
    const r=e.calculate(base({businessType,growthMode,ownerMethod,revenue,cash,expenses:'1000',commitments:'50',ownerBaseline:'125.23'}));
    assert.equal(r.valid,true);
    assert.ok(r.ownerCash>=0&&r.growthCash>=0);
    assert.ok(r.ownerCash+r.growthCash<=Math.max(0,r.cash-r.commitments-r.tax));
    assert.ok(r.cashAfterPlan<=Math.max(0,r.cash-r.commitments));
    if(r.profit>=0)assert.equal(r.expenses+r.tax+r.savings+r.growth+r.ownerPlan+r.unassignedProfit,r.revenue);
    if(r.extraCash>0){assert.ok(r.afterRunway>=r.thresholdMonths);assert.ok(r.margin>=0.1);}
    if(r.status==='red')assert.equal(r.ownerCash,0);
  }
});
