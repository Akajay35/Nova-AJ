package com.novaj

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

private data class ChatMessage(val text: String, val fromUser: Boolean)

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { NovaAjApp() }
    }
}

@androidx.compose.runtime.Composable
private fun NovaAjApp() {
    var selected by remember { mutableStateOf(0) }
    val messages = remember { mutableStateListOf(ChatMessage("Hello! I'm Nova-AJ. How can I help?", false)) }
    val tabs = listOf("Home", "Chat", "Trainer", "Skills", "Settings")

    MaterialTheme {
        Surface(modifier = Modifier.fillMaxSize()) {
            Scaffold(
                bottomBar = {
                    NavigationBar {
                        tabs.forEachIndexed { index, title ->
                            NavigationBarItem(
                                selected = selected == index,
                                onClick = { selected = index },
                                icon = { Text(title.take(1)) },
                                label = { Text(title) }
                            )
                        }
                    }
                }
            ) { padding ->
                when (selected) {
                    0 -> HomeScreen({ selected = 1 })
                    1 -> ChatScreen(messages)
                    2 -> TrainerScreen()
                    3 -> SkillsScreen()
                    else -> SettingsScreen()
                }
            }
        }
    }
}

@androidx.compose.runtime.Composable
private fun HomeScreen(onChat: () -> Unit) {
    Column(Modifier.fillMaxSize().padding(24.dp), verticalArrangement = Arrangement.Center) {
        Text("Nova-AJ", style = MaterialTheme.typography.headlineLarge)
        Spacer(Modifier.height(8.dp))
        Text("Your personal AI assistant")
        Spacer(Modifier.height(24.dp))
        Button(onClick = onChat, modifier = Modifier.fillMaxWidth()) { Text("🎙  Talk to Nova") }
        Spacer(Modifier.height(12.dp))
        Text("Ready • AI • Memory • Skills", style = MaterialTheme.typography.bodyMedium)
    }
}

@androidx.compose.runtime.Composable
private fun ChatScreen(messages: List<ChatMessage>) {
    var input by remember { mutableStateOf("") }
    Column(Modifier.fillMaxSize().padding(16.dp)) {
        Text("Chat", style = MaterialTheme.typography.headlineMedium)
        LazyColumn(Modifier.weight(1f).fillMaxWidth(), reverseLayout = true) {
            items(messages.asReversed()) { message ->
                Card(Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
                    Text(message.text, Modifier.padding(12.dp))
                }
            }
        }
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedTextField(input, { input = it }, Modifier.weight(1f), placeholder = { Text("Ask Nova-AJ…") })
            Button(onClick = { input = "" }, enabled = input.isNotBlank()) { Text("Send") }
        }
    }
}

@androidx.compose.runtime.Composable
private fun TrainerScreen() {
    Column(Modifier.fillMaxSize().padding(16.dp)) {
        Text("Trainer Mode", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(12.dp))
        Text("Teach Nova-AJ new workflows. Trained skills require approval before activation.")
        Spacer(Modifier.height(20.dp))
        Button(onClick = {}) { Text("Start training") }
    }
}

@androidx.compose.runtime.Composable
private fun SkillsScreen() {
    Column(Modifier.fillMaxSize().padding(16.dp)) {
        Text("Skills", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(12.dp))
        listOf("Voice", "Memory", "Web", "File tools", "Trainer").forEach { skill ->
            Card(Modifier.fillMaxWidth().padding(vertical = 4.dp)) { Text("✓  $skill", Modifier.padding(14.dp)) }
        }
    }
}

@androidx.compose.runtime.Composable
private fun SettingsScreen() {
    Column(Modifier.fillMaxSize().padding(16.dp)) {
        Text("Settings", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(12.dp))
        Text("Permissions")
        Text("Memory & privacy")
        Text("Voice settings")
        Text("Diagnostics")
        Text("Backend connection")
    }
}
