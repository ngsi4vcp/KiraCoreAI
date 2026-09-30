package ru.kiracore.ai.debug

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import ru.kiracore.ai.MainActivity

class DeviceEvidenceActivity : ComponentActivity() {
    private lateinit var runner: DeviceEvidenceRunner

    private val exportLauncher = registerForActivityResult(
        ActivityResultContracts.CreateDocument("application/zip"),
    ) { uri: Uri? ->
        uri?.let { runner.exportEvidence(it, contentResolver) }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        runner = DeviceEvidenceRunner(applicationContext)
        runner.observeLifecycle("created")

        setContent {
            val state by runner.state.collectAsState()
            val scroll = rememberScrollState()

            LaunchedEffect(Unit) {
                if (state.recoveryPending) {
                    runner.recoverPending()
                }
            }

            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .verticalScroll(scroll)
                            .padding(20.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp),
                    ) {
                        Text(
                            text = "Кира:Ядро — проверка Android",
                            style = MaterialTheme.typography.headlineSmall,
                        )
                        Text(text = state.overall)
                        Text(text = "Этап: ${state.phase}")
                        state.runId?.let { Text(text = "Запуск: ${it}") }

                        Button(
                            onClick = runner::startFullSmoke,
                            enabled = !state.running,
                            modifier = Modifier.fillMaxWidth(),
                        ) {
                            Text("Запустить полную проверку A0")
                        }

                        Button(
                            onClick = runner::startA1ParitySmoke,
                            enabled = !state.running,
                            modifier = Modifier.fillMaxWidth(),
                        ) {
                            Text("Запустить проверку соответствия A1")
                        }

                        Button(
                            onClick = runner::prepareAndRestart,
                            enabled = !state.running && state.runId != null,
                            modifier = Modifier.fillMaxWidth(),
                        ) {
                            Text("Перезапустить процесс и проверить восстановление")
                        }

                        Button(
                            onClick = {
                                exportLauncher.launch(
                                    "kira-device-evidence-${state.runId ?: "latest"}.zip",
                                )
                            },
                            enabled = !state.running && state.runId != null,
                            modifier = Modifier.fillMaxWidth(),
                        ) {
                            Text("Экспортировать диагностические материалы")
                        }

                        OutlinedButton(
                            onClick = {
                                startActivity(
                                    Intent(
                                        this@DeviceEvidenceActivity,
                                        MainActivity::class.java,
                                    )
                                        .putExtra("skip_debug_harness", true),
                                )
                            },
                            modifier = Modifier.fillMaxWidth(),
                        ) {
                            Text("Открыть обычный A0 экран")
                        }

                        HorizontalDivider()

                        state.checks.forEach { check ->
                            Column(modifier = Modifier.fillMaxWidth()) {
                                Text(
                                    text = "${check.status} · ${check.name}",
                                    style = MaterialTheme.typography.titleMedium,
                                )
                                Text(text = "${check.durationMs} мс · ${check.details}")
                            }
                        }

                        Text(
                            text = "Диагностические материалы хранятся внутри приложения до экспорта. Пароли, ключи и значения SecureStore в bundle не записываются.",
                            style = MaterialTheme.typography.bodySmall,
                        )
                    }
                }
            }
        }
    }

    override fun onStart() {
        super.onStart()
        if (::runner.isInitialized) runner.observeLifecycle("start")
    }

    override fun onStop() {
        if (::runner.isInitialized) runner.observeLifecycle("stop")
        super.onStop()
    }

    override fun onDestroy() {
        if (::runner.isInitialized) runner.close()
        super.onDestroy()
    }
}