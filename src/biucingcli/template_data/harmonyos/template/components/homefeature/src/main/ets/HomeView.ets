import { DeviceProfile, FeatureStyle, HomeOutput } from '@biucing/contracts';
import { HomeModel } from './HomeModel';
@Component
export struct HomeView {
  createModel: () => HomeModel = () => { throw new Error('HomeView requires createModel'); };
  private model: HomeModel | undefined = undefined;
  profile: DeviceProfile = DeviceProfile.Mobile;
  style: FeatureStyle = new FeatureStyle();
  onOutput: (output: HomeOutput) => void = () => {};
  @State result: string = 'Ready';
  @State busy: boolean = false;
  private visible: boolean = true;
  aboutToAppear(): void { this.visible = true; this.result = 'Ready'; this.model = this.createModel(); }
  aboutToDisappear(): void {
    this.visible = false;
    this.model?.close().catch(() => {});
    this.model = undefined;
    this.busy = false;
  }
  private async calculate(): Promise<void> {
    const active = this.model;
    if (!active || this.busy) { return; }
    this.busy = true;
    try {
      const value = await active.calculate();
      if (this.visible && this.model === active) { this.result = value; }
    } catch (_) {
      if (this.visible && this.model === active) { this.result = 'Unable to calculate'; }
    } finally {
      if (this.visible && this.model === active) { this.busy = false; }
    }
  }
  build() {
    Column({ space: this.profile === DeviceProfile.Watch ? 8 : 20 }) {
      Text(this.style.title).fontSize(this.profile === DeviceProfile.TV ? 36 : 22)
      Text($r('app.string.core_description')).fontSize(14)
      Text(this.result).fontSize(this.profile === DeviceProfile.TV ? 48 : 28)
      Button(this.busy ? 'Working…' : this.style.action)
        .enabled(!this.busy).focusable(true).defaultFocus(this.profile === DeviceProfile.TV)
        .onClick(() => { this.calculate(); })
      if (this.profile !== DeviceProfile.Watch) {
        Button('Settings').focusable(true).onClick(() => this.onOutput(HomeOutput.OpenSettings))
      }
    }.width('100%').height('100%').justifyContent(FlexAlign.Center)
    .padding(this.profile === DeviceProfile.Watch ? 24 : 32)
  }
}
