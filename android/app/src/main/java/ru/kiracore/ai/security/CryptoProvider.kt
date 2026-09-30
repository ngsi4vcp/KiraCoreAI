package ru.kiracore.ai.security

interface CryptoProvider {
    fun randomBytes(size: Int): ByteArray
    fun sha256(value: ByteArray): ByteArray
}
