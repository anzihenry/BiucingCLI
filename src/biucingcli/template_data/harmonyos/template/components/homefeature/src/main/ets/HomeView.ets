import { DeviceProfile, FeatureStyle, HomeOutput } from '@biucing/contracts';
import { HomeModel } from './HomeModel';
import { MobileHomeView, DesktopHomeView, WatchHomeView, TVHomeView } from './DeviceHomeViews';

@Component
export struct HomeView {
  @ObjectLink model: HomeModel;
  profile: DeviceProfile = DeviceProfile.Mobile;
  style: FeatureStyle = new FeatureStyle();
  onOutput: (output: HomeOutput) => void = () => {};

  build() {
    Column() {
      if (this.profile === DeviceProfile.Watch) {
        WatchHomeView({ model: this.model, style: this.style })
      } else if (this.profile === DeviceProfile.TV) {
        TVHomeView({ model: this.model, style: this.style, onOutput: this.onOutput })
      } else if (this.profile === DeviceProfile.Desktop) {
        DesktopHomeView({ model: this.model, style: this.style, onOutput: this.onOutput })
      } else {
        MobileHomeView({ model: this.model, style: this.style, onOutput: this.onOutput })
      }
    }.width('100%').height('100%')
  }
}
