package ru.kiracore.ai

import android.content.Context
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import org.json.JSONObject

object KiraRuntimeBridge {
    private const val MODULE = "android_bridge"

    @Synchronized
    private fun python(context: Context): Python {
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(context.applicationContext))
        }
        return Python.getInstance()
    }

    fun initialize(context: Context): JSONObject =
        JSONObject(python(context).getModule(MODULE).callAttr("initialize").toString())

    fun health(context: Context): String =
        python(context).getModule(MODULE).callAttr("health").toString()
}
