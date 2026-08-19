package com.novaj

import android.content.Context
import android.content.Intent
import android.speech.RecognizerIntent
import androidx.activity.result.ActivityResultLauncher

/**
 * Privacy-first wake-word boundary.
 * The app stays idle until the user explicitly enables wake-word mode.
 * Actual always-on hotword detection should be supplied by a dedicated
 * on-device engine/service rather than continuously recording through UI code.
 */
class WakeWordController(
    private val context: Context,
    private val speechLauncher: ActivityResultLauncher<Intent>
) {
    var enabled: Boolean = false
        private set

    fun setEnabled(value: Boolean) {
        enabled = value
    }

    fun startListeningAfterWake() {
        if (!enabled) return
        speechLauncher.launch(Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, context.resources.configuration.locales[0])
            putExtra(RecognizerIntent.EXTRA_PROMPT, "Talk to Nova-AJ")
        })
    }
}
