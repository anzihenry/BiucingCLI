import { FeatureStyle, HomeOutput } from '@biucing/contracts';
import { HomeModel } from './HomeModel';

@Component
export struct MobileHomeView {
  @ObjectLink model: HomeModel;
  style: FeatureStyle = new FeatureStyle();
  onOutput: (output: HomeOutput) => void = () => {};
  build() {
    Scroll() {
      Column({ space: 20 }) {
        Text(this.style.title).fontSize(22).accessibilityLevel('yes')
        Text($r('app.string.core_description')).fontSize(14)
        Text(this.model.result).fontSize(28).accessibilityText('Result: ' + this.model.result)
        Button(this.model.busy ? 'Working…' : this.style.action)
          .enabled(!this.model.busy).onClick(() => { this.model.calculate().catch(() => {}); })
        Button('Settings').onClick(() => this.onOutput(HomeOutput.OpenSettings))
      }.width('100%').constraintSize({ maxWidth: 640 }).padding(32)
    }.width('100%').height('100%')
  }
}

@Component
export struct DesktopHomeView {
  @ObjectLink model: HomeModel;
  style: FeatureStyle = new FeatureStyle();
  onOutput: (output: HomeOutput) => void = () => {};
  build() {
    Column({ space: 24 }) {
      Text(this.style.title).fontSize(28)
      Text(this.model.result).fontSize(36).accessibilityText('Result: ' + this.model.result)
      Flex({ wrap: FlexWrap.Wrap, justifyContent: FlexAlign.Center }) {
        Button(this.model.busy ? 'Working…' : this.style.action)
          .enabled(!this.model.busy).focusable(true).defaultFocus(true)
          .keyboardShortcut('r', [ModifierKey.CTRL])
          .onClick(() => { this.model.calculate().catch(() => {}); }).margin(8)
        Button('Settings').focusable(true)
          .onClick(() => this.onOutput(HomeOutput.OpenSettings)).margin(8)
      }
      Text('Ctrl+R to calculate · Tab to move focus').fontSize(14)
    }.width('100%').height('100%').justifyContent(FlexAlign.Center).padding(32)
  }
}

@Component
export struct WatchHomeView {
  @ObjectLink model: HomeModel;
  style: FeatureStyle = new FeatureStyle();
  build() {
    // The focused scroll container receives the watch crown's native scroll input.
    List({ space: 12 }) {
      ListItem() { Text(this.style.title).fontSize(18).textAlign(TextAlign.Center).width('100%') }
      ListItem() {
        Text(this.model.result).fontSize(24).textAlign(TextAlign.Center).width('100%')
          .accessibilityText('Result: ' + this.model.result)
      }
      ListItem() {
        Button(this.model.busy ? 'Working…' : this.style.action)
          .width('100%').enabled(!this.model.busy)
          .onClick(() => { this.model.calculate().catch(() => {}); })
      }
    }.width('100%').height('100%').padding({ top: 40, bottom: 40, left: 32, right: 32 })
    .focusable(true).defaultFocus(true).focusOnTouch(true)
  }
}

@Component
export struct TVHomeView {
  @ObjectLink model: HomeModel;
  style: FeatureStyle = new FeatureStyle();
  onOutput: (output: HomeOutput) => void = () => {};
  @State private lastFocus: string = 'home-calculate';

  aboutToAppear(): void {
    try { this.getUIContext().getFocusController().requestFocus(this.lastFocus); }
    catch (_) { /* defaultFocus applies when the view is attached. */ }
  }

  build() {
    Column({ space: 32 }) {
      Text(this.style.title).fontSize(36)
      Text(this.model.result).fontSize(48).accessibilityText('Result: ' + this.model.result)
      Row({ space: 32 }) {
        Button(this.model.busy ? 'Working…' : this.style.action)
          .id('home-calculate').focusable(true).defaultFocus(this.lastFocus === 'home-calculate')
          .onFocus(() => { this.lastFocus = 'home-calculate'; })
          .onClick(() => { if (!this.model.busy) { this.model.calculate().catch(() => {}); } })
        Button('Settings').id('home-settings').focusable(true)
          .defaultFocus(this.lastFocus === 'home-settings')
          .onFocus(() => { this.lastFocus = 'home-settings'; })
          .onClick(() => this.onOutput(HomeOutput.OpenSettings))
      }
    }.width('100%').height('100%').justifyContent(FlexAlign.Center).padding(48)
  }
}
