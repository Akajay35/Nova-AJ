package com.novaj

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.speech.RecognizerIntent
import android.speech.tts.TextToSpeech
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import java.util.Locale

private data class ChatMessage(val text: String, val fromUser: Boolean)

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) { super.onCreate(savedInstanceState); setContent { NovaAjApp() } }
}

@Composable
private fun NovaAjApp() {
    var selected by remember { mutableStateOf(0) }
    val messages = remember { mutableStateListOf(ChatMessage("Hello! I'm Nova-AJ. How can I help?", false)) }
    val tabs = listOf("Home", "Chat", "Trainer", "Skills", "Settings")
    val client = remember { NovaApiClient(BuildConfig.NOVA_API_URL, BuildConfig.NOVA_API_TOKEN) }
    val context = LocalContext.current
    val tts = remember { TextToSpeech(context, null) }
    DisposableEffect(tts) { onDispose { tts.stop(); tts.shutdown() } }
    MaterialTheme {
        Surface(Modifier.fillMaxSize()) {
            Scaffold(bottomBar = { NavigationBar { tabs.forEachIndexed { index, title -> NavigationBarItem(selected == index, { selected = index }, icon = { Text(title.take(1)) }, label = { Text(title) }) } } }) { padding ->
                Box(Modifier.padding(padding)) { when (selected) { 0 -> HomeScreen { selected = 1 }; 1 -> ChatScreen(messages, client, tts); 2 -> TrainerScreen(); 3 -> SkillsScreen(); else -> PermissionSettingsScreen() } }
            }
        }
    }
}

private fun speak(tts: TextToSpeech, text: String) { if (text.isNotBlank()) tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "nova-response") }

@Composable
private fun PermissionSettingsScreen() {
    val context = LocalContext.current
    var microphoneGranted by remember { mutableStateOf(androidx.core.content.ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) }
    var wakeWordEnabled by remember { mutableStateOf(false) }
    val speechLauncher = rememberLauncherForActivityResult(ActivityResultContracts.StartActivityForResult()) { }
    val wakeWordController = remember { WakeWordController(context, speechLauncher) }
    val permissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted -> microphoneGranted = granted }
    DisposableEffect(wakeWordController) { onDispose { wakeWordController.setEnabled(false) } }
    Column(Modifier.fillMaxSize().padding(16.dp)) {
        Text("Voice & Wake Word", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(16.dp))
        Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(16.dp)) {
            Text("Microphone", style = MaterialTheme.typography.titleMedium)
            Text(if (microphoneGranted) "Permission granted" else "Permission required for voice input")
            Spacer(Modifier.height(8.dp))
            Button(onClick = {
                if (!microphoneGranted) permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                else context.startActivity(Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.parse("package:${context.packageName}")))
            }) { Text(if (microphoneGranted) "Open app permission settings" else "Allow microphone") }
        } }
        Spacer(Modifier.height(12.dp))
        Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(16.dp)) {
            Text("Wake word", style = MaterialTheme.typography.titleMedium)
            Text(if (wakeWordEnabled) "Enabled — ready for a wake event" else "Disabled by default")
            Spacer(Modifier.height(8.dp))
            Switch(checked = wakeWordEnabled, onCheckedChange = { value ->
                if (microphoneGranted) { wakeWordEnabled = value; wakeWordController.setEnabled(value) }
            })
            if (wakeWordEnabled) {
                Spacer(Modifier.height(8.dp))
                Button(onClick = { wakeWordController.startListeningAfterWake() }) { Text("Test wake event") }
            }
            if (!microphoneGranted) Text("Grant microphone permission before enabling wake-word mode.")
        } }
        Spacer(Modifier.height(12.dp))
        Text("Privacy: wake-word mode is disabled by default. This controller does not continuously record; a dedicated on-device hotword service is required for true always-on detection.")
    }
}

