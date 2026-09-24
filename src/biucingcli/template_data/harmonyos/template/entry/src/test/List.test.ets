import { describe, expect, it } from '@ohos/hypium';
import { AnalysisService, Cancellation } from '@biucing/contracts';
import { HomeFactory } from '@biucing/homefeature';
import { SessionOwner } from '../main/ets/composition/SessionOwner';

class FakeAnalysis implements AnalysisService {
  closed: boolean = false;
  async analyze(values: string[], cancellation?: Cancellation): Promise<string> {
    expect(values.join(',')).assertEqual('20,22');
    return '42';
  }
  async close(): Promise<void> { this.closed = true; }
}
export default function testsuite() {
  describe('{{PROJECT_NAME}} component contracts', () => {
    it('keeps generated app identity available', 0, () => {
      expect('{{BUNDLE_NAME}}'.length > 0).assertTrue();
      expect('{{HARMONY_MODULE_NAME}}'.length > 0).assertTrue();
      expect('{{ABILITY_NAME}}'.length > 0).assertTrue();
    });
    it('runs the published feature through its public factory with a fake service', 0, async () => {
      const service = new FakeAnalysis();
      const model = new HomeFactory(service).create();
      expect(await model.calculate()).assertEqual('42');
      await model.close();
      expect(service.closed).assertTrue();
    });
    it('retains owner state and closes its model exactly once', 0, async () => {
      const firstService = new FakeAnalysis();
      const secondService = new FakeAnalysis();
      const first = new SessionOwner(new HomeFactory(firstService));
      const second = new SessionOwner(new HomeFactory(secondService));
      const retained = first.home;
      await retained.calculate();
      expect(first.home === retained).assertTrue();
      expect(first.home.result).assertEqual('42');
      const completion = first.close();
      expect(first.close() === completion).assertTrue();
      await completion;
      let rejected = false;
      try { await retained.calculate(); } catch (_) { rejected = true; }
      expect(rejected).assertTrue();
      expect(secondService.closed).assertFalse();
      expect(await second.home.calculate()).assertEqual('42');
      await second.close();
    });
    it('cancellation notifies once and respects subscription removal', 0, () => {
      const signal = new Cancellation();
      let called = 0;
      const remove = signal.subscribe(() => { called += 100; });
      remove();
      signal.subscribe(() => { called += 1; });
      signal.cancel(); signal.cancel();
      expect(called).assertEqual(1);
      expect(signal.cancelled).assertTrue();
    });
  });
}
