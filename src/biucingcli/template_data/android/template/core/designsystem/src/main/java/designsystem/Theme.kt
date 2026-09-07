package {{PACKAGE_NAME}}.core.designsystem

import androidx.compose.material3.Typography
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

private val LightColors = lightColorScheme(
    primary = BiucingColors.Brand,
    onPrimary = androidx.compose.ui.graphics.Color.White,
    secondary = BiucingColors.Accent,
    onSecondary = androidx.compose.ui.graphics.Color.White,
    primaryContainer = BiucingColors.BrandMuted,
    secondaryContainer = BiucingColors.AccentMuted,
    background = BiucingColors.SurfaceWarm,
    surface = androidx.compose.ui.graphics.Color.White,
    surfaceVariant = BiucingColors.SurfaceCool,
    onBackground = BiucingColors.Ink,
    onSurface = BiucingColors.Ink,
    outline = BiucingColors.Outline,
)

private val DarkColors = darkColorScheme(
    primary = ColorPaletteDark.Brand,
    onPrimary = ColorPaletteDark.OnBrand,
    secondary = ColorPaletteDark.Accent,
    onSecondary = ColorPaletteDark.OnAccent,
    primaryContainer = ColorPaletteDark.BrandContainer,
    secondaryContainer = ColorPaletteDark.AccentContainer,
    background = ColorPaletteDark.Background,
    surface = ColorPaletteDark.Surface,
    surfaceVariant = ColorPaletteDark.SurfaceVariant,
    onBackground = ColorPaletteDark.OnBackground,
    onSurface = ColorPaletteDark.OnSurface,
    outline = ColorPaletteDark.Outline,
)

private val BiucingTypography = Typography(
    headlineLarge = TextStyle(
        fontSize = 30.sp,
        lineHeight = 36.sp,
        fontWeight = FontWeight.Bold,
    ),
    headlineMedium = TextStyle(
        fontSize = 24.sp,
        lineHeight = 30.sp,
        fontWeight = FontWeight.SemiBold,
    ),
    titleLarge = TextStyle(
        fontSize = 20.sp,
        lineHeight = 26.sp,
        fontWeight = FontWeight.SemiBold,
    ),
    titleMedium = TextStyle(
        fontSize = 16.sp,
        lineHeight = 22.sp,
        fontWeight = FontWeight.Medium,
    ),
    bodyLarge = TextStyle(
        fontSize = 16.sp,
        lineHeight = 24.sp,
    ),
    bodyMedium = TextStyle(
        fontSize = 14.sp,
        lineHeight = 20.sp,
    ),
    labelLarge = TextStyle(
        fontSize = 13.sp,
        lineHeight = 18.sp,
        fontWeight = FontWeight.SemiBold,
    ),
    labelMedium = TextStyle(
        fontSize = 12.sp,
        lineHeight = 16.sp,
        fontWeight = FontWeight.Medium,
        letterSpacing = 0.4.sp,
    ),
)

private object ColorPaletteDark {
    val Brand = androidx.compose.ui.graphics.Color(0xFFB8C6FF)
    val OnBrand = androidx.compose.ui.graphics.Color(0xFF0F1B4D)
    val Accent = androidx.compose.ui.graphics.Color(0xFF7EE2C3)
    val OnAccent = androidx.compose.ui.graphics.Color(0xFF00382C)
    val BrandContainer = androidx.compose.ui.graphics.Color(0xFF1A2D77)
    val AccentContainer = androidx.compose.ui.graphics.Color(0xFF0F4F40)
    val Background = androidx.compose.ui.graphics.Color(0xFF11131A)
    val Surface = androidx.compose.ui.graphics.Color(0xFF171A22)
    val SurfaceVariant = androidx.compose.ui.graphics.Color(0xFF1F2533)
    val OnBackground = androidx.compose.ui.graphics.Color(0xFFE7EAF4)
    val OnSurface = androidx.compose.ui.graphics.Color(0xFFE7EAF4)
    val Outline = androidx.compose.ui.graphics.Color(0xFF56607A)
}

@Composable
@Suppress("ktlint:standard:function-naming")
fun BiucingTheme(
    darkTheme: Boolean = false,
    content: @Composable () -> Unit,
) {
    MaterialTheme(
        colorScheme = if (darkTheme) DarkColors else LightColors,
        typography = BiucingTypography,
        content = content,
    )
}
