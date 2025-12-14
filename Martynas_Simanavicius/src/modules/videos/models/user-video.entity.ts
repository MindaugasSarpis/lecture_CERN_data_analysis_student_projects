import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn, Generated, Index, ManyToOne, OneToOne, JoinColumn } from 'typeorm';
import { User } from '../../auth/models/user.entity';
import { LearningTreeNode } from '../../learning_trees/models/learning-tree-node.entity';
import { ProcessedUserVideo } from './processed-user-video.entity';
import { UserLearningTreeNodeStats } from '../../statistics/models/user-learning-tree-node-stats.entity';

@Entity('user_videos')
export class UserVideo {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'uuid' })
  @Generated('uuid')
  @Index()
  uuid: string;

  @Column({ type: 'integer' })
  @Index()
  user_id: number;

  @ManyToOne(() => User, (user) => user.userVideos)
  @JoinColumn({ name: 'user_id' })
  user: User;

  @Column({ type: 'integer' })
  @Index()
  learning_tree_node_id: number;

  @ManyToOne(() => LearningTreeNode, (node) => node.userVideos)
  @JoinColumn({ name: 'learning_tree_node_id' })
  learningTreeNode: LearningTreeNode;

  @Column({ type: 'varchar', length: 255 })
  video_file_name: string;

  @OneToOne(() => ProcessedUserVideo, (processedVideo) => processedVideo.userVideo)
  processedVideo: ProcessedUserVideo;

  @OneToOne(() => UserLearningTreeNodeStats, (stats) => stats.userVideo)
  stats: UserLearningTreeNodeStats;

  @CreateDateColumn({ type: 'timestamptz' })
  createdAt: Date;

  @UpdateDateColumn({ type: 'timestamptz' })
  updatedAt: Date;
}
