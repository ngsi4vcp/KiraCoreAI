package ru.kiracore.ai

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import ru.kiracore.ai.runtime.KiraRuntimeService
import ru.kiracore.ai.runtime.RuntimeSnapshot

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        startService(Intent(this, KiraRuntimeService::class.java))

        if (BuildConfig.DEBUG && savedInstanceState == null &&
            !intent.getBooleanExtra(EXTRA_SKIP_DEBUG_HARNESS, false)
        ) {
            startActivity(Intent(this, Class.forName("ru.kiracore.ai.debug.DeviceEvidenceActivity")))
        }

        setContent {
            var snapshot by remember {
                mutableStateOf(KiraRuntimeBridge.snapshot())
            }

            DisposableEffect(Unit) {
                val subscription = KiraRuntimeBridge.subscribe { next ->
                    runOnUiThread { snapshot = next }
                }
                onDispose { subscription.close() }
            }

            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    Column(
                        modifier = Modifier.fillMaxSize(),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center,
                    ) {
                        Text(text = "Кира:Ядро — Android Alpha")
                        Text(text = snapshot.message)
                        snapshot.genomeRevision?.let {
                            Text(text = "Геном: G$it")
                        }
                        snapshot.error?.let {
                            Text(text = "Причина: $it")
                        }
                    }
                }
            }
        }
    }
    companion object {
        private const val EXTRA_SKIP_DEBUG_HARNESS = "skip_debug_harness"
    }
}

