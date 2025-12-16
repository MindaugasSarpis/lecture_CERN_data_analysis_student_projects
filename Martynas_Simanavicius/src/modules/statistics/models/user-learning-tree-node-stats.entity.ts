import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn, Generated, Index, ManyToOne, OneToOne, JoinColumn } from 'typeorm';
import { LearningTreeNode } from '../../learning_trees/models/learning-tree-node.entity';
import { User } from '../../auth/models/user.entity';
import { UserVideo } from '../../videos/models/user-video.entity';

@Entity('user_learning_tree_node_stats')
export class UserLearningTreeNodeStats {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'uuid' })
  @Generated('uuid')
  @Index()
  uuid: string;

  @Column({ type: 'integer' })
  @Index()
  learning_tree_node_id: number;

  @ManyToOne(() => LearningTreeNode, (node) => node.userStats)
  @JoinColumn({ name: 'learning_tree_node_id' })
  learningTreeNode: LearningTreeNode;

  @Column({ type: 'integer' })
  @Index()
  user_id: number;

  @ManyToOne(() => User, (user) => user.learningTreeNodeStats)
  @JoinColumn({ name: 'user_id' })
  user: User;

  @Column({ type: 'integer' })
  @Index()
  user_video_id: number;

  @OneToOne(() => UserVideo, (userVideo) => userVideo.stats)
  @JoinColumn({ name: 'user_video_id' })
  userVideo: UserVideo;

  @Column('numeric', { precision: 5, scale: 2 })
  completion_score: number;

  @Column({ type: 'text' })
  analysis_description: string;

  @CreateDateColumn({ type: 'timestamptz' })
  createdAt: Date;

  @UpdateDateColumn({ type: 'timestamptz' })
  updatedAt: Date;
}
