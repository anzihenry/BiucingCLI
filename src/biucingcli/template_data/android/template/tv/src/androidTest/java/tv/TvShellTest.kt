package {{PACKAGE_NAME}}.tv

import androidx.compose.ui.input.key.Key
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.assertIsFocused
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.performKeyInput
import androidx.compose.ui.test.pressKey
import org.junit.Rule
import org.junit.Test

@OptIn(androidx.compose.ui.test.ExperimentalTestApi::class)
class TvShellTest {
    @get:Rule val ui = createAndroidComposeRule<MainActivity>()
    @Test fun remoteCalculatesNavigatesAndRestoresSession() {
        ui.onNodeWithText("计算示例").assertIsFocused()
        ui.onRoot().performKeyInput { pressKey(Key.DirectionCenter) }
        ui.waitUntil(10_000) { ui.onAllNodes(hasText("42")).fetchSemanticsNodes().isNotEmpty() }
        ui.activityRule.scenario.recreate()
        ui.onNodeWithText("42").assertIsDisplayed()
        ui.onNodeWithText("计算示例").assertIsFocused()
        ui.onRoot().performKeyInput { pressKey(Key.DirectionRight); pressKey(Key.DirectionCenter) }
        ui.onNodeWithText("Android TV").assertIsDisplayed()
        ui.onNodeWithText("返回").assertIsFocused()
        ui.onRoot().performKeyInput { pressKey(Key.DirectionCenter) }
        ui.onNodeWithText("计算示例").assertIsFocused()
    }
}
