package com.novaj

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

private data class ChatMessage(val text: String, val fromUser: Boolean)

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { NovaAjApp() }
    }
}

@Composable
private fun NovaAjApp() {
    var selected by remember { mutableStateOf(0) }
    val messages = remember { mutableStateListOf(ChatMessage("Hello! I'm Nova-AJ. How can I help?", false)) }
    val tabs = listOf("Home", "Chat", "Trainer", "Skills", "Settings")
    val client = remember { NovaApiClient(BuildConfig.NOVA_API_URL, BuildConfig.NOVA_API_TOKEN) }

    MaterialTheme {
        Surface(Modifier.fillMaxSize()) {
            Scaffold(bottomBar = {
                NavigationBar {
                    tabs.forEachIndexed { index, title ->
                        NavigationBarItem(selected == index, { selected = index }, icon = { Text(title.take(1)) }, label = { Text(title) })
                    }
                }
            }) { padding ->
                Box(Modifier.padding(padding)) {
                    when (selected) {
                        0 -> HomeScreen { selected = 1 }
                        1 -> ChatScreen(messages, client)
                        2 -> TrainerScreen()
                        3 -> SkillsScreen()
                        else -> SettingsScreen()
                    }
                }
            }
        }
    }
}

@Composable
private fun HomeScreen(onChat: () -> Unit) {
    Column(Modifier.fillMaxSize().padding(24.dp), verticalArrangement = Arrangement.Center) {
        Text("Nova-AJ", style = MaterialTheme.typography.headlineLarge)
        Text("Your personal AI assistant")
        Spacer(Modifier.height(24.dp))
        Button(onClick = onChat, Modifier.fillMaxWidth()) { Text("🎙  Talk to Nova") }
    }
}

@Composable
private fun ChatScreen(messages: MutableList<ChatMessage>, client: NovaApiClient) {
    var input by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    Column(Modifier.fillMaxSize().padding(16.dp)) {
        Text("Chat", style = MaterialTheme.typography.headlineMedium)
        LazyColumn(Modifier.weight(1f).fillMaxWidth(), reverseLayout = true) {
            items(messages.asReversed()) { message ->
                Card(Modifier.fillMaxWidth().padding(vertical = 4.dp)) { Text(message.text, Modifier.padding(12.dp)) }
            }
        }
        error?.let { Text(it, color = MaterialTheme.colorScheme.error) }
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedTextField(input, { input = it }, Modifier.weight(1f), placeholder = { Text("Ask Nova-AJ…") }, enabled = !busy)
            Button(onClick = {
                val text = input.trim(); if (text.isEmpty() || busy) return@Button
                messages.add(ChatMessage(text, true)); input = ""; error = null; busy = true
                Thread {
                    val result = client.chat(text)
                    runOnUiThread {
                        result.onSuccess { messages.add(ChatMessage(it, false)) }
                            .onFailure { error = "Connection failed: ${it.message ?: "unknown error"}" }
                        busy = false
                    }
                }.start()
            }, enabled = input.isNotBlank() && !busy) { Text(if (busy) "…" else "Send") }
        }
    }
}

@Composable
private fun TrainerScreen() {
    Column(Modifier.fillMaxSize().padding(16.dp)) {
        Text("Trainer Mode", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(12.dp))
        Text("Teach Nova-AJ new workflows. Trained skills require approval before activation.")
        Spacer(Modifier.height(20.dp))
        Button(onClick = {}) { Text("Start training") }
    }
}

@Composable
private fun SkillsScreen() {
    Column(Modifier.fillMaxSize().padding(16.dp)) {
        Text("Skills", style = MaterialTheme.typography.headlineMedium)
        listOf("Voice", "Memory", "Web", "File tools", "Trainer").forEach { skill ->
            Card(Modifier.fillMaxWidth().padding(vertical = 4.dp)) { Text("✓  $skill", Modifier.padding(14.dp)) }
        }
    }
}

@Composable
private fun SettingsScreen() {
    Column(Modifier.fillMaxSize().padding(16.dp)) {
        Text("Settings", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(12.dp))
        Text("Backend connection: configured through build-time settings")
        Text("Permissions")
        Text("Memory & privacy")
        Text("Voice settings")
        Text("Diagnostics")
    }
}
