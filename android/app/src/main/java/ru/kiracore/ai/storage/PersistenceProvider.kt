package ru.kiracore.ai.storage

interface PersistenceProvider {
    fun rootPath(): String
    fun isWritable(): Boolean
}
