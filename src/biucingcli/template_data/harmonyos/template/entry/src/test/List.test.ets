import { describe, expect, it } from '@ohos/hypium';

export default function testsuite() {
  describe('{{PROJECT_NAME}} starter smoke tests', () => {
    it('keeps generated app identity available', 0, () => {
      expect('{{BUNDLE_NAME}}'.length > 0).assertTrue();
      expect('{{HARMONY_MODULE_NAME}}'.length > 0).assertTrue();
      expect('{{ABILITY_NAME}}'.length > 0).assertTrue();
    });
  });
}
