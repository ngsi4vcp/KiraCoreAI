package ru.kiracore.ai.storage

import android.content.Context
import java.io.File

class AndroidStorageProbe(
    private val context: Context,
) : PersistenceProvider {
    override fun rootPath(): String = File(context.filesDir, "DATA").absolutePath

    override fun isWritable(): Boolean {
        val root = File(rootPath())
        if (!root.exists() && !root.mkdirs()) return false
        val probe = File(root, ".write-probe")
        return try {
            probe.writeText("ok")
            probe.delete()
        } catch (_: Exception) {
            false
        }
    }
}
