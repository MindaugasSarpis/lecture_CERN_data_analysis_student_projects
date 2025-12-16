import { Router } from 'express';
import { LearningTreeNodesController } from './controllers/learning-tree-nodes.controller';

const router = Router();
const learningTreeNodesController = new LearningTreeNodesController();

// POST /api/learning-tree-nodes
router.post('/', (req, res) => learningTreeNodesController.create(req, res));

// GET /api/learning-tree-nodes
router.get('/', (req, res) => learningTreeNodesController.list(req, res));

// GET /api/learning-tree-nodes/:uuid
router.get('/:uuid', (req, res) => learningTreeNodesController.getOne(req, res));

// PUT /api/learning-tree-nodes/:uuid
router.put('/:uuid', (req, res) => learningTreeNodesController.update(req, res));

// DELETE /api/learning-tree-nodes/:uuid
router.delete('/:uuid', (req, res) => learningTreeNodesController.delete(req, res));

export default router;
