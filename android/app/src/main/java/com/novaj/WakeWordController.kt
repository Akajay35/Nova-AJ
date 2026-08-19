package com.novaj

import android.content.Context
import android.content.Intent
import android.speech.RecognizerIntent
import androidx.activity.result.ActivityResultLauncher

/** Privacy-first wake-word controller. Always-on detection is intentionally delegated to a dedicated on-device engine/service. */
class WakeWordController(
    private val context: Context,
    private val speechLauncher: ActivityResultLauncher<Intent>
) {
    var enabled: Boolean = false
        private set

    fun setEnabled(value: Boolean) { enabled = value }

    fun startListeningAfterWake() {
        if (!enabled) return
        speechLauncher.launch(Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, context.resources.configuration.locales[0])
            putExtra(RecognizerIntent.EXTRA_PROMPT, "Talk to Nova-AJ")
        })
    }
}
