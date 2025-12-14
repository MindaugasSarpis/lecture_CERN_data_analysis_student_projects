package com.arnasmat.fightingapp.domain.repository

import com.arnasmat.fightingapp.domain.model.ExampleItem
import com.arnasmat.fightingapp.domain.util.Resource
import kotlinx.coroutines.flow.Flow

/**
 * Repository interface - domain layer
 * Defines contract for data operations
 * Implementation will be in data layer
 */
interface ExampleRepository {

    suspend fun getExample(id: Int): Flow<Resource<ExampleItem>>

    suspend fun getExamples(): Flow<Resource<List<ExampleItem>>>

    suspend fun createExample(title: String, description: String): Flow<Resource<ExampleItem>>
}

