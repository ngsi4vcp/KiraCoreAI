package ru.kiracore.ai.runtime

import android.app.Service
import android.content.Intent
import android.os.IBinder
import ru.kiracore.ai.KiraRuntimeBridge

class KiraRuntimeService : Service() {
    override fun onCreate() {
        super.onCreate()
        KiraRuntimeBridge.initializeAsync(this)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (KiraRuntimeBridge.snapshot().phase != RuntimePhase.READY) {
            KiraRuntimeBridge.initializeAsync(this)
        }
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
