import AbilityConstant from '@ohos.app.ability.AbilityConstant';
import UIAbility from '@ohos.app.ability.UIAbility';
import Want from '@ohos.app.ability.Want';
import hilog from '@ohos.hilog';
import window from '@ohos.window';

const DOMAIN = 0x0000;
const TAG = '{{ABILITY_NAME}}';

export default class {{ABILITY_NAME}} extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    hilog.info(DOMAIN, TAG, 'Ability created for {{DISPLAY_NAME}}.');
  }

  onWindowStageCreate(windowStage: window.WindowStage): void {
    windowStage.loadContent('pages/Index', (error) => {
      if (error.code) {
        hilog.error(DOMAIN, TAG, 'Failed to load content. code=%{public}d message=%{public}s', error.code, error.message);
        return;
      }

      hilog.info(DOMAIN, TAG, 'Loaded {{DISPLAY_NAME}} content.');
    });
  }

  onDestroy(): void {
    hilog.info(DOMAIN, TAG, 'Ability destroyed.');
  }
}
