import { describe, expect, it } from '@ohos/hypium';
import { AnalysisService, Cancellation } from '@biucing/contracts';
import { HomeFactory } from '@biucing/homefeature';

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
