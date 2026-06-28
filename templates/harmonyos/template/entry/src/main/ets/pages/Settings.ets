import router from '@ohos.router';
import { AppConfig } from '../core/config/AppConfig';
import { BiucingColors, BiucingRadius, BiucingSpacing, BiucingTypography } from '../core/designsystem/Tokens';

@Entry
@Component
struct Settings {
  build() {
    Column({ space: BiucingSpacing.large }) {
      Row() {
        Text('Settings')
          .fontSize(BiucingTypography.title)
          .fontWeight(FontWeight.Bold)
          .fontColor($r('app.color.text_primary'))
          .layoutWeight(1)

        Button('Back')
          .fontSize(BiucingTypography.caption)
          .backgroundColor(BiucingColors.accent)
          .onClick(() => {
            router.back();
          })
      }
      .width('100%')
      .alignItems(VerticalAlign.Center)

      Column({ space: BiucingSpacing.medium }) {
        Text('Application')
          .fontSize(BiucingTypography.sectionTitle)
          .fontWeight(FontWeight.Medium)
          .fontColor($r('app.color.text_primary'))
          .width('100%')

        Text(`Bundle: ${AppConfig.bundleName}`)
          .fontSize(BiucingTypography.caption)
          .fontColor($r('app.color.text_secondary'))
          .width('100%')

        Text(`Module: ${AppConfig.moduleName}`)
          .fontSize(BiucingTypography.caption)
          .fontColor($r('app.color.text_secondary'))
          .width('100%')

        Text(`Ability: ${AppConfig.abilityName}`)
          .fontSize(BiucingTypography.caption)
          .fontColor($r('app.color.text_secondary'))
          .width('100%')
      }
      .alignItems(HorizontalAlign.Start)
      .padding(BiucingSpacing.large)
      .borderRadius(BiucingRadius.medium)
      .backgroundColor($r('app.color.surface'))
      .width('100%')

      Column({ space: BiucingSpacing.medium }) {
        Text('Release')
          .fontSize(BiucingTypography.sectionTitle)
          .fontWeight(FontWeight.Medium)
          .fontColor($r('app.color.text_primary'))
          .width('100%')

        Row({ space: BiucingSpacing.small }) {
          Text(`Version ${AppConfig.versionName}`)
            .fontSize(BiucingTypography.caption)
            .fontColor($r('app.color.text_primary'))

          Text(`code ${AppConfig.versionCode}`)
            .fontSize(BiucingTypography.caption)
            .fontColor($r('app.color.text_secondary'))
        }
        .width('100%')

        Text(`Channel: ${AppConfig.releaseChannel}`)
          .fontSize(BiucingTypography.caption)
          .fontColor(BiucingColors.success)
          .padding({
            left: BiucingSpacing.medium,
            right: BiucingSpacing.medium,
            top: BiucingSpacing.small,
            bottom: BiucingSpacing.small
          })
          .borderRadius(BiucingRadius.small)
          .backgroundColor(BiucingColors.successSoft)
      }
      .alignItems(HorizontalAlign.Start)
      .padding(BiucingSpacing.large)
      .borderRadius(BiucingRadius.medium)
      .backgroundColor($r('app.color.surface'))
      .width('100%')
    }
    .alignItems(HorizontalAlign.Start)
    .height('100%')
    .width('100%')
    .padding(BiucingSpacing.xLarge)
    .backgroundColor($r('app.color.page_background'))
  }
}
