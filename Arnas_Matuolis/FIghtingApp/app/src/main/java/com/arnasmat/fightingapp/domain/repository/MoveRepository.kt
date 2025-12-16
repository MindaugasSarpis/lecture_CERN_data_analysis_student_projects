package com.arnasmat.fightingapp.domain.repository

import com.arnasmat.fightingapp.domain.model.Move
import com.arnasmat.fightingapp.domain.util.Resource
import kotlinx.coroutines.flow.Flow

/**
 * Repository interface for Move operations
 * Following clean architecture - domain layer defines contract
 */
interface MoveRepository {
    /**
     * Get list of suggested moves for learning
     * @return Flow of Resource containing list of moves
     */
    suspend fun getLearningSuggestions(): Flow<Resource<List<Move>>>

    /**
     * Get detailed information about a specific move
     * @param moveId The ID of the move
     * @return Flow of Resource containing move details
     */
    suspend fun getMoveDetail(moveId: Int): Flow<Resource<Move>>

    /**
     * Mark/unmark a move for learning
     * @param moveId The ID of the move
     * @param isMarked Whether the move should be marked
     * @return Flow of Resource containing updated move
     */
    suspend fun toggleMoveMarked(moveId: Int, isMarked: Boolean): Flow<Resource<Move>>

    /**
     * Start learning a move (tracking purposes)
     * @param moveId The ID of the move
     * @return Flow of Resource containing success status
     */
    suspend fun startLearningMove(moveId: Int): Flow<Resource<Unit>>
}

