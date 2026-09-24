import { describe, expect, it } from '@ohos/hypium';
import { Cancellation } from '@biucing/contracts';
import { SharedCoreFactory } from '@biucing/sharedcore';
export default function testsuite() {
  describe('Published SharedCore on HarmonyOS', () => {
    it('calls the real binary and preserves int64 values', 0, async () => {
      const session = new SharedCoreFactory().create();
      try {
        expect(await session.analyze(['20', '22'])).assertEqual('42');
        expect(await session.analyze(['9223372036854775807'])).assertEqual('9223372036854775807');
      } finally { await session.close(); }
    });
    it('isolates sessions and rejects cancelled or closed work', 0, async () => {
      const factory = new SharedCoreFactory();
      const a = factory.create();
      const b = factory.create();
      const token = new Cancellation(); token.cancel();
      let cancelled = false;
      try { await a.analyze(['1'], token); } catch (_) { cancelled = true; }
      expect(cancelled).assertTrue();
      await a.close(); await a.close();
      let closed = false;
      try { await a.analyze(['1']); } catch (_) { closed = true; }
      expect(closed).assertTrue();
      try { expect(await b.analyze(['7'])).assertEqual('7'); }
      finally { await b.close(); }
    });
  });
}
