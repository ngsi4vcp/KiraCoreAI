package ru.kiracore.ai.security

interface PlatformSecureStore {
    fun put(name: String, value: ByteArray)
    fun get(name: String): ByteArray?
    fun delete(name: String)
}
