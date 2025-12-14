package com.arnasmat.fightingapp.data.remote.api

import com.arnasmat.fightingapp.data.remote.dto.AnalysisResponseDto
import com.arnasmat.fightingapp.data.remote.dto.ExampleGetResponseDto
import com.arnasmat.fightingapp.data.remote.dto.ExamplePostRequestDto
import com.arnasmat.fightingapp.data.remote.dto.ExamplePostResponseDto
import com.arnasmat.fightingapp.data.remote.dto.MarkMoveRequestDto
import com.arnasmat.fightingapp.data.remote.dto.MoveDto
import com.arnasmat.fightingapp.data.remote.dto.StartLearningRequestDto
import com.arnasmat.fightingapp.data.remote.dto.SuccessResponseDto
import com.arnasmat.fightingapp.data.remote.dto.UserProfileDto
import com.arnasmat.fightingapp.data.remote.dto.VideoStreamResponseDto
import com.arnasmat.fightingapp.data.remote.dto.VideoUploadResponseDto
import okhttp3.MultipartBody
import okhttp3.RequestBody
import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Path
import retrofit2.http.Streaming

/**
 * Main API interface for all network calls
 * Base URL will be provided via Hilt DI module
 */
interface FightingApi {

    /**
     * Example GET request
     * @param id The ID of the resource to fetch
     * @return Response containing the requested resource
     */
    @GET("api/examples/{id}")
    suspend fun getExample(
        @Path("id") id: Int
    ): Response<ExampleGetResponseDto>

    /**
     * Example GET request for list
     * @return Response containing list of resources
     */
    @GET("api/examples")
    suspend fun getExamples(): Response<List<ExampleGetResponseDto>>

    /**
     * Example POST request
     * @param request The data to create
     * @return Response containing the created resource
     */
    @POST("api/examples")
    suspend fun createExample(
        @Body request: ExamplePostRequestDto
    ): Response<ExamplePostResponseDto>

    /**
     * Analyze fighting video pose
     * Uploads video and waits for full analysis to complete
     * @param video The video file as multipart (.mp4, .avi, or .mov)
     * @return Response containing analysis results with streaming URLs
     */
    @Multipart
    @POST("analyze")
    suspend fun analyzeVideo(
        @Part file: MultipartBody.Part
    ): Response<AnalysisResponseDto>

    /**
     * Stream analyzed video
     * @param fileName The name of the video file to stream
     * @return Response body containing video stream
     */
    @Streaming
    @GET("stream/video/{filename}")
    suspend fun streamVideo(
        @Path("filename") fileName: String
    ): Response<ResponseBody>

    /**
     * Download analysis chart
     * @param fileName The name of the chart file
     * @return Response body containing PNG image
     */
    @Streaming
    @GET("download/chart/{filename}")
    suspend fun downloadChart(
        @Path("filename") fileName: String
    ): Response<ResponseBody>


    /**
     * Get list of suggested moves for learning
     * @return Response containing list of moves
     */
    @GET("api/moves/suggestions")
    suspend fun getLearningSuggestions(): Response<List<MoveDto>>

    /**
     * Get detailed information about a specific move
     * @param moveId The ID of the move
     * @return Response containing move details
     */
    @GET("api/moves/{id}")
    suspend fun getMoveDetail(
        @Path("id") moveId: Int
    ): Response<MoveDto>

    /**
     * Mark/unmark a move for learning
     * @param moveId The ID of the move
     * @param request Mark status
     * @return Response containing updated move
     */
    @POST("api/moves/{id}/mark")
    suspend fun toggleMoveMarked(
        @Path("id") moveId: Int,
        @Body request: MarkMoveRequestDto
    ): Response<MoveDto>

    /**
     * Start learning a move
     * @param request Start learning request
     * @return Response containing success status
     */
    @POST("api/moves/start-learning")
    suspend fun startLearningMove(
        @Body request: StartLearningRequestDto
    ): Response<SuccessResponseDto>

    /**
     * Get current user profile with move ratings
     * @return Response containing user profile data
     */
    @GET("api/user/profile")
    suspend fun getUserProfile(): Response<UserProfileDto>

    // TODO: Add actual API endpoints when backend is ready
    // Fighting video analysis endpoints will go here
}

