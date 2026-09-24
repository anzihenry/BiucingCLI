import deviceInfo from '@ohos.deviceInfo';
import { DeviceProfile, FeatureStyle, HomeOutput } from '@biucing/contracts';
import { HomeView, HomeModel } from '@biucing/homefeature';
import { Application } from '../composition/Application';
import { createHomeFactory } from '../composition/GeneratedGraph';
import { AppConfig } from '../core/config/AppConfig';

@Entry
@Component
struct Index {
  private style: FeatureStyle = new FeatureStyle();
  aboutToAppear(): void { this.style.title = AppConfig.displayName; }
  private profile(): DeviceProfile {
    if (deviceInfo.deviceType === 'wearable') { return DeviceProfile.Watch; }
    if (deviceInfo.deviceType === 'tv') { return DeviceProfile.TV; }
    if (deviceInfo.deviceType === '2in1') { return DeviceProfile.Desktop; }
    return DeviceProfile.Mobile;
  }
  build() {
    Column() {
      HomeView({ createModel: (): HomeModel => createHomeFactory((AppStorage.get<Application>('application') || new Application()).sessions).create(), profile: this.profile(), style: this.style,
      onOutput: (output: HomeOutput) => {
        if (output === HomeOutput.OpenSettings) {
          this.getUIContext().getRouter().pushUrl({ url: 'pages/Settings' });
        }
      } })
    }.width('100%').height('100%')
  }
}
