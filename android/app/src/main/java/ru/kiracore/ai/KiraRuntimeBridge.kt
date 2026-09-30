package ru.kiracore.ai

import android.content.Context
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import org.json.JSONObject
import java.io.File

object KiraRuntimeBridge {
    private const val MODULE = "android_bridge"

    @Synchronized
    private fun python(context: Context): Python {
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(context.applicationContext))
        }
        return Python.getInstance()
    }

    private fun stageGenome(context: Context): File {
        val target = File(context.filesDir, "GENOME/genome.txt")
        target.parentFile?.mkdirs()
        context.assets.open("GENOME/genome.txt").use { input ->
            target.outputStream().use { output -> input.copyTo(output) }
        }
        return target
    }

    fun initialize(context: Context): JSONObject {
        stageGenome(context)
        return JSONObject(
            python(context)
                .getModule(MODULE)
                .callAttr("initialize", context.filesDir.absolutePath)
                .toString()
        )
    }

    fun health(context: Context): String =
        python(context).getModule(MODULE).callAttr("health").toString()
}
