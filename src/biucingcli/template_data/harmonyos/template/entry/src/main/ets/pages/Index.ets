import deviceInfo from '@ohos.deviceInfo';
import { DeviceProfile, FeatureStyle, HomeOutput } from '@biucing/contracts';
import { HomeView, HomeModel } from '@biucing/homefeature';
import { AppConfig } from '../core/config/AppConfig';

@Entry({ useSharedStorage: true })
@Component
struct Index {
  @LocalStorageLink('homeModel') private model: HomeModel | undefined = undefined;
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
      if (this.model) {
        HomeView({ model: this.model, profile: this.profile(), style: this.style,
        onOutput: (output: HomeOutput) => {
          if (output === HomeOutput.OpenSettings) {
            this.getUIContext().getRouter().pushUrl({ url: 'pages/Settings' });
          }
        } })
      }
    }.width('100%').height('100%')
  }
}
