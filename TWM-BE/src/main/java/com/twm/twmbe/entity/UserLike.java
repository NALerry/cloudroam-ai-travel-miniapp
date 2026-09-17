package com.twm.twmbe.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Entity
@Table(name = "user_like")
@Data
public class UserLike {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "post_id", nullable = false)
    private Long postId;

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();

    // 关联的帖子信息（非数据库字段，用于查询）
    @Transient
    private Post post;

    // 关联的用户信息（非数据库字段，用于查询）
    @Transient
    private User user;

    public UserLike() {}

    public UserLike(Long userId, Long postId) {
        this.userId = userId;
        this.postId = postId;
    }
}