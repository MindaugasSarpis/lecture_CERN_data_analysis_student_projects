package com.arnasmat.fightingapp.di

import android.content.Context
import android.util.Log
import com.arnasmat.fightingapp.data.local.UserProfileCache
import com.arnasmat.fightingapp.data.local.VideoHistoryDataSource
import com.arnasmat.fightingapp.data.remote.api.FightingApi
import com.arnasmat.fightingapp.data.repository.ExampleRepositoryImpl
import com.arnasmat.fightingapp.data.repository.MoveRepositoryImpl
import com.arnasmat.fightingapp.data.repository.UserRepositoryImpl
import com.arnasmat.fightingapp.data.repository.VideoRepositoryImpl
import com.arnasmat.fightingapp.domain.repository.ExampleRepository
import com.arnasmat.fightingapp.domain.repository.MoveRepository
import com.arnasmat.fightingapp.domain.repository.UserRepository
import com.arnasmat.fightingapp.domain.repository.VideoRepository
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Singleton

/**
 * Hilt module for network dependencies
 * Provides Retrofit, OkHttpClient, and API instances
 */
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    // TODO: Replace with actual base URL when backend is ready
    private const val BASE_URL = "https://web-production-a59ad.up.railway.app/"

    /**
     * Provides OkHttpClient with logging interceptor
     * Best practice: Different configurations for debug/release builds
     */
    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY // Use NONE in release builds
        }

        return OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .connectTimeout(60, TimeUnit.SECONDS)
            .readTimeout(300, TimeUnit.SECONDS) // 5 minutes for video analysis
            .writeTimeout(300, TimeUnit.SECONDS) // 5 minutes for video upload
            .retryOnConnectionFailure(true)
            // Add authentication interceptor here when needed:
            // .addInterceptor(authInterceptor)
            .build()
    }

    /**
     * Provides Retrofit instance
     * Using Gson converter for JSON serialization/deserialization
     */
    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        Log.i("NetworkModule", "Initializing Retrofit with BASE_URL: $BASE_URL")
        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    /**
     * Provides FightingApi instance
     */
    @Provides
    @Singleton
    fun provideFightingApi(retrofit: Retrofit): FightingApi {
        return retrofit.create(FightingApi::class.java)
    }

    /**
     * Provides ExampleRepository implementation
     * Best practice: Depend on abstraction (interface) not implementation
     */
    @Provides
    @Singleton
    fun provideExampleRepository(api: FightingApi): ExampleRepository {
        return ExampleRepositoryImpl(api)
    }

    /**
     * Provides VideoRepository implementation
     */
    @Provides
    @Singleton
    fun provideVideoRepository(
        api: FightingApi,
        @ApplicationContext context: Context,
        videoHistoryDataSource: VideoHistoryDataSource
    ): VideoRepository {
        return VideoRepositoryImpl(api, context, videoHistoryDataSource)
    }

    /**
     * Provides MoveRepository implementation
     */
    @Provides
    @Singleton
    fun provideMoveRepository(api: FightingApi): MoveRepository {
        return MoveRepositoryImpl(api)
    }

    /**
     * Provides UserProfileCache for persistent storage
     */
    @Provides
    @Singleton
    fun provideUserProfileCache(@ApplicationContext context: Context): UserProfileCache {
        return UserProfileCache(context)
    }

    /**
     * Provides UserRepository implementation with caching support
     */
    @Provides
    @Singleton
    fun provideUserRepository(
        api: FightingApi,
        cache: UserProfileCache
    ): UserRepository {
        return UserRepositoryImpl(api, cache)
    }
}

