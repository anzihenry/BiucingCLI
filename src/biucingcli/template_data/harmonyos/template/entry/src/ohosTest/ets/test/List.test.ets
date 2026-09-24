import { describe, expect, it } from '@ohos/hypium';
import { Application } from '../../../main/ets/composition/Application';
import { Cancellation } from '@biucing/contracts';
import { SharedCoreFactory } from '@biucing/sharedcore';
export default function testsuite() {
  describe('Published SharedCore on HarmonyOS', () => {
    it('retains a window model and closes independent owners', 0, async () => {
      const application = new Application();
      const first = application.createSession();
      const second = application.createSession();
      const retained = first.home;
      try {
        expect(await retained.calculate()).assertEqual('42');
        expect(first.home === retained).assertTrue();
        expect(first.home.result).assertEqual('42');
        const completion = first.close();
        expect(first.close() === completion).assertTrue();
        await completion;
        let rejected = false;
        try { await retained.calculate(); } catch (_) { rejected = true; }
        expect(rejected).assertTrue();
        expect(await second.home.calculate()).assertEqual('42');
      } finally { await first.close(); await second.close(); }
    });
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
