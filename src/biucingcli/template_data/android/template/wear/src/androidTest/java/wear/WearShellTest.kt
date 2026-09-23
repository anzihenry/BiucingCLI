package {{PACKAGE_NAME}}.wear

import android.os.SystemClock
import android.view.InputDevice
import android.view.MotionEvent
import org.junit.Assert.assertTrue
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import org.junit.Rule
import org.junit.Test

class WearShellTest {
    @get:Rule val ui = createAndroidComposeRule<MainActivity>()
    @Test fun rotaryInputScrollsRoundList() {
        val before = ui.onNodeWithText("—").fetchSemanticsNode().boundsInRoot.center.y
        ui.runOnUiThread {
            val pointer = MotionEvent.PointerProperties().apply { id = 0 }
            val coords = MotionEvent.PointerCoords().apply { setAxisValue(MotionEvent.AXIS_SCROLL, -1f) }
            val time = SystemClock.uptimeMillis()
            val event = MotionEvent.obtain(time, time, MotionEvent.ACTION_SCROLL, 1,
                arrayOf(pointer), arrayOf(coords), 0, 0, 1f, 1f, 0, 0,
                InputDevice.SOURCE_ROTARY_ENCODER, 0)
            try { ui.activity.dispatchGenericMotionEvent(event) } finally { event.recycle() }
        }
        ui.waitForIdle()
        val after = ui.onNodeWithText("—").fetchSemanticsNode().boundsInRoot.center.y
        assertTrue("Rotary input must move the list", after < before)
    }

    @Test fun roundScreenCalculatesAndRetainsSession() {
        ui.onNodeWithText("计算示例").performScrollTo().performClick()
        ui.waitUntil(10_000) { ui.onAllNodes(hasText("42")).fetchSemanticsNodes().isNotEmpty() }
        ui.activityRule.scenario.recreate()
        ui.onNodeWithText("42").assertIsDisplayed()
        ui.onNodeWithText("关于").performScrollTo().performClick()
        ui.onNodeWithText("Wear OS").assertIsDisplayed()
        ui.onNodeWithText("返回").performScrollTo().performClick()
        ui.onNodeWithText("42").assertIsDisplayed()
    }
}
