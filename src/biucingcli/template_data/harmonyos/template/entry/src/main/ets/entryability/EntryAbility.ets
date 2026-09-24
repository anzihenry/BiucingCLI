import { Application } from '../composition/Application';
import { SessionOwner } from '../composition/SessionOwner';
import AbilityConstant from '@ohos.app.ability.AbilityConstant';
import UIAbility from '@ohos.app.ability.UIAbility';
import Want from '@ohos.app.ability.Want';
import hilog from '@ohos.hilog';
import window from '@ohos.window';

const DOMAIN = 0x0000;
const TAG = '{{ABILITY_NAME}}';

export default class {{ABILITY_NAME}} extends UIAbility {
  private application: Application = new Application();
  private session: SessionOwner | undefined = undefined;

  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    hilog.info(DOMAIN, TAG, 'Ability created for {{DISPLAY_NAME_JS_SINGLE}}.');
  }

  onWindowStageCreate(windowStage: window.WindowStage): void {
    const session = this.application.createSession();
    this.session = session;
    const storage = new LocalStorage();
    storage.setOrCreate('homeModel', session.home);
    windowStage.loadContent('pages/Index', storage, (error) => {
      if (error.code) {
        this.closeSession(session);
        hilog.error(DOMAIN, TAG, 'Failed to load content. code=%{public}d message=%{public}s', error.code, error.message);
        return;
      }

      hilog.info(DOMAIN, TAG, 'Loaded {{DISPLAY_NAME_JS_SINGLE}} content.');
    });
  }

  // A hidden/background window retains its session. Only destruction ends ownership.
  onWindowStageDestroy(): void {
    if (this.session) { this.closeSession(this.session); }
    this.session = undefined;
  }

  private closeSession(session: SessionOwner): void {
    session.close().then(() => {
      hilog.info(DOMAIN, TAG, 'Business session closed.');
    }).catch((error: Error) => {
      hilog.error(DOMAIN, TAG, 'Session close failed: %{public}s', error.message);
    });
  }

  onDestroy(): void {
    if (this.session) { this.closeSession(this.session); }
    this.session = undefined;
    hilog.info(DOMAIN, TAG, 'Ability destroyed.');
  }
}
