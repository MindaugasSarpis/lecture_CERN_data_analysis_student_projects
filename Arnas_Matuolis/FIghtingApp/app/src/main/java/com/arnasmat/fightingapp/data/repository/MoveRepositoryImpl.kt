package com.arnasmat.fightingapp.data.repository

import com.arnasmat.fightingapp.data.remote.api.FightingApi
import com.arnasmat.fightingapp.data.remote.dto.MarkMoveRequestDto
import com.arnasmat.fightingapp.data.remote.dto.MoveDto
import com.arnasmat.fightingapp.data.remote.dto.StartLearningRequestDto
import com.arnasmat.fightingapp.domain.model.Move
import com.arnasmat.fightingapp.domain.model.MoveDifficulty
import com.arnasmat.fightingapp.domain.model.MoveStep
import com.arnasmat.fightingapp.domain.repository.MoveRepository
import com.arnasmat.fightingapp.domain.util.Resource
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

/**
 * Implementation of MoveRepository
 * Handles data operations for moves
 *
 * DEBUG MODE: Set USE_MOCK_DATA = true to use mock data for testing
 * Set USE_MOCK_DATA = false to use real API calls
 */
class MoveRepositoryImpl @Inject constructor(
    private val api: FightingApi
) : MoveRepository {

    companion object {
        /**
         * Toggle this flag to switch between mock data and real API calls
         * true = Use mock data (for debugging/testing)
         * false = Use real API calls (for production)
         */
        private const val USE_MOCK_DATA = true // TODO: Set to false when backend is ready
    }

    override suspend fun getLearningSuggestions(): Flow<Resource<List<Move>>> = flow {
        emit(Resource.Loading())

        // USE MOCK DATA FOR DEBUGGING
        if (USE_MOCK_DATA) {
            delay(500) // Simulate network delay
            emit(Resource.Success(getMockMoves()))
            return@flow
        }

        // REAL API CALL (Kept for future use)

        try {
            val response = api.getLearningSuggestions()

            if (response.isSuccessful && response.body() != null) {
                val moves = response.body()!!.map { it.toDomainModel() }
                emit(Resource.Success(moves))
            } else {
                emit(Resource.Error("Failed to fetch moves: ${response.code()}"))
            }
        } catch (e: HttpException) {
            emit(Resource.Error("Network error: ${e.localizedMessage}"))
        } catch (e: IOException) {
            emit(Resource.Error("Connection failed. Check internet."))
        } catch (e: Exception) {
            emit(Resource.Error("Unexpected error: ${e.localizedMessage}"))
        }
    }

    override suspend fun getMoveDetail(moveId: Int): Flow<Resource<Move>> = flow {
        emit(Resource.Loading())

        // USE MOCK DATA FOR DEBUGGING
        if (USE_MOCK_DATA) {
            delay(300) // Simulate network delay
            val move = getMockMoves().find { it.id == moveId }
            if (move != null) {
                emit(Resource.Success(move))
            } else {
                emit(Resource.Error("Move not found"))
            }
            return@flow
        }

        // REAL API CALL (Kept for future use)

        try {
            val response = api.getMoveDetail(moveId)

            if (response.isSuccessful && response.body() != null) {
                val move = response.body()!!.toDomainModel()
                emit(Resource.Success(move))
            } else {
                emit(Resource.Error("Failed to fetch move details: ${response.code()}"))
            }
        } catch (e: HttpException) {
            emit(Resource.Error("Network error: ${e.localizedMessage}"))
        } catch (e: IOException) {
            emit(Resource.Error("Connection failed. Check internet."))
        } catch (e: Exception) {
            emit(Resource.Error("Unexpected error: ${e.localizedMessage}"))
        }
    }

    override suspend fun toggleMoveMarked(moveId: Int, isMarked: Boolean): Flow<Resource<Move>> = flow {
        emit(Resource.Loading())

        // USE MOCK DATA FOR DEBUGGING
        if (USE_MOCK_DATA) {
            delay(200) // Simulate network delay
            val move = getMockMoves().find { it.id == moveId }
            if (move != null) {
                val updatedMove = move.copy(isMarked = isMarked)
                emit(Resource.Success(updatedMove))
            } else {
                emit(Resource.Error("Move not found"))
            }
            return@flow
        }

        // REAL API CALL (Kept for future use)

        try {
            val request = MarkMoveRequestDto(isMarked)
            val response = api.toggleMoveMarked(moveId, request)

            if (response.isSuccessful && response.body() != null) {
                val move = response.body()!!.toDomainModel()
                emit(Resource.Success(move))
            } else {
                emit(Resource.Error("Failed to update move: ${response.code()}"))
            }
        } catch (e: HttpException) {
            emit(Resource.Error("Network error: ${e.localizedMessage}"))
        } catch (e: IOException) {
            emit(Resource.Error("Connection failed. Check internet."))
        } catch (e: Exception) {
            emit(Resource.Error("Unexpected error: ${e.localizedMessage}"))
        }
    }

    override suspend fun startLearningMove(moveId: Int): Flow<Resource<Unit>> = flow {
        emit(Resource.Loading())

        // USE MOCK DATA FOR DEBUGGING
        if (USE_MOCK_DATA) {
            delay(300) // Simulate network delay
            val move = getMockMoves().find { it.id == moveId }
            if (move != null) {
                emit(Resource.Success(Unit))
            } else {
                emit(Resource.Error("Move not found"))
            }
            return@flow
        }

        // REAL API CALL (Kept for future use)

        try {
            val request = StartLearningRequestDto(moveId)
            val response = api.startLearningMove(request)

            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(Unit))
            } else {
                emit(Resource.Error("Failed to start learning: ${response.code()}"))
            }
        } catch (e: HttpException) {
            emit(Resource.Error("Network error: ${e.localizedMessage}"))
        } catch (e: IOException) {
            emit(Resource.Error("Connection failed. Check internet."))
        } catch (e: Exception) {
            emit(Resource.Error("Unexpected error: ${e.localizedMessage}"))
        }
    }

    /**
     * Extension function to convert DTO to domain model
     */
    private fun MoveDto.toDomainModel(): Move {
        return Move(
            id = id,
            title = title,
            description = description,
            imageUrl = imageUrl ?: "",
            difficulty = difficulty?.let { parseDifficulty(it) } ?: MoveDifficulty.WHITE_BELT,
            videoUrl = videoUrl ?: "",
            isMarked = isMarked ?: false,
            category = category
        )
    }

    /**
     * Parse difficulty string to belt level
     */
    private fun parseDifficulty(difficulty: String): MoveDifficulty {
        return when (difficulty.lowercase()) {
            "white", "white_belt" -> MoveDifficulty.WHITE_BELT
            "yellow", "yellow_belt" -> MoveDifficulty.YELLOW_BELT
            "orange", "orange_belt" -> MoveDifficulty.ORANGE_BELT
            "green", "green_belt" -> MoveDifficulty.GREEN_BELT
            "blue", "blue_belt" -> MoveDifficulty.BLUE_BELT
            "purple", "purple_belt" -> MoveDifficulty.PURPLE_BELT
            "brown", "brown_belt" -> MoveDifficulty.BROWN_BELT
            "black", "black_belt" -> MoveDifficulty.BLACK_BELT
            // Legacy support
            "beginner" -> MoveDifficulty.WHITE_BELT
            "intermediate" -> MoveDifficulty.YELLOW_BELT
            "advanced" -> MoveDifficulty.BLUE_BELT
            "expert" -> MoveDifficulty.BROWN_BELT
            else -> MoveDifficulty.WHITE_BELT
        }
    }

    /**
     * Mock data for debugging/testing - Karate focused with belt-based progression
     * Organized by belt level from White Belt (absolute beginners) to Black Belt (advanced)
     * Remove or disable when backend is ready by setting USE_MOCK_DATA = false
     */
    private fun getMockMoves(): List<Move> {
        return listOf(
            // WHITE BELT - Fundamental techniques for absolute beginners
            Move(
                id = 1,
                title = "Zenkutsu-Dachi (前屈立ち)",
                description = "Front Stance - The fundamental forward stance in karate. Your front knee is bent over the front foot, back leg is straight and strong. 60% of weight on front leg, 40% on back leg. This stance provides stability and power for forward techniques. Feet are hip-width apart for balance.",
                imageUrl = "https://picsum.photos/seed/zenkutsudachi/400/300",
                difficulty = MoveDifficulty.WHITE_BELT,
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                isMarked = false,
                category = "Karate - Stances (立ち方)",
                steps = getZenkutsuDachiSteps()
            ),
            Move(
                id = 2,
                title = "Chūdan Tsuki (中段突き)",
                description = "Middle-Level Punch - A straight punch targeting the opponent's solar plexus or chest area. Start from chambered position at hip, twist hips and extend arm forward in a straight line. Pull opposite hand back to hip (hikite). Fist rotates 180 degrees during extension. Focus on hip rotation for power.",
                imageUrl = "https://picsum.photos/seed/chudantsuki/400/300",
                difficulty = MoveDifficulty.WHITE_BELT,
                videoUrl = "https://storage.googleapis.com/nika-train/Showcase.mp4",
                isMarked = false,
                category = "Karate - Punches (突き)",
                steps = getChudanTsukiSteps(),
                isAvailable = true,
            ),
            Move(
                id = 3,
                title = "Oi-Zuki (追い突き)",
                description = "Lunge Punch - A stepping punch combining zenkutsu-dachi and chūdan tsuki. Step forward into front stance while simultaneously executing a straight punch with the leading hand. Coordinate the stepping motion with the punch for maximum power. The step and punch should land at the same moment. This is a fundamental attacking technique in karate.",
                imageUrl = "https://picsum.photos/seed/oizuki/400/300",
                difficulty = MoveDifficulty.WHITE_BELT,
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
                isMarked = false,
                category = "Karate - Combinations (連続技)",
                steps = getOiZukiSteps()
            ),
            Move(
                id = 4,
                title = "Gedan Barai (下段払い)",
                description = "Downward Block - A sweeping block that deflects low attacks away from your body. Start with blocking arm across your chest, sweep down and outward in an arc, ending at your outer thigh. The forearm rotates during the block. Pull opposite hand to hip (hikite). Essential for defending against kicks and low punches.",
                imageUrl = "https://picsum.photos/seed/gedanbarai/400/300",
                difficulty = MoveDifficulty.WHITE_BELT,
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
                isMarked = false,
                category = "Karate - Blocks (受け)"
            ),

            // YELLOW BELT - Building on fundamentals
            Move(
                id = 5,
                title = "Age-Uke (上げ受け)",
                description = "Rising Block - An upward block used to deflect attacks to the head. Raise your forearm in an upward arc, ending above your forehead. The blocking arm comes from the opposite hip, crosses the centerline, and blocks upward. Rotate forearm 180 degrees during execution. Keep opposite hand chambered at hip.",
                imageUrl = "https://picsum.photos/seed/ageuke/400/300",
                difficulty = MoveDifficulty.YELLOW_BELT,
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
                isMarked = false,
                category = "Karate - Blocks (受け)"
            ),
            Move(
                id = 6,
                title = "Soto-Uke (外受け)",
                description = "Outside Block - An outside forearm block moving from inside to outside. Block sweeps across the body from inside to outside, deflecting middle-level attacks. Start with blocking arm across chest, use opposite forearm to sweep outward. Emphasize hip rotation and pull hikite strongly to the hip for power.",
                imageUrl = "https://picsum.photos/seed/sotouke/400/300",
                difficulty = MoveDifficulty.YELLOW_BELT,
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
                isMarked = false,
                category = "Karate - Blocks (受け)"
            ),
            Move(
                id = 7,
                title = "Mae-Geri (前蹴り)",
                description = "Front Kick - A powerful kick delivered straight forward with the ball of the foot. Chamber knee high and close to chest, snap leg forward extending from the knee, strike with ball of foot (koshi). Pull toes back to expose ball of foot. Rechamber the leg before setting down. Keep upper body upright.",
                imageUrl = "https://picsum.photos/seed/maegeri/400/300",
                difficulty = MoveDifficulty.YELLOW_BELT,
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
                isMarked = false,
                category = "Karate - Kicks (蹴り)"
            ),

            // ORANGE BELT - Intermediate techniques
            Move(
                id = 8,
                title = "Uchi-Uke (内受け)",
                description = "Inside Block - An inside forearm block moving from outside to inside. Starts with blocking arm outside the body, sweeps inward across the centerline to deflect middle-level attacks. The blocking forearm should end in front of your opposite shoulder. Strong hip rotation and hikite are essential.",
                imageUrl = "https://picsum.photos/seed/uchiuke/400/300",
                difficulty = MoveDifficulty.ORANGE_BELT,
                videoUrl = "https://picsum.photos/seed/uchiuke/400/300",
                isMarked = false,
                category = "Karate - Blocks (受け)"
            ),
            Move(
                id = 9,
                title = "Kōkutsu-Dachi (後屈立ち)",
                description = "Back Stance - A defensive stance with 70% weight on the back leg. Front knee is slightly bent, back knee is deeply bent. Both feet are 90 degrees to each other. Hips are at 45-degree angle to opponent. This stance provides strong stability for blocking and quick backward movement.",
                imageUrl = "https://picsum.photos/seed/kokutsudachi/400/300",
                difficulty = MoveDifficulty.ORANGE_BELT,
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
                isMarked = true,
                category = "Karate - Stances (立ち方)"
            ),

            // GREEN BELT - Advanced basics
            Move(
                id = 10,
                title = "Gyaku-Zuki (逆突き)",
                description = "Reverse Punch - A powerful punch using the rear hand from a front stance. While in zenkutsu-dachi with left leg forward, punch with the right hand (opposite of front leg). Maximum hip rotation generates power. This is one of karate's strongest punches. Coordinate hip rotation with arm extension and hikite.",
                imageUrl = "https://picsum.photos/seed/gyakuzuki/400/300",
                difficulty = MoveDifficulty.GREEN_BELT,
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4",
                isMarked = false,
                category = "Karate - Punches (突き)"
            ),
            Move(
                id = 11,
                title = "Shuto-Uke (手刀受け)",
                description = "Knife-Hand Block - A block using the edge of the open hand. Typically performed in back stance (kōkutsu-dachi). The knife hand sweeps across the body from shoulder to centerline. The blade of the hand (between wrist and pinky) is the blocking surface. Other hand chambers at opposite ear then pulls to solar plexus.",
                imageUrl = "https://picsum.photos/seed/shutouke/400/300",
                difficulty = MoveDifficulty.GREEN_BELT,
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/VolkswagenGTIReview.mp4",
                isMarked = false,
                category = "Karate - Blocks (受け)"
            ),

            // BLUE BELT - More complex techniques
            Move(
                id = 12,
                title = "Mawashi-Geri (回し蹴り)",
                description = "Roundhouse Kick - A circular kick striking with the ball of the foot or instep. Chamber knee high and to the side, pivot on supporting foot, rotate hips, and extend leg in a circular arc. Strike with ball of foot for traditional karate or shin/instep for sport karate. Rechamber and control the leg down.",
                imageUrl = "https://picsum.photos/seed/mawashigeri/400/300",
                difficulty = MoveDifficulty.BLUE_BELT,
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
                isMarked = false,
                category = "Karate - Kicks (蹴り)"
            ),
            Move(
                id = 13,
                title = "Yoko-Geri Keage (横蹴上げ)",
                description = "Side Snap Kick - A snapping side kick using the edge of the foot (sokuto). Chamber knee high across the body, pivot on supporting foot, snap leg out to the side striking with the foot edge. Toes pulled back, heel pushed forward. Quick snap and rechamber. Different from the thrusting side kick (yoko-geri kekomi).",
                imageUrl = "https://picsum.photos/seed/yokogerikeage/400/300",
                difficulty = MoveDifficulty.BLUE_BELT,
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4",
                isMarked = false,
                category = "Karate - Kicks (蹴り)"
            ),

            // BROWN BELT - Advanced techniques
            Move(
                id = 14,
                title = "Ushiro-Geri (後ろ蹴り)",
                description = "Back Kick - A powerful backward thrust kick. Look over shoulder to find target, chamber knee to chest, thrust leg backward striking with the heel (kakato). Supporting leg is straight, kicking leg extends fully. Highly effective for creating distance and surprising opponents who have circled behind you.",
                imageUrl = "https://picsum.photos/seed/ushirogeri/400/300",
                difficulty = MoveDifficulty.BROWN_BELT,
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                isMarked = false,
                category = "Karate - Kicks (蹴り)"
            ),
            Move(
                id = 15,
                title = "Uraken-Uchi (裏拳打ち)",
                description = "Back-Fist Strike - A whipping strike using the back of the fist. Arm bends at elbow, whips across the body or in a circular motion. Strike with the back of the first two knuckles. Can target the face, temple, or ribs. Fast and deceptive technique often used in kumite (sparring). Focus on speed and snap.",
                imageUrl = "https://picsum.photos/seed/urakenuchi/400/300",
                difficulty = MoveDifficulty.BROWN_BELT,
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
                isMarked = true,
                category = "Karate - Strikes (打ち)"
            )
        )
    }

    /**
     * Step-by-step instructions for Zenkutsu-Dachi (Front Stance)
     */
    private fun getZenkutsuDachiSteps(): List<MoveStep> {
        return listOf(
            MoveStep(
                id = 1,
                stepNumber = 1,
                title = "Starting Position",
                description = "Stand in a natural stance (heiko-dachi) with feet shoulder-width apart. Keep your back straight, shoulders relaxed, and hands in fists at your sides. Look straight ahead.",
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                tips = listOf(
                    "Keep your posture upright",
                    "Distribute weight evenly on both feet",
                    "Breathe naturally and stay relaxed"
                ),
                imageUrl = "https://picsum.photos/seed/zenkutsu-step1/400/300"
            ),
            MoveStep(
                id = 2,
                stepNumber = 2,
                title = "Step Forward",
                description = "Step forward with your lead leg (left or right). The step should be approximately twice your shoulder width in length. Keep your upper body upright as you step.",
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                tips = listOf(
                    "Step length: about 2 shoulder widths",
                    "Step width: maintain hip-width separation",
                    "Don't lean forward while stepping"
                ),
                imageUrl = "https://picsum.photos/seed/zenkutsu-step2/400/300"
            ),
            MoveStep(
                id = 3,
                stepNumber = 3,
                title = "Bend Front Knee",
                description = "Bend your front knee until it is directly over your front foot. Your knee should align with your toes. The front thigh should be nearly parallel to the ground.",
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                tips = listOf(
                    "Front knee over front foot - don't let it collapse inward",
                    "Front thigh nearly parallel to ground",
                    "60% of weight on front leg"
                ),
                imageUrl = "https://picsum.photos/seed/zenkutsu-step3/400/300"
            ),
            MoveStep(
                id = 4,
                stepNumber = 4,
                title = "Straighten Back Leg",
                description = "Keep your back leg completely straight and strong. Press the entire sole of your back foot firmly into the ground. Your back foot should be at a 45-degree angle.",
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                tips = listOf(
                    "Back leg must be straight and locked",
                    "Back foot at 45-degree angle",
                    "40% of weight on back leg",
                    "Press entire back foot into ground"
                ),
                imageUrl = "https://picsum.photos/seed/zenkutsu-step4/400/300"
            )
        )
    }

    /**
     * Step-by-step instructions for Chūdan Tsuki (Middle Punch)
     */
    private fun getChudanTsukiSteps(): List<MoveStep> {
        return listOf(
            MoveStep(
                id = 1,
                stepNumber = 1,
                title = "Chamber Stance",
                description = "Adopt a balanced fighting stance with feet shoulder-width apart, lead foot forward, and knees slightly bent. Keep hands guarding the face and ribs to protect and prepare for the punch.",
                videoUrl = "https://storage.googleapis.com/nika-train/1ChamberStance.mp4", // Will be provided later
                tips = listOf(
                    "Feet shoulder-width apart for stability",
                    "Lead foot forward, knees slightly bent",
                    "Hands guard face and ribs",
                    "Maintain balanced weight distribution"
                ),
                imageUrl = "https://picsum.photos/seed/chudan-chamber/400/300"
            ),
            MoveStep(
                id = 2,
                stepNumber = 2,
                title = "How to Correctly Hold a Fist and Punch Trajectory",
                description = "Make a tight fist with the thumb outside the fingers and keep the wrist aligned. Punch along a straight centerline from the chamber to the mid-section target (chudan) to maximize speed and reduce wrist injury.",
                videoUrl = "https://storage.googleapis.com/nika-train/3Trajektorija.mp4",
                tips = listOf(
                    "Thumb outside fingers, tight grip",
                    "Keep wrist straight and aligned",
                    "Punch travels in straight line",
                    "Target the mid-section (chudan level)"
                ),
                imageUrl = "https://picsum.photos/seed/chudan-fist/400/300"
            ),
            MoveStep(
                id = 3,
                stepNumber = 3,
                title = "Positioning and Correct Hand Movement",
                description = "Shift weight or step slightly as you extend. Rotate hips and shoulders to generate power while keeping the non-punching hand guarding. Retract the punching hand back to the chamber immediately after impact.",
                videoUrl = "https://storage.googleapis.com/nika-train/5CorrectHandMovement.mp4",
                tips = listOf(
                    "Rotate hips and shoulders for power",
                    "Keep non-punching hand up on guard",
                    "Shift weight into the punch",
                    "Retract hand quickly after impact"
                ),
                imageUrl = "https://picsum.photos/seed/chudan-movement/400/300"
            ),
            MoveStep(
                id = 4,
                stepNumber = 4,
                title = "How to Perform Chudan Tsuki and Common Mistakes",
                description = "Combine chamber, hip rotation, and straight extension to strike the midsection. Common mistakes: overextending, dropping the guard, telegraphing the punch, and misaligned wrist. Correct by practicing short controlled repetitions and returning to guard.",
                videoUrl = "https://storage.googleapis.com/nika-train/6HowToPunch.mp4",
                tips = listOf(
                    "Combine all elements smoothly",
                    "Don't overextend your arm",
                    "Never drop your guard",
                    "Avoid telegraphing the punch",
                    "Keep wrist aligned at all times",
                    "Practice controlled repetitions"
                ),
                imageUrl = "https://picsum.photos/seed/chudan-mistakes/400/300"
            )
        )
    }

    /**
     * Step-by-step instructions for Oi-Zuki (Lunge Punch)
     */
    private fun getOiZukiSteps(): List<MoveStep> {
        return listOf(
            MoveStep(
                id = 1,
                stepNumber = 1,
                title = "Starting Stance",
                description = "Begin in zenkutsu-dachi (front stance) with your weight distributed properly. Chamber your lead hand (same side as front leg) at your hip, palm up. Keep your other hand in guard position.",
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
                tips = listOf(
                    "Start in proper front stance",
                    "Lead hand chambered at hip",
                    "Maintain good posture"
                ),
                imageUrl = "https://picsum.photos/seed/oizuki-step1/400/300"
            ),
            MoveStep(
                id = 2,
                stepNumber = 2,
                title = "Coordinate Step and Punch",
                description = "This is the key to oi-zuki: Begin stepping forward with your back leg AND begin the punch motion at the same time. The step and punch must be perfectly synchronized.",
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
                tips = listOf(
                    "Step and punch start together",
                    "Timing is crucial",
                    "Don't punch before or after stepping"
                ),
                imageUrl = "https://picsum.photos/seed/oizuki-step2/400/300"
            ),
            MoveStep(
                id = 3,
                stepNumber = 3,
                title = "Drive Forward",
                description = "As you step forward into the new front stance, drive your hips forward and extend your punch. Use the momentum from stepping to add power to your punch.",
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
                tips = listOf(
                    "Hips drive forward with the step",
                    "Use stepping momentum for power",
                    "Keep upper body upright",
                    "Don't lean into the punch"
                ),
                imageUrl = "https://picsum.photos/seed/oizuki-step3/400/300"
            ),
            MoveStep(
                id = 4,
                stepNumber = 4,
                title = "Complete Technique",
                description = "Land in a solid front stance with your punch fully extended at the same moment your front foot lands. Execute hikite (pulling opposite hand to hip) and apply kime (focus) at the point of impact.",
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
                tips = listOf(
                    "Foot lands and punch lands simultaneously",
                    "Strong hikite to opposite hip",
                    "Apply kime at impact",
                    "New front leg bent, back leg straight"
                ),
                imageUrl = "https://picsum.photos/seed/oizuki-step4/400/300"
            ),
            MoveStep(
                id = 5,
                stepNumber = 5,
                title = "Recovery and Repeat",
                description = "After completing the technique, maintain your stance briefly to ensure balance. Then chamber your new lead hand and prepare to step forward again with the opposite side.",
                videoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
                tips = listOf(
                    "Hold final position briefly",
                    "Check your stance",
                    "Chamber opposite hand for next technique",
                    "Practice both left and right sides equally"
                ),
                imageUrl = "https://picsum.photos/seed/oizuki-step5/400/300"
            )
        )
    }
}

