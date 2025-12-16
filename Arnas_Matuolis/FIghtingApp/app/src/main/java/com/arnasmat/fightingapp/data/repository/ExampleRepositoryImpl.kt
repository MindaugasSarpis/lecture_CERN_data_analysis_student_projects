package com.arnasmat.fightingapp.data.repository

import com.arnasmat.fightingapp.data.remote.api.FightingApi
import com.arnasmat.fightingapp.data.remote.dto.ExamplePostRequestDto
import com.arnasmat.fightingapp.domain.model.ExampleItem
import com.arnasmat.fightingapp.domain.repository.ExampleRepository
import com.arnasmat.fightingapp.domain.util.Resource
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

/**
 * Implementation of ExampleRepository
 * Handles data operations and maps DTOs to domain models
 */
class ExampleRepositoryImpl @Inject constructor(
    private val api: FightingApi
) : ExampleRepository {

    override suspend fun getExample(id: Int): Flow<Resource<ExampleItem>> = flow {
        emit(Resource.Loading())

        try {
            val response = api.getExample(id)

            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!
                val domainModel = ExampleItem(
                    id = dto.id,
                    title = dto.title,
                    description = dto.description ?: ""
                )
                emit(Resource.Success(domainModel))
            } else {
                emit(Resource.Error("Failed to fetch data: ${response.code()}"))
            }
        } catch (e: HttpException) {
            emit(Resource.Error("Network error: ${e.localizedMessage}"))
        } catch (e: IOException) {
            emit(Resource.Error("Network connection failed. Please check your internet connection."))
        } catch (e: Exception) {
            emit(Resource.Error("Unexpected error: ${e.localizedMessage}"))
        }
    }

    override suspend fun getExamples(): Flow<Resource<List<ExampleItem>>> = flow {
        emit(Resource.Loading())

        try {
            val response = api.getExamples()

            if (response.isSuccessful && response.body() != null) {
                val domainModels = response.body()!!.map { dto ->
                    ExampleItem(
                        id = dto.id,
                        title = dto.title,
                        description = dto.description ?: ""
                    )
                }
                emit(Resource.Success(domainModels))
            } else {
                emit(Resource.Error("Failed to fetch data: ${response.code()}"))
            }
        } catch (e: HttpException) {
            emit(Resource.Error("Network error: ${e.localizedMessage}"))
        } catch (e: IOException) {
            emit(Resource.Error("Network connection failed. Please check your internet connection."))
        } catch (e: Exception) {
            emit(Resource.Error("Unexpected error: ${e.localizedMessage}"))
        }
    }

    override suspend fun createExample(
        title: String,
        description: String
    ): Flow<Resource<ExampleItem>> = flow {
        emit(Resource.Loading())

        try {
            val requestDto = ExamplePostRequestDto(
                title = title,
                description = description
            )

            val response = api.createExample(requestDto)

            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!
                val domainModel = ExampleItem(
                    id = dto.id,
                    title = dto.title,
                    description = dto.description
                )
                emit(Resource.Success(domainModel))
            } else {
                emit(Resource.Error("Failed to create item: ${response.code()}"))
            }
        } catch (e: HttpException) {
            emit(Resource.Error("Network error: ${e.localizedMessage}"))
        } catch (e: IOException) {
            emit(Resource.Error("Network connection failed. Please check your internet connection."))
        } catch (e: Exception) {
            emit(Resource.Error("Unexpected error: ${e.localizedMessage}"))
        }
    }
}

