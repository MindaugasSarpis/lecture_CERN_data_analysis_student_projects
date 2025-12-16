package com.arnasmat.fightingapp.domain.util

/**
 * Sealed class representing the result of an API call
 * This is a best practice for handling success/error states in a type-safe manner
 */
sealed class Resource<T>(
    val data: T? = null,
    val message: String? = null
) {
    class Success<T>(data: T) : Resource<T>(data)
    class Error<T>(message: String, data: T? = null) : Resource<T>(data, message)
    class Loading<T>(data: T? = null) : Resource<T>(data)
}

