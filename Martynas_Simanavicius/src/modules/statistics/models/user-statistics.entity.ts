import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn, Generated, Index, OneToOne, JoinColumn, ManyToOne } from 'typeorm';
import { User } from '../../auth/models/user.entity';

@Entity('user_statistics')
export class UserStatistics {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'uuid' })
  @Generated('uuid')
  @Index()
  uuid: string;

  @Column({ type: 'integer' })
  @Index()
  user_id: number;

  @OneToOne(() => User, (user) => user.userStatistics)
  @JoinColumn({ name: 'user_id' })
  user: User;

  @Column('numeric', { precision: 5, scale: 2 })
  average_score: number;

  @Column('numeric', { precision: 4, scale: 2 })
  lessons_per_day: number;

  @Column({ type: 'integer' })
  largest_streak: number;

  @CreateDateColumn({ type: 'timestamptz' })
  createdAt: Date;

  @UpdateDateColumn({ type: 'timestamptz' })
  updatedAt: Date;
}
