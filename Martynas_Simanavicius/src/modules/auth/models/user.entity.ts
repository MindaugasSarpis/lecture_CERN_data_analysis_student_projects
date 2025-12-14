import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn, Generated, Index, OneToOne, OneToMany, JoinColumn } from 'typeorm';
import { UserStatistics } from '../../statistics/models/user-statistics.entity';
import { UserVideo } from '../../videos/models/user-video.entity';
import { UserLearningTreeNodeStats } from '../../statistics/models/user-learning-tree-node-stats.entity';

@Entity('users')
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'uuid' })
  @Generated('uuid')
  @Index()
  uuid: string;

  @Column({ unique: true, length: 254 })
  @Index()
  email: string;

  @Column({ unique: true, length: 50 })
  username: string;

  @Column({ length: 255 })
  password: string;

  @OneToOne(() => UserStatistics, (userStatistics) => userStatistics.user)
  userStatistics: UserStatistics;

  @OneToMany(() => UserVideo, (userVideo) => userVideo.user)
  userVideos: UserVideo[];

  @OneToMany(() => UserLearningTreeNodeStats, (stats) => stats.user)
  learningTreeNodeStats: UserLearningTreeNodeStats[];

  @CreateDateColumn({ type: 'timestamptz' })
  createdAt: Date;

  @UpdateDateColumn({ type: 'timestamptz' })
  updatedAt: Date;
}