@Composable
private fun HomeScreen(onChat: () -> Unit) {
    val context = LocalContext.current; var status by remember { mutableStateOf<String?>(null) }
    val speechLauncher = rememberLauncherForActivityResult(ActivityResultContracts.StartActivityForResult()) { result -> val text = result.data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)?.firstOrNull(); status = if (text.isNullOrBlank()) "No speech detected." else "Heard: $text" }
    val permissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted -> if (granted) speechLauncher.launch(Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply { putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM); putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault()); putExtra(RecognizerIntent.EXTRA_PROMPT, "Talk to Nova-AJ") }) else status = "Microphone permission denied." }
    Column(Modifier.fillMaxSize().padding(24.dp), verticalArrangement = Arrangement.Center) {
        Text("Nova-AJ", style = MaterialTheme.typography.headlineLarge); Text("Your personal AI assistant"); Spacer(Modifier.height(24.dp))
        Button(onClick = onChat, Modifier.fillMaxWidth()) { Text("Chat with Nova") }; Spacer(Modifier.height(12.dp))
        Button(onClick = { if (androidx.core.content.ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) speechLauncher.launch(Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply { putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM); putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault()); putExtra(RecognizerIntent.EXTRA_PROMPT, "Talk to Nova-AJ") }) else permissionLauncher.launch(Manifest.permission.RECORD_AUDIO) }, Modifier.fillMaxWidth()) { Text("🎙  Talk to Nova") }
        status?.let { Spacer(Modifier.height(12.dp)); Text(it) }
    }
}

@Composable
private fun ChatScreen(messages: MutableList<ChatMessage>, client: NovaApiClient, tts: TextToSpeech) {
    var input by remember { mutableStateOf("") }; var busy by remember { mutableStateOf(false) }; var error by remember { mutableStateOf<String?>(null) }
    val context = LocalContext.current
    val speechLauncher = rememberLauncherForActivityResult(ActivityResultContracts.StartActivityForResult()) { result -> val text = result.data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)?.firstOrNull(); if (!text.isNullOrBlank() && !busy) input = text }
    val permissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted -> if (granted) speechLauncher.launch(Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply { putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM); putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault()); putExtra(RecognizerIntent.EXTRA_PROMPT, "Ask Nova-AJ") }) }
    fun startVoice() { if (androidx.core.content.ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) speechLauncher.launch(Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply { putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM); putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault()); putExtra(RecognizerIntent.EXTRA_PROMPT, "Ask Nova-AJ") }) else permissionLauncher.launch(Manifest.permission.RECORD_AUDIO) }
    fun send(text: String) { if (text.isBlank() || busy) return; messages.add(ChatMessage(text.trim(), true)); input = ""; error = null; busy = true; Thread { val result = client.chat(text.trim()); runOnUiThread { result.onSuccess { reply -> messages.add(ChatMessage(reply, false)); speak(tts, reply) }.onFailure { error = "Connection failed: ${it.message ?: "unknown error"}" }; busy = false } }.start() }
    Column(Modifier.fillMaxSize().padding(16.dp)) {
        Text("Chat", style = MaterialTheme.typography.headlineMedium)
        LazyColumn(Modifier.weight(1f).fillMaxWidth(), reverseLayout = true) { items(messages.asReversed()) { message -> Card(Modifier.fillMaxWidth().padding(vertical = 4.dp)) { Text(if (message.fromUser) "You: ${message.text}" else "Nova: ${message.text}", Modifier.padding(12.dp)) } } }
        error?.let { Text(it, color = MaterialTheme.colorScheme.error) }
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedTextField(input, { input = it }, Modifier.weight(1f), placeholder = { Text("Ask Nova-AJ…") }, enabled = !busy)
            Button(onClick = { startVoice() }, enabled = !busy) { Text("🎙") }
            Button(onClick = { send(input) }, enabled = input.isNotBlank() && !busy) { Text(if (busy) "…" else "Send") }
        }
    }
}

@Composable private fun TrainerScreen() { Column(Modifier.fillMaxSize().padding(16.dp)) { Text("Trainer Mode", style = MaterialTheme.typography.headlineMedium); Spacer(Modifier.height(12.dp)); Text("Teach Nova-AJ new workflows. Trained skills require approval before activation."); Spacer(Modifier.height(20.dp)); Button(onClick = {}) { Text("Start training") } } }
@Composable private fun SkillsScreen() { Column(Modifier.fillMaxSize().padding(16.dp)) { Text("Skills", style = MaterialTheme.typography.headlineMedium); listOf("Voice", "Memory", "Web", "File tools", "Trainer").forEach { skill -> Card(Modifier.fillMaxWidth().padding(vertical = 4.dp)) { Text("✓  $skill", Modifier.padding(14.dp)) } } } }
