const assert = require('node:assert/strict');
const core = require(process.argv[2]);
(async () => {
  const a = core.create(), b = core.create();
  assert.throws(() => core.analyze({}, ['1']), e => e.code === 1);
  assert.throws(() => core.close({}), e => e.code === 1);
  assert.equal(await core.analyze(a, ['9223372036854775807', '-1']), '9223372036854775806');
  await assert.rejects(core.analyze(a, ['9223372036854775807', '1']), e => e.code === 2);
  assert.equal(await core.analyze(a, ['20', '22']), '42');
  assert.equal(await core.analyze(b, ['-9223372036854775808']), '-9223372036854775808');
  for (const value of ['1.1', '9223372036854775808', '', '1\0junk']) {
    assert.throws(() => core.analyze(a, [value]), e => e.code === 1);
  }
  const pending = core.analyze(a, Array(1000000).fill('1'));
  assert.throws(() => core.analyze(a, ['1']), e => e.code === 1);
  assert.throws(() => core.close(a), e => e.code === 1);
  core.cancel(a);
  try { assert.equal(await pending, '1000000'); } catch (e) { assert.equal(e.code, 3); }
  assert.equal(await core.analyze(a, ['42']), '42');
  core.close(a); core.close(a);
  assert.throws(() => core.analyze(a, ['1']), e => e.code === 4);
  assert.equal(await core.analyze(b, ['7']), '7');
  core.close(b);
  let transient = core.create();
  const keptAlive = core.analyze(transient, ['12', '30']);
  transient = null;
  if (global.gc) global.gc();
  assert.equal(await keptAlive, '42');
  console.log('Native bridge: full int64, errors, cancellation, serial access, close, isolation, GC keepalive passed');
})().catch(e => { console.error(e); process.exitCode = 1; });
