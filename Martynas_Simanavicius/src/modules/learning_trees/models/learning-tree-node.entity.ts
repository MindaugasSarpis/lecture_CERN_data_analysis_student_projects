import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn, Generated, Index, ManyToOne, OneToMany, JoinColumn } from 'typeorm';
import { LearningTree } from './learning-tree.entity';
import { UserVideo } from '../../videos/models/user-video.entity';
import { UserLearningTreeNodeStats } from '../../statistics/models/user-learning-tree-node-stats.entity';

@Entity('learning_tree_nodes')
export class LearningTreeNode {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'uuid' })
  @Generated('uuid')
  @Index()
  uuid: string;

  @Column({ type: 'integer' })
  @Index()
  learning_tree_id: number;
  
  @ManyToOne(() => LearningTree, (learningTree) => learningTree.nodes)
  @JoinColumn({ name: 'learning_tree_id' })
  learningTree: LearningTree;

  @Column({ type: 'varchar', length: 120 })
  name: string;

  @Column({ type: 'text', nullable: true })
  description: string | null;

  @Column({ type: 'varchar', length: 255, nullable: true })
  video_file_name: string | null;

  @OneToMany(() => UserVideo, (userVideo) => userVideo.learningTreeNode)
  userVideos: UserVideo[];

  @OneToMany(() => UserLearningTreeNodeStats, (stats) => stats.learningTreeNode)
  userStats: UserLearningTreeNodeStats[];

  @CreateDateColumn({ type: 'timestamptz' })
  createdAt: Date;

  @UpdateDateColumn({ type: 'timestamptz' })
  updatedAt: Date;
}
