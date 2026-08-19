package com.novaj

import java.net.HttpURLConnection
import java.net.URL
import java.io.OutputStreamWriter

class NovaApiClient(
    private val baseUrl: String,
    private val token: String
) {
    fun chat(message: String): Result<String> = runCatching {
        val connection = (URL("${baseUrl.trimEnd('/')}/v1/chat").openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            connectTimeout = 8_000
            readTimeout = 30_000
            doOutput = true
            setRequestProperty("Content-Type", "application/json")
            setRequestProperty("Authorization", "Bearer $token")
        }
        OutputStreamWriter(connection.outputStream, Charsets.UTF_8).use { writer ->
            writer.write("{\"message\":${jsonString(message)}}")
        }
        val stream = if (connection.responseCode in 200..299) connection.inputStream else connection.errorStream
        val response = stream.bufferedReader().use { it.readText() }
        if (connection.responseCode !in 200..299) error("HTTP ${connection.responseCode}")
        Regex("\\\"reply\\\"\\s*:\\s*\\\"((?:\\\\.|[^\\\"])*)\\\"").find(response)?.groupValues?.get(1)?.replace("\\\"", "\"")
            ?: error("invalid server response")
    }

    private fun jsonString(value: String): String = "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n") + "\""
}
