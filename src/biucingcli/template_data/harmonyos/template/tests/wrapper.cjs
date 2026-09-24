const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require(process.argv[3]);
const root = path.resolve(__dirname, '..');
const native = require(process.argv[2]);
const cache = new Map();
function load(file) {
  if (cache.has(file)) return cache.get(file).exports;
  const module = { exports: {} };
  cache.set(file, module);
  const source = fs.readFileSync(file, 'utf8');
  const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, esModuleInterop: true } }).outputText;
  const localRequire = id => {
    if (id === 'libbiucing_shared.so') return native;
    if (id === '@biucing/contracts') return load(path.join(root, 'components/contracts/Index.ets'));
    return load(path.resolve(path.dirname(file), id + '.ets'));
  };
  new vm.Script('(function(require, module, exports) {' + compiled + '\n})', { filename: file }).runInThisContext()(localRequire, module, module.exports);
  return module.exports;
}
(async () => {
  const { SharedCoreFactory } = load(path.join(root, 'components/sharedcore/src/main/ets/SharedCore.ets'));
  const { Cancellation } = load(path.join(root, 'components/contracts/Index.ets'));
  const factory = new SharedCoreFactory();
  const a = factory.create(), b = factory.create();
  const inputs = ['20', '22'];
  const copied = a.analyze(inputs); inputs[0] = '100';
  assert.equal(await copied, '42');
  assert.deepEqual(await Promise.all([a.analyze(['1']), a.analyze(['2']), b.analyze(['3'])]), ['1', '2', '3']);
  const token = new Cancellation(); token.cancel();
  await assert.rejects(a.analyze(['10'], token), e => e.code === 3);
  const activeToken = new Cancellation();
  const pending = a.analyze(Array(100000).fill('1'), activeToken);
  await Promise.resolve(); activeToken.cancel();
  try { assert.equal(await pending, '100000'); } catch (e) { assert.equal(e.code, 3); }
  const first = a.analyze(Array(10000).fill('1'));
  const queued = a.analyze(['5']);
  const results = Promise.allSettled([first, queued]);
  const closing = a.close();
  assert.equal(a.close(), closing);
  await closing;
  assert.ok((await results).every(r => r.status === 'rejected' && r.reason.code === 4));
  await assert.rejects(a.analyze(['1']), e => e.code === 4);
  assert.equal(await b.analyze(['9223372036854775807']), '9223372036854775807');
  await b.close();
  const c = factory.create();
  const running = c.analyze(Array(100000).fill('1'));
  const observed = Promise.allSettled([running]);
  await Promise.resolve(); // Allow the queue to submit the real native work.
  await c.close();
  const finished = (await observed)[0];
  if (finished.status === 'rejected') assert.equal(finished.reason.code, 3);
  else assert.equal(finished.value, '100000');
  await assert.rejects(c.analyze(['1']), e => e.code === 4);
  const { HomeFactory } = load(path.join(root, 'components/homefeature/src/main/ets/HomeModel.ets'));
  let closed = false;
  const fake = { analyze: async values => { assert.deepEqual(values, ['20', '22']); return '42'; }, close: async () => { closed = true; } };
  const home = new HomeFactory(fake).create();
  assert.equal(await home.calculate(), '42'); await home.close(); assert.equal(closed, true);
  console.log('ArkTS source on host: serial queue, defensive copy, cancellation, async close, isolation and injected HomeFactory passed');
})().catch(error => { console.error(error); process.exitCode = 1; });
