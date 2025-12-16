import { Router } from 'express';
import { LearningTreesController } from './controllers/learning-trees.controller';

const router = Router();
const learningTreesController = new LearningTreesController();

// POST /api/learning-trees
router.post('/', (req, res) => learningTreesController.create(req, res));

// GET /api/learning-trees
router.get('/', (req, res) => learningTreesController.list(req, res));

// GET /api/learning-trees/:uuid
router.get('/:uuid', (req, res) => learningTreesController.getOne(req, res));

// PUT /api/learning-trees/:uuid
router.put('/:uuid', (req, res) => learningTreesController.update(req, res));

// DELETE /api/learning-trees/:uuid
router.delete('/:uuid', (req, res) => learningTreesController.delete(req, res));

export default router;
